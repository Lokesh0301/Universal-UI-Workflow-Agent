from call_llm import call_gpt4_1
import os
import json
from playwright_executor import StepExecutor
import asyncio

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set in the environment variables.")
        return

    # Prompt to generate the JSON structure for playwright_executor
    prompt = """
    Return only the JSON array of steps (no explanation, no markdown, no extra text) for Playwright to automate the following scenario:
    1. Go to https://www.notion.so
    2. Click the 'New page' button
    3. Wait for the title field to appear
    4. Enter the title 'My AI Generated Page'
    5. Take a screenshot after entering the title
    6. Enter 'This is the body content.' in the body
    7. Take a final screenshot.
    Each step should be a dictionary with keys: action, selector (if needed), value (if needed), and description.
    
    The available actions you can use are:
    - goto (navigate to a URL)
    - click (click a CSS selector)
    - wait_for (wait for a selector to appear)
    - type (fill a selector with a value)
    - screenshot (take a screenshot)
    - set_title (set the page title using the selector '[data-testid="page-title"]')
    - hover (hover over a selector)
    - press (press a keyboard key on a selector)
    Only use these actions. Do not include any other text or explanation in the response.
    """

    response = call_gpt4_1(prompt, api_key)
    print("GPT-4.1 response:")
    print(response)

    # Try to parse and pretty-print the JSON if possible
    try:
        steps = json.loads(response)
        print("\nParsed steps:")
        print(json.dumps(steps, indent=2))
        # Execute the steps using StepExecutor
        executor = StepExecutor(steps)
        asyncio.run(executor.run())
    except Exception:
        print("\nResponse could not be parsed as JSON.")

if __name__ == "__main__":
    main()
