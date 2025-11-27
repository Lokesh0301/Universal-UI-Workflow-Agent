#Plan - B
prompt_B = """
You are an agent responsible for repairing a single failed Playwright step.
Return ONLY a single JSON object representing the corrected step.
NO explanations. NO markdown. NO surrounding text. Only valid JSON.

Context Provided:
1. task_description:
    {TASK_DESCRIPTION}

2. previous_steps:
    {PREVIOUS_STEPS}

3. failed_step:
    {FAILED_STEP}

4. error_message:
    {ERROR_MESSAGE}

5. semantic_dom:
    {SEMANTIC_DOM}   

6. accessibility_tree:
    {ACCESSIBILITY_TREE}

Your responsibilities:
- Diagnose why the failed step did not work.
- Repair ONLY the failed step.
- Use the semantic_dom and accessibility_tree to locate a more reliable selector.
- Use only the allowed actions:
  ["goto", "click", "wait_for", "type", "press", "hover", "screenshot",
    "set_title", "keyboard_type", "keyboard_press", "scroll_to", "scroll_by",
    "select_option", "upload_file", "frame_click", "frame_type",
    "wait", "wait_for_navigation"]
- Use the most stable selector available:
      * data-testid
      * role=...
      * aria-label
      * name=...
      * type=...
      * visible text
      * or multi-selector OR expressions
- If the element does not exist, replace the step with the next best action
  required to progress toward the task goal.

Output Format:
Return ONLY this JSON object and nothing else:

{
  "action": "...",
  "selector": "...",   // omit if not needed
  "value": "...",      // omit if not needed
  "description": "..."
}

Do not return an array. Do not return previous steps. Return only the fixed step.
"""


from agents.call_llm import call_o3_mini

def repair_step(task_description, previous_steps, failed_step, error_message, semantic_dom, accessibility_tree, api_key):
     """
     Repairs a failed step using o3-mini and returns the repaired step.
     """
     prompt = prompt_B.replace("{TASK_DESCRIPTION}", task_description)
     prompt = prompt.replace("{PREVIOUS_STEPS}", previous_steps)
     prompt = prompt.replace("{FAILED_STEP}", failed_step)
     prompt = prompt.replace("{ERROR_MESSAGE}", error_message)
     prompt = prompt.replace("{SEMANTIC_DOM}", semantic_dom)
     prompt = prompt.replace("{ACCESSIBILITY_TREE}", accessibility_tree)
     response = call_o3_mini(prompt, api_key)
     return response
