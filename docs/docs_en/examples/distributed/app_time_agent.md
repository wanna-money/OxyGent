# Distributed Time Agent Service

**Source:** `examples/distributed/app_time_agent.py`

## Overview

This file defines the **time agent service**, the leaf node in the three-service distributed system. It runs on port 8082 and provides a simple `ReActAgent` that can answer time-related queries using the `mcp-server-time` MCP tool. It is called by the math agent on port 8081, but can also be used standalone through its own web UI.

## Prerequisites

- Environment variables (in `.env` or exported):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider.
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM endpoint.
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier.
- **uvx** must be installed (used to run the `mcp-server-time` package).
- No other services need to be running first -- this is the leaf service.

### Startup Order

This service has no downstream dependencies. In the full distributed demo, start it **first**:

1. **Port 8082** -- Start this time agent first.
2. **Port 8081** -- Then start `app_math_agent.py`.
3. **Port 8080** -- Then start `app_master_agent.py`.

## How to Run

```bash
python -m examples.distributed.app_time_agent
```

The service will be available at `http://127.0.0.1:8082`.

## Code Walkthrough

### Configuration

```python
Config.set_app_name("app-time")
Config.set_server_port(8082)
```

Sets the app name to `app-time` and binds to port **8082**.

### Components (`oxy_space`)

| Component | Type | Purpose |
|---|---|---|
| `default_name` | `HttpLLM` | Shared LLM backend with `temperature=0.01` and `semaphore=4`. |
| `time_tools` | `StdioMCPClient` | Launches the `mcp-server-time` MCP server via `uvx` with the timezone set to `Asia/Shanghai`. Provides time-related tools (get current time, convert timezones, etc.). |
| `time_agent` | `ReActAgent` | The master agent for this service. Uses `time_tools` to answer time queries through LLM-driven Reason-Act loops. |

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="What time is it now?")
```

Starts the web service on port 8082 with a demo query for standalone testing.

## Key Concepts

- **Leaf service pattern** -- This is the simplest possible distributed OxyGent service: a single agent with a single tool. It demonstrates that even the smallest unit of functionality can be deployed as an independent service and accessed by other agents via SSE.
- **StdioMCPClient with uvx** -- The `uvx` command runs a Python package directly without prior installation. Here it launches `mcp-server-time`, a community MCP server that provides time-related tools.
- **Timezone configuration** -- The `--local-timezone=Asia/Shanghai` argument configures the time server to report times in the China Standard Time zone.

## Expected Behavior

1. When accessed standalone, the web UI at `http://127.0.0.1:8082` opens with the query *"What time is it now?"*.
2. The `time_agent` uses the MCP time tools to determine the current time in the Asia/Shanghai timezone.
3. The response displays the current date and time.
4. When called remotely by the math agent (port 8081), the same flow occurs but the result is returned via SSE instead of being displayed in the local web UI.
