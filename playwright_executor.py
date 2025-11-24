import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


class StepExecutor:
    """
    Fully general-purpose executor for LLM-generated browser actions.
    Supports Playwright actions across ANY web application.
    Includes:
      - Safe clicking
      - Auto scrolling
      - Typing, keyboard, mouse, file upload
      - Dropdown selection
      - Iframe interaction
      - Automatic screenshot after ANY UI-changing action
      - Automatic DOM + accessibility snapshots for LLM
      - Full generalization across apps
    """

    def __init__(self, steps, output_dir="agent_outputs", capture_dom=True, capture_accessibility=True):
        self.steps = steps
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        self.screenshots_dir = self.output_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True, parents=True)

        self.dom_dir = self.output_dir / "dom_states"
        self.dom_dir.mkdir(exist_ok=True, parents=True)

        self.capture_dom = capture_dom
        self.capture_accessibility = capture_accessibility

    # -------------------------------------------------------
    # SEMANTIC DOM EXTRACTION (required for LLM step planning)
    # -------------------------------------------------------
    async def _extract_semantic_dom(self, page):
        """
        Extracts a compact representation of all actionable elements.
        This is what the LLM uses to plan next-step actions.
        """
        return await page.evaluate(
            """() => {
                const nodes = document.querySelectorAll(
                    'button, a, input, textarea, select, [role], [contenteditable]'
                );

                const describe = (el) => {
                    const tag = el.tagName.toLowerCase();
                    const text = (el.innerText || '').trim().slice(0, 200);
                    const aria = el.getAttribute('aria-label');
                    const role = el.getAttribute('role') || null;
                    const placeholder = el.getAttribute('placeholder');
                    const type = el.getAttribute('type');
                    const href = el.getAttribute('href');

                    // Build the most stable selector possible
                    let selector = null;
                    const id = el.id;
                    const dataTest = el.getAttribute('data-testid');
                    const name = el.getAttribute('name');

                    if (id) selector = `${tag}#${id}`;
                    else if (dataTest) selector = `${tag}[data-testid="${dataTest}"]`;
                    else if (name) selector = `${tag}[name="${name}"]`;
                    else if (aria) selector = `${tag}[aria-label="${aria}"]`;
                    else {
                        const classes = [...el.classList].slice(0, 2).join('.');
                        selector = classes ? `${tag}.${classes}` : tag;
                    }

                    return { tag, role, text, aria, placeholder, type, href, selector };
                };

                return [...nodes].map(describe);
            }"""
        )

    # -------------------------------------------------------
    # ACCESSIBILITY SNAPSHOT (optional supplement)
    # -------------------------------------------------------
    async def _extract_accessibility_tree(self, page):
        try:
            return await page.accessibility.snapshot()
        except:
            return None

    async def _save_state(self, page, idx, description):
        """Screenshot + DOM + Accessibility Tree"""
        screenshot_path = self.screenshots_dir / f"{idx+1}_{description}.png"
        await page.screenshot(path=screenshot_path)

        # Save semantic DOM
        if self.capture_dom:
            dom_data = await self._extract_semantic_dom(page)
            with open(self.dom_dir / f"{idx+1}_{description}_dom.json", "w", encoding="utf-8") as f:
                json.dump(dom_data, f, indent=2)

        # Save accessibility tree
        if self.capture_accessibility:
            acc = await self._extract_accessibility_tree(page)
            with open(self.dom_dir / f"{idx+1}_{description}_accessibility.json", "w", encoding="utf-8") as f:
                json.dump(acc, f, indent=2)

    # -------------------------------------------------------
    # LOW-LEVEL SAFE OPERATIONS
    # -------------------------------------------------------
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

    # -------------------------------------------------------
    # MAIN EXECUTION LOOP
    # -------------------------------------------------------
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
                    # -------- NAVIGATION --------
                    if action == "goto":
                        await page.goto(value, wait_until="domcontentloaded")

                    elif action == "wait_for_navigation":
                        await page.wait_for_load_state("networkidle")

                    # -------- CLICKING --------
                    elif action == "click":
                        await self._safe_click(page, selector)

                    elif action == "dblclick":
                        await page.dblclick(selector)

                    elif action == "right_click":
                        await page.click(selector, button="right")

                    # -------- TYPING --------
                    elif action == "type":
                        await self._safe_fill(page, selector, value)

                    elif action == "keyboard_type":
                        await page.keyboard.type(value)

                    elif action == "keyboard_press":
                        await page.keyboard.press(value)

                    elif action == "press":
                        await page.press(selector, value)

                    # -------- HOVER --------
                    elif action == "hover":
                        await page.hover(selector)

                    # -------- WAITING --------
                    elif action == "wait_for":
                        await page.wait_for_selector(selector)

                    elif action == "wait":
                        await page.wait_for_timeout(value)

                    # -------- SCROLLING --------
                    elif action == "scroll_to":
                        await page.evaluate(
                            f"document.querySelector('{selector}')?.scrollIntoView()"
                        )

                    elif action == "scroll_by":
                        await page.mouse.wheel(value.get("x", 0), value.get("y", 400))

                    # -------- SELECTING/DROPDOWN --------
                    elif action == "select_option":
                        await page.select_option(selector, value)

                    # -------- FILE UPLOAD --------
                    elif action == "upload_file":
                        await page.set_input_files(selector, value)

                    # -------- SPECIAL TITLE HANDLER --------
                    elif action == "set_title":
                        el = page.locator(selector).first
                        await el.click()
                        await page.keyboard.press("Control+A")
                        await page.keyboard.press("Backspace")
                        await page.keyboard.type(value, delay=40)

                    # -------- IFRAME HANDLING --------
                    elif action == "frame_click":
                        frame = page.frame(name=step["frame_name"])
                        await frame.click(selector)

                    elif action == "frame_type":
                        frame = page.frame(name=step["frame_name"])
                        await frame.fill(selector, value)

                    # -------- RAW SCREENSHOT --------
                    elif action == "screenshot":
                        await self._save_state(page, idx, desc)
                        continue

                    else:
                        print(f"⚠ Unknown action: {action}")

                    # -----------------------------------------
                    # After ANY meaningful UI-changing action
                    # -----------------------------------------
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
