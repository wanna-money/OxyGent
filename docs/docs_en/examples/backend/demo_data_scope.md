# Understanding Data Scopes: shared_data, group_data, and global_data

**Source:** `examples/backend/demo_data_scope.py`

## Overview

This example demonstrates the three data scoping levels in OxyGent -- `shared_data`, `group_data`, and `global_data` -- and how they propagate through a multi-agent system. It shows how each scope persists across conversation turns and how sub-agents inherit data from their parent. This pattern is essential for understanding data flow in complex multi-agent architectures.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Node.js with `uvx` available (for the MCP time server tool)

## How to Run

```bash
python -m examples.backend.demo_data_scope
```

## Code Walkthrough

### Hook Functions

```python
def process_input(oxy_request: OxyRequest) -> OxyRequest:
    print("--- agent name --- :", oxy_request.callee)
    print("--- arguments --- :", oxy_request.get_arguments())
    print("--- shared_data --- :", oxy_request.get_shared_data())
    print("--- group_data --- :", oxy_request.get_group_data())
    print("--- global_data --- :", oxy_request.get_global_data())
    return oxy_request
```

This diagnostic hook is attached to both agents, printing all three data scopes each time an agent is invoked. This lets you observe how data propagates through the agent hierarchy.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | Standard LLM credentials |
| `time_tools` | `StdioMCPClient` | MCP time server (`mcp-server-time`) for timezone queries |
| `master_agent` | `ReActAgent` | `is_master=True`, `sub_agents=["time_agent"]`, has `process_input` hook |
| `time_agent` | `ReActAgent` | `tools=["time_tools"]`, has `process_input` hook, described as a time query tool |

### Entry Point

The example makes three sequential calls to demonstrate data scope behavior:

**Round 1-1 -- Baseline call (no extra data):**
```python
oxy_response = await mas.chat_with_agent({"query": "What time is it"})
```
Only `global_data` (set at MAS initialization) is available.

**Round 2-1 -- Call with shared_data and group_data:**
```python
oxy_response = await mas.chat_with_agent({
    "query": "What time is it",
    "shared_data": {"shared_key": "shared_value"},
    "group_data": {"group_key": "group_value"},
})
```
Both `shared_data` and `group_data` are injected into the request.

**Round 2-2 -- Continuation of Round 2-1 via from_trace_id:**
```python
trace_id = oxy_response.oxy_request.current_trace_id
oxy_response = await mas.chat_with_agent({
    "query": "What time is it",
    "from_trace_id": trace_id,
})
```
Uses `from_trace_id` to continue the previous conversation, inheriting its `shared_data` and `group_data`.

### MAS Initialization

```python
global_data = {"global_key": "global_value"}
async with MAS(oxy_space=oxy_space, global_data=global_data) as mas:
```

The `global_data` dictionary is passed at MAS construction and is accessible by all agents across all requests.

## Key Concepts

- **shared_data**: Per-request scoped data. Set via the payload or programmatically. Persists within a single trace and can be carried forward using `from_trace_id`.
- **group_data**: Per-request scoped data similar to `shared_data` but designed for group-level context (e.g., user session data). Also persists across trace continuations.
- **global_data**: MAS-level scoped data. Set at MAS initialization. Shared across all requests and all agents for the lifetime of the MAS instance.
- **from_trace_id**: Allows continuing a previous conversation, inheriting its data scopes.
- **Data inheritance**: When a master agent delegates to a sub-agent, data scopes are propagated down the call chain.

## Expected Behavior

1. Round 1-1: The `process_input` hook prints empty `shared_data` and `group_data`, but shows `global_data` containing `{"global_key": "global_value"}`.
2. Round 2-1: The hook prints `shared_data` with `{"shared_key": "shared_value"}`, `group_data` with `{"group_key": "group_value"}`, and the same `global_data`.
3. Round 2-2: Despite not explicitly passing `shared_data` or `group_data`, these values are inherited from the previous trace via `from_trace_id`.
4. Sub-agent `time_agent` also receives the propagated data scopes when invoked by `master_agent`.
