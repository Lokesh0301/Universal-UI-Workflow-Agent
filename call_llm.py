from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def call_gpt4_1(prompt, api_key):
    """
    Calls the OpenAI GPT-4.1 Responses API with the given prompt.

    Args:
        prompt (str): The input prompt to send to the model.
        api_key (str): Your OpenAI API key.

    Returns:
        str: The response from the GPT-4.1 model.
    """
    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )

        # Extract the output text properly
        return response.output_text

    except Exception as e:
        return f"An error occurred: {e}"

# Example usage
if __name__ == "__main__":
    #user_prompt = "What is the capital of France?"
    user_prompt = """
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
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Error: OPENAI_API_KEY is not set in the environment variables.")
    else:
        print(call_gpt4_1(user_prompt, api_key))








'''
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(task_instruction, semantic_dom, accessibility_tree, previous_steps):
    """
    Calls GPT-4.1 to generate the NEXT executable Playwright step.
    
    Args:
        task_instruction (str): High-level task, e.g., "Create a new page in Notion".
        semantic_dom (list): Extracted DOM snapshot for current page state.
        accessibility_tree (dict): Playwright accessibility tree.
        previous_steps (list): Steps already executed in this session.

    Returns:
        dict: A single step dictionary for StepExecutor.
    """

    prompt = f"""
You are Agent B in a multi-agent system. Your job is to return EXACTLY ONE next step
that the Playwright StepExecutor can run.

### You MUST follow these rules:
- Output ONLY a JSON object (no array, no explanation).
- Use ONLY the allowed actions listed below.
- Refer ONLY to the provided DOM snapshot and accessibility tree.
- The step MUST be executable immediately by Playwright.
- If you cannot determine the correct next step, return a wait_for step on the
  closest matching actionable selector.

### HIGH-LEVEL TASK:
{task_instruction}

### CURRENT SEMANTIC DOM SNAPSHOT:
{semantic_dom}

### ACCESSIBILITY TREE:
{accessibility_tree}

### STEPS ALREADY EXECUTED:
{previous_steps}

### ALLOWED ACTIONS:
- goto               → navigate to a URL
- click              → click a CSS selector
- dblclick           → double-click a selector
- right_click        → right-click a selector
- type               → fill an input field
- keyboard_type      → type using keyboard
- keyboard_press     → press keyboard key
- press              → press key on a selector
- hover              → hover over selector
- wait_for           → wait for element to appear
- wait               → sleep milliseconds
- scroll_to          → scroll to a selector
- scroll_by          → scroll by pixels
- select_option      → select dropdown value
- upload_file        → file upload
- set_title          → Notion-style title setting
- frame_click        → click inside iframe
- frame_type         → type inside iframe
- screenshot         → capture screenshot (always safe)

### FORMAT:
Return ONLY a single JSON object:
{{
    "action": "...",
    "selector": "...",
    "value": "...",
    "description": "..."
}}

### GENERAL REASONING RULES:
- If the user's goal requires clicking something, find the best matching element in the DOM.
- If the text/aria-label matches the intended element, select that.
- If no selector clearly matches, return a safe wait_for step.
- Always choose the MOST stable selector (id > data-testid > aria-label > name > class fallback).
- Never generate multiple steps. Only ONE.

Return ONLY ONE JSON step.
"""

    try:
        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )
        return response.output_text

    except Exception as e:
        print("LLM error:", e)
        return None

'''