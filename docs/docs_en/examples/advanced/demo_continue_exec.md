# Continue Execution (Restart from Node)

**Source:** `examples/advanced/demo_continue_exec.py`

## Overview

This example demonstrates the "continue execution" or "restart from node" feature, which allows you to re-run an agent's workflow from a specific intermediate node. After an initial query completes, you can provide a `restart_node_id` (and optionally a `restart_node_output`) to replay execution from that point. This is useful for debugging, testing alternative tool outputs, or recovering from failures mid-execution.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Node.js runtime (for `uvx` to run the MCP time server)

## How to Run

```bash
python -m examples.advanced.demo_continue_exec
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from environment |
| `time_tools` | `StdioMCPClient` | `command="uvx"`, `args=["mcp-server-time", "--local-timezone=Asia/Shanghai"]` |
| `time_agent` | `ReActAgent` | `desc="A tool for time query."`, `tools=["time_tools"]`, `llm_model="default_llm"` |

### Entry Point

`main()` demonstrates a two-phase execution pattern:

**Phase 1 -- Initial Execution:**
```python
payload = {"query": "Get what time it is Asia/Shanghai"}
oxy_response = await mas.chat_with_agent(payload=payload)
```
Runs the time agent normally and prints the result.

**Phase 2 -- Restart from Node (commented out):**
```python
payload = {
    "restart_node_id": "BcgSFR4Ls3nHCkFm",   # node_id from the first execution
    "restart_node_output": '{"timezone": "Asia/Shanghai", ...}',  # optional override
}
oxy_response = await mas.chat_with_agent(payload=payload)
```
To use this phase, uncomment the code and supply a valid `restart_node_id` from the first run's trace. The `restart_node_output` field is optional: if provided, it replaces the original output of that node, allowing you to test how the agent reacts to different intermediate results.

## Key Concepts

- **restart_node_id** -- The identifier of an intermediate execution node to restart from. Retrieved from the trace data of a previous run.
- **restart_node_output** -- An optional override for the node's output. If omitted, the original query is auto-retrieved from the database and the node re-executes normally.
- **Trace Replay** -- The framework stores execution traces (nodes, tool calls, LLM responses) and can replay from any point, making it possible to iterate on agent behavior without re-running the entire chain.
- **chat_with_agent()** -- The core MAS entry point for running queries. Accepts both standard queries and restart payloads.

## Expected Behavior

1. Phase 1 executes: the time agent queries the current time in Asia/Shanghai and prints the result.
2. Phase 2 (when uncommented): execution resumes from the specified node, optionally using the overridden output, and the agent produces a new final answer based on that node's data.
