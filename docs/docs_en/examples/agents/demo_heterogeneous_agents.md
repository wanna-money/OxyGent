# Heterogeneous Multi-Agent System

**Source:** `examples/agents/demo_heterogeneous_agents.py`

## Overview

This example demonstrates a multi-agent system composed of different agent types working together: a `ReActAgent` as the master orchestrator, a `ChatAgent` for general knowledge, and a `WorkflowAgent` for structured time queries. It also showcases integration with an MCP (Model Context Protocol) tool server and the use of `Config.set_agent_llm_model()` as a global default. This pattern is ideal when different sub-tasks require different agent strategies.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`
- `uvx` installed (for running the MCP time server via `mcp-server-time`)

## How to Run

```bash
python -m examples.agents.demo_heterogeneous_agents
```

## Code Walkthrough

### Configuration

```python
Config.set_agent_llm_model("default_llm")
```

Sets a global default LLM model name for all agents. Agents that do not explicitly specify `llm_model` will use `"default_llm"`. In this example, the `QA_agent` and the `time_agent` rely on this default.

### Hook Functions

#### `workflow(oxy_request: OxyRequest)`

An async workflow function registered as `func_workflow` on the `WorkflowAgent`. It defines a deterministic execution sequence:

1. Calls the `get_current_time` tool (provided by the MCP time server) with `arguments={"timezone": "Asia/Shanghai"}`.
2. Returns the tool's output directly.

This shows how a `WorkflowAgent` can execute a fixed sequence of steps without LLM reasoning.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars |
| `time_tools` | `StdioMCPClient` | `params.command="uvx"`, `params.args=["mcp-server-time", "--local-timezone=Asia/Shanghai"]` |
| `master_agent` | `ReActAgent` | `llm_model="default_llm"`; `sub_agents=["QA_agent", "time_agent"]` |
| `QA_agent` | `ChatAgent` | `desc="A tool for knowledge."` ; `llm_model="default_llm"` |
| `time_agent` | `WorkflowAgent` | `desc="A tool for time query."`; `tools=["time_tools"]`; `func_workflow=workflow` |

### Entry Point

```python
await mas.start_web_service(
    first_query="What time it is?",
)
```

Launches the web service with a time-related initial query.

## Key Concepts

- **Heterogeneous agents** -- combining different agent types (`ReActAgent`, `ChatAgent`, `WorkflowAgent`) under one master agent, each specializing in a different capability.
- **`sub_agents`** -- the master `ReActAgent` treats sub-agents as callable tools. It reasons about which sub-agent to invoke based on the user query.
- **`StdioMCPClient`** -- connects to an external MCP tool server via stdio. The `mcp-server-time` package provides time-related tools.
- **`WorkflowAgent`** -- executes a predefined programmatic workflow (no LLM-driven reasoning), useful for deterministic multi-step tasks.
- **`desc`** -- the description field on sub-agents helps the master agent decide which sub-agent to route a query to.
- **`Config.set_agent_llm_model()`** -- sets the global default LLM, reducing repetition when many agents share the same model.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The initial query "What time it is?" is sent.
3. The master `ReActAgent` reasons that this is a time query and delegates to `time_agent`.
4. The `time_agent` (a `WorkflowAgent`) executes its workflow: calling the `get_current_time` MCP tool with timezone `Asia/Shanghai`.
5. The current time is returned through the agent chain and displayed in the web UI.
6. For knowledge-related queries, the master would instead delegate to `QA_agent`.
