# Live Prompt Modes: Static vs Dynamic Prompts

**Source:** `examples/live_prompts/demo.py`

## Overview

This example demonstrates the three prompt modes available for OxyGent agents: system default prompts, code-defined static prompts, and live (dynamic) prompts that can be hot-reloaded at runtime. It builds a multi-agent system with a master agent coordinating time, file, and math sub-agents, each configured with a different prompt strategy.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`
- Elasticsearch backend (or local fallback) for live prompt storage when `use_live_prompt=True`

## How to Run

```bash
python -m examples.live_prompts.demo
```

## Code Walkthrough

### Configuration

```python
Config.set_agent_llm_model("default_llm")
```

Sets the global default LLM model name so that agents without an explicit `llm_model` parameter will use `"default_llm"`.

### Components (`oxy_space`)

| Component | Type | Prompt Mode | Key Parameters |
|-----------|------|-------------|----------------|
| `default_llm` | `HttpLLM` | N/A | `api_key`, `base_url`, `model_name` from env vars |
| `time_tools` | Preset Tools | N/A | Built-in time query tools from `oxygent.preset_tools` |
| `time_agent` | `ReActAgent` | Static (`use_live_prompt=False`) | `prompt="You are a time management assistant..."`, `tools=["time_tools"]` |
| `file_tools` | Preset Tools | N/A | Built-in file operation tools from `oxygent.preset_tools` |
| `file_agent` | `ReActAgent` | Static (`use_live_prompt=False`) | `prompt="You are a file system assistant..."`, `tools=["file_tools"]` |
| `math_tools` | Preset Tools | N/A | Built-in math tools from `oxygent.preset_tools` |
| `math_agent` | `ReActAgent` | Dynamic (default) | `prompt="You are a math assistant..."`, `tools=["math_tools"]` |
| `master_agent` | `ReActAgent` | Dynamic (default) | `is_master=True`, `sub_agents=["time_agent", "file_agent", "math_agent"]` |

### Prompt Mode Details

1. **`time_agent`** -- `use_live_prompt=False` with a `prompt` value set. Since live prompt is disabled, the agent uses the code-defined `prompt` string. If `prompt` were empty, it would fall back to the system default prompt.

2. **`file_agent`** -- `use_live_prompt=False` with a `prompt` value set. Same behavior: the code-level `prompt` is used directly, and no runtime updates from the prompt store are applied.

3. **`math_agent`** -- `use_live_prompt` is not set (defaults to `True`). The code-level `prompt` serves as the initial value, but can be overridden at runtime via the live prompt management system backed by Elasticsearch.

4. **`master_agent`** -- Also uses live prompts by default. Its prompt can be hot-reloaded without restarting the service.

### Entry Point

```python
await mas.start_web_service(
    first_query="What time is it now? Please save it into time.txt."
)
```

Launches the web service and automatically sends an initial query that requires cooperation between the time agent (to get the current time) and the file agent (to save it to a file).

## Key Concepts

- **Live Prompt (`use_live_prompt`)** -- When `True` (the default), the agent's prompt is managed by the live prompt system (`oxygent/live_prompt/`). Prompts can be updated at runtime via the ES-backed prompt store without restarting the application.
- **Static Prompt** -- When `use_live_prompt=False`, the agent uses the `prompt` parameter defined in code. This is deterministic and does not change at runtime.
- **System Default Prompt** -- When `use_live_prompt=False` and `prompt` is empty, the agent falls back to the framework's built-in default prompt.
- **Preset Tools** -- OxyGent provides built-in tool collections (`time_tools`, `file_tools`, `math_tools`) in `oxygent/preset_tools/` that wrap common operations.
- **Master Agent Routing** -- The master agent (`is_master=True`) receives user queries and delegates to the appropriate sub-agent based on the task.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The first query "What time is it now? Please save it into time.txt." is sent automatically.
3. The master agent routes the time-related part to `time_agent`, which queries the current time using preset time tools.
4. The master agent then routes the file-saving task to `file_agent`, which writes the time into `time.txt` using preset file tools.
5. `math_agent` and `master_agent` have live prompts enabled -- their prompts can be updated at runtime through the live prompt management system.
6. `time_agent` and `file_agent` have live prompts disabled -- their prompts remain fixed as defined in code.
