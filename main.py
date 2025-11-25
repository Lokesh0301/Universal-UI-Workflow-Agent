from call_llm import call_gpt4_1, call_o3_mini
import os
import json
from playwright_executor import StepExecutor
import asyncio
from agent import prompt_A, prompt_B, prompt_C

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set in the environment variables.")
        return

    # Ask user which app to automate
    app_choice = input("Which app do you want to automate? (notion/linear): ").strip().lower()
    if app_choice == "linear":
        storage_state_file = "linear_state.json"
    else:
        storage_state_file = "notion_state.json"

    # Getting user input for task description
    user_input = input("Enter NLP query from agent A:")

    # ---------------------------------------------
    # Plan - A
    # ---------------------------------------------
    prompt_A_with_task = prompt_A.format(TASK_DESCRIPTION=user_input)
    print("Calling o3-mini with prompt A...")

    response_A = call_o3_mini(prompt_A_with_task, api_key)
    print("Response from o3-mini:")

    try:
        steps = json.loads(response_A)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from o3-mini response: {e}")
        return

    executor = StepExecutor(steps=steps)
    previous_steps = []

    async def run_steps():
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(storage_state=storage_state_file)
            page = await context.new_page()

            for idx, step in enumerate(steps):
                print(f"Executing step: {step}")
                success, error_message, semantic_dom, accessibility_tree = await executor.execute_step(page, idx, step)
                if success:
                    print("Step executed successfully.")
                    previous_steps.append(step)
                else:
                    print(f"Step failed with error: {error_message}")
                    prompt_B_filled = prompt_B
                    prompt_B_filled = prompt_B_filled.replace("{TASK_DESCRIPTION}", user_input)
                    prompt_B_filled = prompt_B_filled.replace("{PREVIOUS_STEPS}", json.dumps(previous_steps, indent=2))
                    prompt_B_filled = prompt_B_filled.replace("{FAILED_STEP}", json.dumps(step, indent=2))
                    prompt_B_filled = prompt_B_filled.replace("{ERROR_MESSAGE}", error_message)
                    prompt_B_filled = prompt_B_filled.replace("{SEMANTIC_DOM}", json.dumps(semantic_dom, indent=2))
                    prompt_B_filled = prompt_B_filled.replace("{ACCESSIBILITY_TREE}", json.dumps(accessibility_tree, indent=2))
                    print("Calling o3-mini with prompt B to repair the step...")
                    response_B = call_o3_mini(prompt_B_filled, api_key)
                    print("Response from o3-mini:")
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

    asyncio.run(run_steps())
        
if __name__ == "__main__":
    main()
