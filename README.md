# Universal UI Workflow Agent

Universal UI Workflow Agent is a modular Python automation tool that uses LLMs (OpenAI o3-mini, GPT-4.1, or GPT-5.1) to generate and repair Playwright automation steps for any web application, based on natural language task descriptions.

## Features
- **LLM-Powered Planning:** Converts user task descriptions into executable Playwright steps using OpenAI models.
- **Step Repair:** Automatically repairs failed steps using DOM and accessibility context.
- **Modular Agents:** Planner and repair logic are separated for maintainability.
- **Output Management:** Screenshots, DOM states, and accessibility trees are saved for each run.
- **Environment Config:** Uses `.env` for API keys and configuration.
- **Extensible:** Easily switch between LLM models (o3-mini, GPT-4.1, GPT-5.1).

## Directory Structure
```
Universal-UI-Workflow-Agent/
├── agents/
│   ├── planner_agent.py
│   ├── repair_agent.py
│   ├── call_llm.py
│   └── __init__.py
├── playwright_executor.py
├── main.py
├── .env
├── .gitignore
├── README.md
└── agent_outputs/
    └── [timestamped_run_folders]
```

## Setup
1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   pip install python-dotenv
   ```
2. **Configure API Key:**
   - Create a `.env` file:
     ```env
     OPENAI_API_KEY=your_openai_api_key_here
     ```
3. **Run the agent:**
   ```sh
   python main.py
   ```

## Usage
- Enter the app to automate (e.g., Notion, Linear).
- Enter a natural language task description.
- The agent will generate a plan, execute steps, and repair failures automatically.
- Outputs (screenshots, DOM, accessibility trees) are saved in `agent_outputs/[timestamp]`.

## How It Works
- **Planning:** `planner_agent.py` uses LLMs to generate Playwright steps.
- **Execution:** `playwright_executor.py` runs each step and saves outputs.
- **Repair:** `repair_agent.py` uses LLMs to fix failed steps using UI context.

## Extending
- To use a different LLM, update the agent functions in `agents/`.
- Add new automation logic or output formats as needed.


