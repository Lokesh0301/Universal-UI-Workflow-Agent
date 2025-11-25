import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


class StepExecutor:
    """
    Fully general-purpose executor for LLM-generated browser actions.
    Supports Playwright actions across ANY web application.
    Includes:
      - Safe clicking with fallback strategies
      - Auto scrolling when an element is outside viewport
      - Typing, keyboard input, file upload
      - Dropdown selection
      - iFrame interaction
      - Automatic screenshot after ALL UI-changing actions
      - DOM + accessibility snapshots for next-step LLM reasoning
      - Full generalization across apps via semantic DOM extraction
    """

    def __init__(self, steps, output_dir="agent_outputs",
                 capture_dom=True, capture_accessibility=True):

        self.steps = steps

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        self.screenshots_dir = self.output_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True, parents=True)

        self.dom_dir = self.output_dir / "dom_states"
        self.dom_dir.mkdir(exist_ok=True, parents=True)

        self.capture_dom = capture_dom
        self.capture_accessibility = capture_accessibility

    # ---------------------------------------------
    # SEMANTIC DOM TREE FOR AGENTIC NEXT-STEP PLANNING
    # ---------------------------------------------
    async def _extract_semantic_dom(self, page):
        return await page.evaluate(
            """() => {
                const nodes = document.querySelectorAll(
                    'button, a, input, textarea, select, [role], [contenteditable]'
                );

                const describe = (el) => {
                    const tag = el.tagName.toLowerCase();
                    const text = (el.innerText || '').trim().slice(0, 200);
                    const aria = el.getAttribute('aria-label');
                    const role = el.getAttribute('role');
                    const placeholder = el.getAttribute('placeholder');
                    const href = el.getAttribute('href');
                    const type = el.getAttribute('type');
                    const id = el.id;
                    const dt = el.getAttribute('data-testid');
                    const name = el.getAttribute('name');

                    let selector = null;

                    if (dt) selector = `${tag}[data-testid="${dt}"]`;
                    else if (id) selector = `${tag}#${id}`;
                    else if (name) selector = `${tag}[name="${name}"]`;
                    else if (aria) selector = `${tag}[aria-label="${aria}"]`;
                    else {
                        const cl = [...el.classList].slice(0, 2).join('.');
                        selector = cl ? `${tag}.${cl}` : tag;
                    }

                    return {
                        tag, text, aria, role, placeholder, href, type,
                        selector
                    };
                };

                return [...nodes].map(describe);
            }"""
        )

    # ---------------------------------------------
    # ACCESSIBILITY TREE EXTRACTION
    # ---------------------------------------------
    async def _extract_accessibility_tree(self, page):
        try:
            return await page.accessibility.snapshot()
        except:
            return None

    # ---------------------------------------------
    # SAVE STATE (Screenshot + DOM + AX Tree)
    # ---------------------------------------------
    async def _save_state(self, page, idx, description):
        screenshot_path = self.screenshots_dir / f"{idx+1}_{description}.png"
        await page.screenshot(path=screenshot_path)

        if self.capture_dom:
            dom_data = await self._extract_semantic_dom(page)
            with open(self.dom_dir / f"{idx+1}_{description}_dom.json", "w") as f:
                json.dump(dom_data, f, indent=2)

        if self.capture_accessibility:
            acc = await self._extract_accessibility_tree(page)
            with open(self.dom_dir / f"{idx+1}_{description}_accessibility.json", "w") as f:
                json.dump(acc, f, indent=2)

    # ---------------------------------------------
    # SAFE HELPERS
    # ---------------------------------------------
    async def _safe_click(self, page, selector):
        try:
            el = page.locator(selector).first
            await el.scroll_into_view_if_needed()
            await el.click(timeout=5000)
        except:
            await page.locator(selector).first.click(force=True)

    async def _safe_fill(self, page, selector, value):
        try:
            await page.fill(selector, value)
        except:
            await page.click(selector)
            await page.fill(selector, value)

    # ---------------------------------------------
    # EXECUTE A SINGLE STEP (for agentic loops)
    # ---------------------------------------------
    async def execute_step(self, page, idx, step):
        """
        Executes a single step and returns:
        (success, error_message, semantic_dom, accessibility_tree)
        """

        action = step.get("action")
        selector = step.get("selector")
        value = step.get("value")
        desc = step.get("description", f"step_{idx+1}")

        print(f"\n▶ SINGLE STEP {idx+1}: {json.dumps(step, indent=2)}")

        try:
            # ---------------- Navigation ----------------
            if action == "goto":
                await page.goto(value, wait_until="domcontentloaded")

            elif action == "wait_for_navigation":
                await page.wait_for_load_state("networkidle")

            # ---------------- Clicking ----------------
            elif action == "click":
                await self._safe_click(page, selector)

            elif action == "dblclick":
                await page.dblclick(selector)

            elif action == "right_click":
                await page.click(selector, button="right")

            # ---------------- Typing ----------------
            elif action == "type":
                await self._safe_fill(page, selector, value)

            elif action == "keyboard_type":
                await page.keyboard.type(value)

            elif action == "keyboard_press":
                await page.keyboard.press(value)

            elif action == "press":
                await page.press(selector, value)

            # ---------------- Hover ----------------
            elif action == "hover":
                await page.hover(selector)

            # ---------------- Waiting ----------------
            elif action == "wait_for":
                await page.wait_for_selector(selector)

            elif action == "wait":
                await page.wait_for_timeout(value)

            # ---------------- Scrolling ----------------
            elif action == "scroll_to":
                await page.locator(selector).scroll_into_view_if_needed()

            elif action == "scroll_by":
                await page.mouse.wheel(value.get("x", 0), value.get("y", 400))

            # ---------------- Dropdowns ----------------
            elif action == "select_option":
                await page.select_option(selector, value)

            # ---------------- File Upload ----------------
            elif action == "upload_file":
                await page.set_input_files(selector, value)

            # ---------------- Title Handler ----------------
            elif action == "set_title":
                el = page.locator(selector).first
                await el.click()
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")
                await page.keyboard.type(value, delay=40)

            # ---------------- iFrames ----------------
            elif action == "frame_click":
                frame = page.frame(name=step["frame_name"])
                await frame.click(selector)

            elif action == "frame_type":
                frame = page.frame(name=step["frame_name"])
                await frame.fill(selector, value)

            # ---------------- Screenshot ----------------
            elif action == "screenshot":
                await self._save_state(page, idx, desc)

            else:
                raise Exception(f"Unknown action: {action}")

            # -----------------------------------
            # After ANY UI-changing action → save
            # -----------------------------------
            if action not in ["wait", "wait_for", "screenshot"]:
                await self._save_state(page, idx, desc)

            # Success → return state details
            semantic_dom = await self._extract_semantic_dom(page)
            accessibility_tree = await self._extract_accessibility_tree(page)
            return True, None, semantic_dom, accessibility_tree

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error in single step {idx+1}: {error_msg}")

            semantic_dom = await self._extract_semantic_dom(page)
            accessibility_tree = await self._extract_accessibility_tree(page)

            return False, error_msg, semantic_dom, accessibility_tree


    # ---------------------------------------------
    # MAIN EXECUTION LOOP
    # ---------------------------------------------
    async def run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(storage_state="notion_state.json")
            page = await context.new_page()

            for idx, step in enumerate(self.steps):
                action = step.get("action")
                selector = step.get("selector")
                value = step.get("value")
                desc = step.get("description", f"step_{idx+1}")

                print(f"\n▶ STEP {idx+1}: {json.dumps(step, indent=2)}")

                try:
                    # ---------------- Navigation ----------------
                    if action == "goto":
                        await page.goto(value, wait_until="domcontentloaded")

                    elif action == "wait_for_navigation":
                        await page.wait_for_load_state("networkidle")

                    # ---------------- Clicking ----------------
                    elif action == "click":
                        await self._safe_click(page, selector)

                    elif action == "dblclick":
                        await page.dblclick(selector)

                    elif action == "right_click":
                        await page.click(selector, button="right")

                    # ---------------- Typing ----------------
                    elif action == "type":
                        await self._safe_fill(page, selector, value)

                    elif action == "keyboard_type":
                        await page.keyboard.type(value)

                    elif action == "keyboard_press":
                        await page.keyboard.press(value)

                    elif action == "press":
                        await page.press(selector, value)

                    # ---------------- Hover ----------------
                    elif action == "hover":
                        await page.hover(selector)

                    # ---------------- Waiting ----------------
                    elif action == "wait_for":
                        await page.wait_for_selector(selector)

                    elif action == "wait":
                        await page.wait_for_timeout(value)

                    # ---------------- Scrolling ----------------
                    elif action == "scroll_to":
                        await page.locator(selector).scroll_into_view_if_needed()

                    elif action == "scroll_by":
                        await page.mouse.wheel(value.get("x", 0), value.get("y", 400))

                    # ---------------- Dropdowns ----------------
                    elif action == "select_option":
                        await page.select_option(selector, value)

                    # ---------------- File Upload ----------------
                    elif action == "upload_file":
                        await page.set_input_files(selector, value)

                    # ---------------- Title Handler ----------------
                    elif action == "set_title":
                        el = page.locator(selector).first
                        await el.click()
                        await page.keyboard.press("Control+A")
                        await page.keyboard.press("Backspace")
                        await page.keyboard.type(value, delay=40)

                    # ---------------- iFrames ----------------
                    elif action == "frame_click":
                        frame = page.frame(name=step["frame_name"])
                        await frame.click(selector)

                    elif action == "frame_type":
                        frame = page.frame(name=step["frame_name"])
                        await frame.fill(selector, value)

                    # ---------------- Raw screenshot ----------------
                    elif action == "screenshot":
                        await self._save_state(page, idx, desc)
                        continue

                    else:
                        print("⚠ Unknown action:", action)

                    # ---------------- Auto-save state ----------------
                    if action not in ["wait", "wait_for"]:
                        await self._save_state(page, idx, desc)

                except Exception as e:
                    print(f"❌ Error executing step {idx+1}: {e}")

            await browser.close()


# -------------------------
# Standalone Test Execution
# -------------------------
if __name__ == "__main__":

    # Sample steps to test the executor
    sample_steps = [
        {
            "action": "goto",
            "value": "https://www.notion.so",
            "description": "open_homepage"
        },
        {
            "action": "wait_for",
            "selector": "div[aria-label='New page'], div[role='button']:has-text('New page')",
            "description": "wait_for_new_page_button"
        },
        {
            "action": "click",
            "selector": "div[aria-label='New page'], div[role='button']:has-text('New page')",
            "description": "click_new_page"
        },
        {
            "action": "wait_for",
            "selector": "div[contenteditable='true']",
            "description": "wait_for_editor"
        },
        {
            "action": "set_title",
            "selector": "[data-testid='page-title'], div[contenteditable='true']",
            "value": "Agent B Generated Page",
            "description": "set_title"
        },
        {
            "action": "keyboard_type",
            "value": "This page was created automatically by Agent B using Playwright.",
            "description": "type_body"
        },

        # ----------------------------------------
        # Final screenshot after completing all UI
        # ----------------------------------------
        {
            "action": "screenshot",
            "description": "post_completion_state"
        }
    ]

    executor = StepExecutor(
        steps=sample_steps,
        output_dir="agent_test_output",
        capture_dom=True,
        capture_accessibility=True
    )

    # Explicitly create the screenshots folder
    executor.screenshots_dir = executor.output_dir / "screenshots"
    executor.screenshots_dir.mkdir(exist_ok=True, parents=True)

    asyncio.run(executor.run())
