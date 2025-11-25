prompt_A = """
Return ONLY a JSON array of steps. Do NOT include explanations, markdown, or extra text.

Your role:
You are an agent that generates Playwright automation steps for ANY web application, even apps you have never seen before. Use only observable UI elements, semantic cues, element text, roles, or stable attributes.

Each step must be a dictionary with keys:
- action
- selector (if needed)
- value (if needed)
- description

The ONLY actions allowed are:
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
1. Always prefer stable selectors:
   - [data-testid="..."]
   - role selectors
   - aria-label
   - name
   - type
   - visible text
2. If multiple selectors are possible, provide a multi-selector OR expression:
   "button:has-text('New page'), div[aria-label='New page']"
3. Every UI-changing action must be followed by a screenshot step.
4. The flow must be executable by Playwright with no human intervention.
5. Do not hallucinate hidden elements. Base actions ONLY on typical UI patterns.
6. Output must be strictly valid JSON.

Now generate the JSON array of steps for the following task description:
{TASK_DESCRIPTION}
"""

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

prompt_C = """
You are an agent responsible for regenerating an entire Playwright workflow
when multiple steps have failed or when the original plan is no longer viable.

Return ONLY a JSON array of steps (no explanations, no markdown, no surrounding text).
Each step must be a dictionary with keys:
- action
- selector (if needed)
- value (if needed)
- description

Context Provided:
1. task_description:
   {TASK_DESCRIPTION}   

2. previous_successful_steps:
   {PREVIOUS_SUCCESSFUL_STEPS}

3. failed_steps:
   {FAILED_STEPS}

4. error_messages:
   {ERROR_MESSAGES}

5. semantic_dom:
   {SEMANTIC_DOM}

6. accessibility_tree:
   {ACCESSIBILITY_TREE}

Your responsibilities:
- Rebuild the entire step sequence needed to solve the task.
- Incorporate all new discoveries from semantic_dom and accessibility_tree.
- Avoid reusing broken or unstable selectors.
- Follow the constraints of the allowed actions:
  ["goto", "click", "wait_for", "type", "press", "hover", "screenshot",
   "set_title", "keyboard_type", "keyboard_press", "scroll_to", "scroll_by",
   "select_option", "upload_file", "frame_click", "frame_type",
   "wait", "wait_for_navigation"]
- Prefer stable selectors:
     * [data-testid="..."]
     * aria-label
     * role
     * name
     * type
     * visible text matches
     * OR expressions combining multiple selectors
- Ensure every UI-changing action is followed by a screenshot step.
- The generated workflow must be fully executable by Playwright.

Output Format:
Return ONLY a JSON array of steps. Example shape:

[
  {
    "action": "...",
    "selector": "...",
    "value": "...",
    "description": "..."
  },
  ...
]

Do NOT include explanations.
Do NOT repeat the context.
Do NOT wrap the JSON in markdown.
"""
