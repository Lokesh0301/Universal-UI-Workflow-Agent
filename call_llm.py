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
