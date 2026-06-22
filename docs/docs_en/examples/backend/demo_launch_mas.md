# Launching MAS: All Execution Modes

**Source:** `examples/backend/demo_launch_mas.py`

## Overview

This example is a comprehensive reference demonstrating all the ways to create, initialize, and launch a MAS instance. It covers direct component invocation via `mas.call()`, agent-level interaction via `chat_with_agent()`, and all three runtime modes: CLI, batch processing, and web service. It also shows the alternative `MAS.create()` factory method. Use this as a quick-start guide to understand the full MAS API surface.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Node.js with `uvx` available (for the MCP time server tool)

## How to Run

```bash
python -m examples.backend.demo_launch_mas
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | Standard LLM credentials |
| `time_tools` | `StdioMCPClient` | MCP time server for timezone queries |
| `time_agent` | `ReActAgent` | `tools=["time_tools"]` -- a ReAct agent equipped with time tools |

### Alternative Initialization: MAS.create()

```python
async def get_mas_object():
    mas = await MAS.create(oxy_space=oxy_space)
    await mas.start_web_service()
```

`MAS.create()` is an async factory method that returns an initialized MAS instance without using the `async with` context manager. This is useful when you need more control over the MAS lifecycle or when integrating with frameworks that manage their own event loops.

### Entry Point

The main function demonstrates five usage patterns sequentially:

**1. Direct tool call:**
```python
await mas.call(
    callee="get_current_time",
    arguments={"timezone": "Asia/Shanghai"},
)
```
Invokes a specific tool (registered by the MCP client) by name.

**2. Direct LLM call:**
```python
await mas.call(
    callee="default_llm",
    arguments={
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "hello"},
        ],
        "llm_params": {"temperature": 0.2},
    },
)
```
Calls the LLM directly with custom messages and parameters.

**3. Direct agent call:**
```python
await mas.call(
    callee="time_agent",
    arguments={"query": "What time it is?"},
)
```
Invokes a specific agent by name with a query.

**4. Chat with master agent:**
```python
payload = {"query": "What time it is?"}
oxy_response = await mas.chat_with_agent(payload=payload)
```
Routes the query to the master agent (the first agent in `oxy_space` or one marked `is_master=True`).

**5. Runtime modes:**
```python
await mas.start_cli_mode(first_query="What time it is?")
await mas.start_batch_processing(["What time it is?"] * 10)
await mas.start_web_service(first_query="What time it is?")
```
- `start_cli_mode`: Interactive REPL in the terminal.
- `start_batch_processing`: Concurrent processing of multiple queries.
- `start_web_service`: FastAPI server with web UI.

## Key Concepts

- **mas.call()**: Low-level API to invoke any registered Oxy component (agent, tool, or LLM) by name.
- **mas.chat_with_agent()**: High-level API that routes a query to the master agent, handling trace management and response formatting.
- **MAS.create()**: Async factory method for MAS initialization outside of a context manager.
- **Three runtime modes**: CLI mode for development/debugging, batch mode for bulk processing, and web service mode for production deployment.
- **MCP tool registration**: Tools provided by `StdioMCPClient` are automatically registered by their tool names (e.g., `get_current_time`), making them callable via `mas.call()`.

## Expected Behavior

1. The MAS initializes with the LLM, MCP client, and agent.
2. The direct tool call returns the current time in the Shanghai timezone.
3. The direct LLM call returns a greeting response.
4. The direct agent call triggers the ReAct loop: the agent reasons about the query, calls the time tool, and returns the result.
5. `chat_with_agent` routes through the master agent and returns an `OxyResponse`.
6. Each runtime mode starts in sequence (in practice, you would choose one).
