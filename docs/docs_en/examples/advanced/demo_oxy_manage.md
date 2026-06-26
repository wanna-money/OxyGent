# Runtime Oxy Management

**Source:** `examples/advanced/demo_oxy_manage.py`

## Overview

This example demonstrates how to use `oxy_manage_tools` to dynamically create, move, and delete agents and tools in a running MAS at runtime. A dedicated "doctor_agent" is equipped with `oxy_manage_tools` and acts as a system administrator -- it can inspect the current organization tree, create new agents, attach tools to them, move Oxy nodes between parents, and remove agents that are no longer needed, all without restarting the system.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`

## How to Run

```bash
python -m examples.advanced.demo_oxy_manage
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from environment |
| `math_tools` | `FunctionHub` | Preset mathematical calculation tools |
| `time_tools` | `FunctionHub` | Preset time query tools |
| `time_agent` | `ReActAgent` | `desc="A tool that can query the time"`, `tools=["time_tools"]` |
| `file_tools` | `FunctionHub` | Preset file system operation tools |
| `file_agent` | `ReActAgent` | `desc="A tool that can operate the file system"`, `tools=["file_tools"]` |
| `oxy_manage_tools` | `FunctionHub` | Preset tools for runtime CRUD on the agent/tool organization |
| `doctor_agent` | `ReActAgent` | `desc="A system administrator..."`, `tools=["oxy_manage_tools"]` |
| `master_agent` | `ReActAgent` | `is_master=True`, `sub_agents=["time_agent", "file_agent", "doctor_agent"]` |

### Entry Point

`main()` creates a `MAS` context and launches the web service with a `first_query` list containing four sequential commands. The `first_query` parameter accepts a `list[str]`, and each string is executed in order as an initial conversation turn when the web UI loads.

## Key Concepts

- **oxy_manage_tools** -- A preset FunctionHub that provides tools for inspecting and modifying the agent/tool organization tree at runtime. It enables creating new Oxy instances, deleting existing ones, moving Oxy nodes between parent agents, and querying the current organization structure -- all while the MAS is running.
- **Runtime CRUD on Agent Organization** -- Traditional multi-agent setups define the organization statically in code. With `oxy_manage_tools`, the organization becomes dynamic: agents and tools can be added, removed, or reorganized on the fly via natural language instructions to the doctor_agent.
- **first_query with list[str]** -- The `start_web_service()` method accepts `first_query` as either a single string or a list of strings. When a list is provided, each entry is executed sequentially as an initial query, enabling scripted multi-step demonstrations that run automatically when the web UI opens.

## Expected Behavior

1. **Create math_agent** -- The doctor_agent creates a new ReActAgent named `math_agent` with the description "A tool that can perform mathematical calculations", assigns `math_tools` to it, and attaches it as a sub-agent of `master_agent`. After this step, the organization gains a new math-capable agent.
2. **Test math_agent** -- The master_agent delegates the query "What is 2 raised to the power of 9?" to the newly created `math_agent`, which uses `math_tools` to compute and return `512`.
3. **Reorganize time tools** -- The doctor_agent moves the `get_current_time` Oxy from under `time_agent` to directly under `master_agent`, then deletes `time_agent` from the organization. This demonstrates runtime reorganization -- tools can be reassigned and redundant agents removed.
4. **Test reorganized time tool** -- The master_agent answers "what time it is now" using the `get_current_time` tool that now lives directly under it, confirming the reorganization was successful.
