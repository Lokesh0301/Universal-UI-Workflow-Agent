# Plan - A
prompt_A = """
Return ONLY a JSON array of steps. Do NOT include explanations, markdown, or extra text.

Your role:
You are an agent that generates Playwright automation steps for ANY web application, even apps you have never seen before.
You MUST ALWAYS open the relevant application first before performing any actions.

Rules for determining which app to open:
- If the task description mentions Notion, open https://www.notion.so
- If it mentions Linear, open https://linear.app
- If it mentions Asana, open https://app.asana.com
- If it mentions Trello, open https://trello.com
- If it mentions Jira, open https://jira.com OR the closest known Jira domain
- If no app name is obvious, infer the most likely site from the task wording and still start with a goto step.

Your first step MUST always be:
{{ "action": "goto", "value": "<detected_app_url>", "description": "open_application" }}

Each subsequent step must be a dictionary with keys:
- action
- selector (if needed)
- value (if needed)
- description

Allowed actions:
- goto
- click
- wait_for
- type
- press
- hover
- screenshot
- set_title
- keyboard_type
- keyboard_press
- scroll_to
- scroll_by
- select_option
- upload_file
- frame_click
- frame_type
- wait
- wait_for_navigation

Guidelines:
1. ALWAYS start with the correct app-opening step using the goto action. Never skip this.
2. Prefer stable selectors:
   - [data-testid="..."]
   - aria-label
   - role
   - name
   - type
   - visible text
3. If multiple selectors could work, use OR selectors:
   "button:has-text('New page'), div[aria-label='New page']"
4. Every UI-changing action must be followed by a screenshot step.
5. When creating or submitting something via a form or modal (project, task, page, issue, etc.):
   - Click/focus the primary name/title field and set its value.
   - Then CLICK the primary button that completes the action
     (e.g. "Create project", "Create", "New page", "Save") before moving on.
   - After the submit action, capture a screenshot of the success state.
6. The flow MUST be executable by Playwright with no human intervention.
7. Do NOT hallucinate elements. Use only selectors that are typical for the app.
8. Output must be strictly valid JSON.


Now generate the JSON array of steps for the following task:
{TASK_DESCRIPTION}
"""


# --- LLM Call Function ---
from agents.call_llm import call_o3_mini

# --- Plan Generation Function ---
def generate_plan(task_description, api_key):
    """
    Generates a plan using o3-mini for the given task description.
    """
    prompt = prompt_A.format(TASK_DESCRIPTION=task_description)
    response = call_o3_mini(prompt, api_key)
    return response
