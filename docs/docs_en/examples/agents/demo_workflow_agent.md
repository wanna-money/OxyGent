# Workflow Agent with Multi-Component Orchestration

**Source:** `examples/agents/demo_workflow_agent.py`

## Overview

This example demonstrates the `WorkflowAgent` in its full power: a programmatic workflow function that calls sub-agents, LLMs, and tools directly via `oxy_request.call()`. It shows how to access conversation memory, send custom messages, invoke an LLM for auxiliary reasoning, and call MCP tools -- all within a single deterministic workflow. This pattern is ideal for complex, multi-step tasks that require precise control over the execution order.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`
- `uv` installed (for running the custom math MCP server)
- The `mcp_servers/` directory with `math_tools.py` must exist in the project root

## How to Run

```bash
python -m examples.agents.demo_workflow_agent
```

## Code Walkthrough

### Hook Functions

#### `workflow(oxy_request: OxyRequest)`

The core async workflow function registered via `func_workflow`. It demonstrates the full range of `OxyRequest` capabilities:

1. **Accessing memory:**
   - `oxy_request.get_short_memory()` -- retrieves the current agent's short-term conversation memory.
   - `oxy_request.get_short_memory(master_level=True)` -- retrieves the master-level memory (the top-level agent's conversation history).

2. **Accessing queries:**
   - `oxy_request.get_query()` -- gets the current query directed at this agent.
   - `oxy_request.get_query(master_level=True)` -- gets the original user query at the master level.

3. **Sending custom messages:**
   - `await oxy_request.send_message({"type": "msg_type", "content": "msg_content"})` -- sends a custom SSE message to the frontend.

4. **Calling a sub-agent:**
   - Calls `chat_agent` with the current query and captures its direct answer.

5. **Calling an LLM directly:**
   - Calls `default_llm` with a custom message list and `llm_params={"temperature": 0.2}` to determine how many decimal places of Pi the user wants.

6. **Calling an MCP tool:**
   - Calls `calc_pi` (provided by the math MCP server) with the extracted precision to compute Pi.

7. **Returning the final result:** a formatted string combining the precision and the computed Pi value.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars |
| `math_tools` | `StdioMCPClient` | `params.command="uv"`, `params.args=["--directory", "./mcp_servers", "run", "math_tools.py"]` |
| `chat_agent` | `ChatAgent` | `llm_model="default_llm"` (minimal config) |
| `math_agent` | `WorkflowAgent` | `is_master=True`; `sub_agents=["chat_agent"]`; `tools=["math_tools"]`; `func_workflow=workflow`; `llm_model="default_llm"` |

### Entry Point

```python
await mas.start_web_service(
    first_query="Please calculate the 20 positions of Pi",
)
```

Launches the web service with a Pi calculation query.

## Key Concepts

- **`oxy_request.call()`** -- the universal invocation method within a workflow. By specifying `callee` and `arguments`, you can call any registered Oxy component: agents, LLMs, or tools.
- **`get_short_memory()` / `get_query()`** -- methods on `OxyRequest` to access conversation context. The `master_level=True` flag accesses the root-level context.
- **`send_message()`** -- sends custom SSE events to the connected frontend, useful for progress updates or intermediate results.
- **Direct LLM calls** -- within a workflow, you can call an LLM directly with custom messages and parameters, bypassing the agent abstraction for fine-grained control.
- **`StdioMCPClient` with custom server** -- the `math_tools.py` MCP server is launched via `uv run` from the `mcp_servers/` directory.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The query "Please calculate the 20 positions of Pi" is sent.
3. The workflow executes sequentially:
   - Prints the current and master-level short memory and query to the terminal.
   - Sends a custom message `{"type": "msg_type", "content": "msg_content"}` to the frontend.
   - Calls `chat_agent` for a direct answer (printed to terminal).
   - Calls `default_llm` to extract the number "20" from the query (printed to terminal).
   - Calls the `calc_pi` MCP tool with `prec=20`.
4. The final response "Save 20 positions: [Pi value]" is displayed in the web UI.
