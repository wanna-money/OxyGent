# Flow Chart Generation Agent with Mermaid

**Source:** `examples/other/create_flow_image_demo.py`

## Overview

This example builds an interactive flowchart assistant that generates and displays Mermaid-based flowcharts in the browser. It uses a master `ReActAgent` to coordinate two sub-agents: one for generating flowchart HTML files from text descriptions, and another for opening existing flowchart files. The application also sets up a custom FastAPI server with static file serving and a dedicated API router for flowchart operations.

<img src="https://storage.jd.com/opponent/AI/5.png" width="80%"/>
<img src="https://storage.jd.com/opponent/AI/6.png" width="80%"/>

## Prerequisites

- Environment variables: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL_NAME` (note: this example uses OpenAI-style variable names, not the default `DEFAULT_LLM_*` names)
- Python packages listed in `requirements.txt`
- The `oxygent.chart` module (provides `flow_image_gen_tools`, `open_chart_tools`, `create_static_files`, and `flowchart_api`)
- A web browser for viewing generated flowcharts

## How to Run

```bash
cd examples/other
python create_flow_image_demo.py
```

Or from the project root:

```bash
PYTHONPATH=. python examples/other/create_flow_image_demo.py
```

Note: The script manually adds the project root to `sys.path` and loads `.env` via `python-dotenv`, so it can be run directly from its directory.

## Code Walkthrough

### Configuration

```python
Config.set_agent_llm_model("default_llm")
```

Sets the global default LLM model. The script also optionally disables automatic browser opening with `Config.set_server_auto_open_webpage(False)` (commented out by default).

### Master Agent Prompt

The `MASTER_AGENT_PROMPT` is a detailed Chinese-language system prompt that instructs the master agent to:

1. **Analyze user intent** -- Identify whether the user wants to generate, open, or edit a flowchart.
2. **Route to the correct agent/tool** based on keyword matching:
   - Generation keywords (generate, create, draw, design) route to `image_gen_agent`.
   - Open/view keywords route to `open_chart_agent`.
   - Edit/export questions are answered directly with usage guidance.
3. **Extract parameters** from user input (e.g., flowchart description, file paths).
4. **Provide feedback** using predefined response templates.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL_NAME` from env vars |
| `flow_image_gen_tools` | FunctionHub | Imported from `oxygent.chart.flow_image_gen_tools`; generates Mermaid flowcharts |
| `open_chart_tools` | FunctionHub | Imported from `oxygent.chart.open_chart_tools`; opens HTML files in browser |
| `image_gen_agent` | `ReActAgent` | `tools=["flow_image_gen_tools"]`, desc: flowchart generation agent |
| `open_chart_agent` | `ReActAgent` | `tools=["open_chart_tools"]`, desc: open flowchart in browser |
| `master_agent` | `ReActAgent` | `is_master=True`, `sub_agents=["image_gen_agent", "open_chart_agent"]`, `prompt_template=MASTER_AGENT_PROMPT`, also has direct tool access to both tool sets |

### FastAPI Application Setup

The script creates a custom FastAPI application alongside the OxyGent MAS:

1. **CORS middleware** -- Allows all origins for development convenience.
2. **Flowchart API router** -- Mounted at `/api` from `oxygent.chart.flowchart_api`.
3. **Root redirect** -- `GET /` redirects to `/static/index.html`.
4. **Static files** -- The web UI is served from `oxygent/chart/web/` at the `/static` path.

### Entry Point

```python
async def main():
    os.makedirs("../../oxygent/chart/web", exist_ok=True)
    os.makedirs("../../oxygent/chart/web/css", exist_ok=True)
    os.makedirs("../../oxygent/chart/web/js", exist_ok=True)
    create_static_files("../../oxygent/chart")
    app.mount("/static", StaticFiles(directory="../../oxygent/chart/web"), name="web")

    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Please generate a software development flowchart including requirements analysis, design, coding, testing, and deployment stages",
            port=8081,
        )
```

1. Creates the web directory structure if it does not exist.
2. Generates static files (HTML, CSS, JS) for the Mermaid editor UI.
3. Mounts static files on the FastAPI app.
4. Starts the MAS web service on port **8081** (not the default 8080) with an initial flowchart generation request.

## Usage Guide

1. **Default query**: On startup the program automatically sends an initial flowchart generation request (a software development flowchart).
2. **Custom queries**: Type a flowchart description in the web UI input box, e.g. "Generate a project management flowchart", "Create a user registration flowchart", "Draw an order processing flowchart".
3. **View results**: The flowchart opens automatically in the browser; the HTML file is saved in the project directory.
4. **Edit and preview**: Edit the Mermaid code directly on the flowchart page, click "Update Preview" to see changes in real time, and choose from preset templates.
5. **Export**: Click "Export SVG" or "Export PNG" to download the flowchart in the corresponding format.

## Key Concepts

- **Mermaid.js** -- A JavaScript-based diagramming library that renders diagrams from text definitions. The generated flowcharts are Mermaid syntax embedded in HTML files.
- **`prompt_template`** -- A full system prompt template that replaces the default agent prompt entirely (as opposed to `additional_prompt` which appends to it).
- **Direct Tool Access on Master** -- The master agent has `tools=["flow_image_gen_tools", "open_chart_tools"]` in addition to its sub-agents, allowing it to call tools directly without delegating to sub-agents.
- **Custom FastAPI Integration** -- This example shows how to extend the OxyGent web service with custom API routes and static file serving, running alongside the MAS service on a different port.
- **Static File Generation** -- `create_static_files()` programmatically generates the web editor UI files (HTML/CSS/JS) at startup.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8081`.
2. The static Mermaid editor UI is available at `http://127.0.0.1:8081/static/index.html`.
3. The first query asks the agent to generate a software development flowchart.
4. The master agent routes the request to `image_gen_agent`, which calls `generate_flow_chart` to produce a Mermaid flowchart HTML file.
5. The generated flowchart opens automatically in the browser, showing stages: requirements analysis, design, coding, testing, and deployment.
6. Users can continue interacting -- asking to generate new flowcharts, open existing ones, or get guidance on editing/exporting.

## Troubleshooting

1. **API connection failure**: Check the API settings in your `.env` file and verify network connectivity and API service status. The system will automatically fall back to a sample flowchart.
2. **Port in use**: If the default port 8081 is occupied, change the `port` parameter, or run `pkill -f create_flow_image_demo.py` to clean up the process.
3. **File path issues**: Ensure you have sufficient filesystem permissions and that the output directory exists.
4. **Missing static files**: The system creates the necessary static files automatically. If problems occur, verify that the `create_static_files` function executed successfully.

Enable debug mode for detailed logs:

```bash
export LOG_LEVEL=DEBUG
python examples/other/create_flow_image_demo.py
```
