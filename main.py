from agents import generate_plan, repair_step
import os
import json
from playwright_executor import StepExecutor
import asyncio
import datetime
import re
from dotenv import load_dotenv

load_dotenv()
def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set in the environment variables.")
        return

    # Ask user which app to automate
    app_choice = input("Which app do you want to automate? (notion/linear): ").strip().lower()
    if app_choice == "linear":
        storage_state_file = "saved_cookies/linear_state.json"
    else:
        storage_state_file = "saved_cookies/notion_state.json"

    # Getting user input for task description
    user_input = input("Enter NLP query from agent A:")

    # ---------------------------------------------
    # Plan - A
    # ---------------------------------------------

    print("Calling o3-mini with Plan A...")
    response_A = generate_plan(user_input, api_key)
    print("Got response from o3-mini")
    print(response_A)

    try:
        steps = json.loads(response_A)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from o3-mini response: {e}")
        return

    
    # Create a unique folder name for each run
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    # Use a sanitized version of the task description for folder name
    #task_name = re.sub(r'[^a-zA-Z0-9_-]', '_', user_input)[:40]
    run_folder = f"agent_outputs/{timestamp}"
    executor = StepExecutor(steps=steps, output_dir=run_folder)
    previous_steps = []

    async def run_steps():
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(storage_state=storage_state_file)
            page = await context.new_page()

            task_failed = False
            for idx, step in enumerate(steps):
                print(f"\n\n Executing step: {step}")
                success, error_message, semantic_dom, accessibility_tree = await executor.execute_step(page, idx, step)
                if success:
                    print("Step executed successfully.")
                    previous_steps.append(step)
                else:
                    # ---------------------------------------------
                    # Plan - B
                    # ---------------------------------------------
                    print(f"Step failed with error: {error_message}")
                    print("Calling o3-mini with Plan B...")
                    # # ---------------------------------------------
                    # # AUTO-SCROLL + AUTO-EXPAND BEFORE PLAN B
                    # # ---------------------------------------------
                    # try:
                    #     await page.mouse.wheel(0, 4000)
                    #     await page.wait_for_timeout(200)
                    #     await executor.auto_expand_ui(page)
                    # except:
                    #     pass

                    # Refresh DOM for repair prompt
                    semantic_dom = await executor._extract_semantic_dom(page)
                    accessibility_tree = await executor._extract_accessibility_tree(page)

                    # Use repair_step from agents
                    response_B = repair_step(
                        user_input,
                        json.dumps(previous_steps, indent=2),
                        json.dumps(step, indent=2),
                        error_message,
                        json.dumps(semantic_dom, indent=2),
                        json.dumps(accessibility_tree, indent=2),
                        api_key
                    )
                    print("Got response from o3-mini")
                    try:
                        repaired_step = json.loads(response_B)
                        print(f"Repaired step: {repaired_step}")
                        success, error_message, _, _ = await executor.execute_step(page, idx, repaired_step)
                        if success:
                            print("Repaired step executed successfully.")
                            previous_steps.append(repaired_step)
                        else:
                            print(f"Repaired step failed again with error: {error_message}")
                            print("Aborting further execution.")
                            break
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON from o3-mini response: {e}")
                        print("Aborting further execution.")
                        break
            await browser.close()
            if not task_failed:
                print(f"✅ Task completed and outputs stored in '{run_folder}'")
            await browser.close()

    asyncio.run(run_steps())

        
if __name__ == "__main__":
    main()
