# GRPO Resample (Trace Replay for Reinforcement Learning)

**Source:** `examples/advanced/demo_grpo_resample.py`

## Overview

This example demonstrates a trace-replay pattern useful for GRPO (Group Relative Policy Optimization) or similar reinforcement-learning workflows. It runs a multi-agent task, retrieves all intermediate LLM nodes from the execution trace, and then replays each LLM node in parallel. This allows collecting multiple samples of agent behavior from the same intermediate states for reward modeling or policy optimization.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`

## How to Run

```bash
python -m examples.advanced.demo_grpo_resample
```

## Code Walkthrough

### Configuration

```python
Config.set_agent_llm_model("default_llm")
Config.set_message_is_send_tool_call(False)
Config.set_message_is_send_observation(False)
Config.set_storage_es_engine("MemoryEs")
```

- `set_agent_llm_model("default_llm")` -- Sets the default LLM for all agents.
- `set_message_is_send_tool_call(False)` -- Disables sending tool call messages to the frontend (reduces noise during batch replay).
- `set_message_is_send_observation(False)` -- Disables sending observation messages to the frontend.
- `set_storage_es_engine("MemoryEs")` -- Uses an in-memory Elasticsearch substitute instead of a real ES cluster, keeping traces in memory for this demo.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from environment |
| `time_tools` | `preset_tools.time_tools` | Built-in preset time tools |
| `time_agent` | `ReActAgent` | `desc="A tool that can query the time"`, `tools=["time_tools"]` |
| `file_tools` | `preset_tools.file_tools` | Built-in preset file system tools |
| `file_agent` | `ReActAgent` | `desc="A tool that can operate the file system"`, `tools=["file_tools"]` |
| `math_tools` | `preset_tools.math_tools` | Built-in preset math tools |
| `math_agent` | `ReActAgent` | `desc="A tool that can perform mathematical calculations."`, `tools=["math_tools"]` |
| `master_agent` | `ReActAgent` | `is_master=True`, `sub_agents=["time_agent", "file_agent", "math_agent"]` |

### Entry Point

`main()` executes a three-step workflow:

**Step 1 -- Initial Execution:**
```python
payload = {"query": "What time is it now? Please save it into time.txt."}
oxy_response = await mas.chat_with_agent(payload)
trace_id = oxy_response.oxy_request.current_trace_id
await mas.await_background_tasks(trace_id)
```
Runs the full multi-agent task and waits for all background tasks to complete.

**Step 2 -- Extract LLM Nodes:**
```python
res = await get_task_info(trace_id)
filterd_nodes = [node for node in res["data"]["nodes"] if node["node_type"] == "llm"]
```
Uses `get_task_info()` (from `oxygent.routes`) to retrieve the full execution trace, then filters for only LLM-type nodes.

**Step 3 -- Parallel Replay:**
```python
tasks = []
for node in sorted(filterd_nodes, key=lambda x: x["create_time"]):
    payload = {"restart_node_id": node["node_id"]}
    tasks.append(mas.chat_with_agent(payload))
oxy_responses = await asyncio.gather(*tasks)
```
Replays all LLM nodes in parallel using `restart_node_id`. Each replay re-executes the agent from that specific point, producing potentially different outputs due to LLM sampling.

## Key Concepts

- **GRPO Resampling** -- By replaying LLM decision points from the same trace, you can collect multiple trajectory samples from identical states, which is a key step in Group Relative Policy Optimization.
- **MemoryEs** -- An in-memory Elasticsearch substitute that stores trace data without requiring a real ES cluster. Ideal for experiments and demos.
- **get_task_info()** -- A route utility that retrieves the full execution trace for a given `trace_id`, including all nodes, their types, callers, callees, and timestamps.
- **Parallel Replay** -- Using `asyncio.gather()` to replay multiple nodes concurrently, collecting diverse outputs from the same intermediate states.
- **await_background_tasks()** -- Waits for all background tasks associated with a trace to complete before proceeding, ensuring the trace data is fully populated.

## Expected Behavior

1. Step 1: The master agent queries the time, delegates to `time_agent`, gets the result, then delegates to `file_agent` to save it to `time.txt`.
2. Step 2: The execution trace is retrieved and filtered to extract all LLM decision nodes.
3. Step 3: Each LLM node is replayed in parallel. The outputs (potentially different due to LLM sampling) are printed to stdout, one per line.
