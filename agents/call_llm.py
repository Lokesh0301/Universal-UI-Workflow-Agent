if __name__ == "__main__":
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    prompt = "Say hello from GPT-5.1!"
    if not api_key:
        print("OPENAI_API_KEY not set in environment.")
    else:
        print("Calling GPT-5.1...")
        result = call_gpt5_1(prompt, api_key)
        print("Result:", result)

from openai import OpenAI

def call_gpt4_1(prompt, api_key):
    """
    Calls the OpenAI GPT-4.1 Responses API with the given prompt.
    Returns: str: The response from the GPT-4.1 model.
    """
    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )
        return response.output_text
    except Exception as e:
        return f"An error occurred: {e}"

def call_o3_mini(prompt, api_key):
    """
    Calls the OpenAI o3-mini Responses API with the given prompt.
    Returns: str: The response from the o3-mini model.
    """
    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(
            model="o3-mini",
            input=prompt
        )
        return response.output_text
    except Exception as e:
        return f"An error occurred: {e}"

def call_gpt5_1(prompt, api_key):
    """
    Calls the OpenAI GPT-5.1 Responses API with the given prompt.
    Returns: str: The response from the GPT-5.1 model.
    """
    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(
            model="gpt-5.1",
            input=prompt
        )
        return response.output_text
    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == "__main__":
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    prompt = "Say hello from GPT-5.1!"
    if not api_key:
        print("OPENAI_API_KEY not set in environment.")
    else:
        print("Calling GPT-5.1...")
        result = call_gpt5_1(prompt, api_key)
        print("Result:", result)