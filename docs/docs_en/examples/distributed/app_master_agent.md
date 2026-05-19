# Distributed Master Agent (Gateway)

**Source:** `examples/distributed/app_master_agent.py`

## Overview

This file defines the **master agent** in a three-service distributed multi-agent system. It acts as the gateway that end users interact with: it runs a web UI on the default port (8080), hosts a local file agent, and delegates math-related queries to a remote math agent running on port 8081 via SSE (Server-Sent Events). Together with `app_math_agent.py` and `app_time_agent.py`, it demonstrates how OxyGent distributes agents across independent processes that communicate over HTTP/SSE.

## Prerequisites

- Environment variables (in `.env` or exported):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider.
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM endpoint.
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier (e.g. `gpt-4`).
- **Node.js** must be installed (`npx` is used to launch the MCP filesystem server).
- **The math agent service** (`app_math_agent.py`) must already be running on `http://127.0.0.1:8081` before starting this service. The math agent in turn depends on the time agent on port 8082. See [Startup Order](#startup-order) below.

### Startup Order

Because this master agent connects to the math agent via SSE, and the math agent connects to the time agent, you must start the services bottom-up:

1. **Port 8082** -- Start the time agent first: `python -m examples.distributed.app_time_agent`
2. **Port 8081** -- Start the math agent second: `python -m examples.distributed.app_math_agent`
3. **Port 8080** -- Start the master agent last: `python -m examples.distributed.app_master_agent`

## How to Run

```bash
# Terminal 1
python -m examples.distributed.app_time_agent

# Terminal 2
python -m examples.distributed.app_math_agent

# Terminal 3
python -m examples.distributed.app_master_agent
```

Open the web UI at `http://127.0.0.1:8080` after all three services are running.

## Code Walkthrough

### Configuration

No explicit `Config.set_server_port()` or `Config.set_app_name()` call is made, so this service uses the framework defaults -- port **8080** and the default app name.

### Components (`oxy_space`)

The `oxy_space` list registers four components:

| Component | Type | Purpose |
|---|---|---|
| `default_llm` | `HttpLLM` | LLM backend shared by all local agents. `temperature` is set to 0.01 for near-deterministic output. `semaphore=4` limits concurrent LLM calls. |
| `file_tools` | `StdioMCPClient` | Launches the `@modelcontextprotocol/server-filesystem` MCP server via `npx`, scoped to the `./local_file` directory. Provides file-system read/write tools. |
| `master_agent` | `ReActAgent` | The top-level agent (`is_master=True`). Routes user queries to either `file_agent` or `math_agent` based on intent. |
| `file_agent` | `ReActAgent` | A sub-agent that handles local file queries using `file_tools`. |
| `math_agent` | `SSEOxyGent` | A **remote** agent proxy. It forwards requests over SSE to `http://127.0.0.1:8081` where the actual math agent runs. `is_share_call_stack=False` keeps call stacks isolated between services. |

### Entry Point

The `main()` coroutine creates a `MAS` instance with the `oxy_space`, then starts the web service with an initial query of *"The first 30 positions of pi"*. This pre-populated query is displayed in the web UI when it first loads, triggering an immediate demonstration of the distributed workflow.

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="The first 30 positions of pi")
```

## Key Concepts

- **SSEOxyGent** -- The bridge between distributed services. It wraps a remote MAS endpoint as if it were a local agent, using SSE for streaming communication. This is the core mechanism that enables multi-process agent deployment.
- **is_share_call_stack=False** -- Prevents the master agent's call-stack context from being forwarded to the remote math agent, keeping each service's reasoning history independent.
- **ReActAgent** -- An agent that follows the Reason-Act cycle: it reasons about the user query, selects a tool or sub-agent, observes the result, and repeats until it can produce a final answer.
- **MCP (Model Context Protocol)** -- The `StdioMCPClient` launches an external MCP server as a child process and communicates via stdio, exposing the server's tools to the agent.

## Expected Behavior

1. The web UI opens at `http://127.0.0.1:8080` with the pre-filled query *"The first 30 positions of pi"*.
2. The `master_agent` recognizes this as a math task and delegates it to `math_agent`.
3. The `math_agent` proxy forwards the request via SSE to port 8081, where the actual math agent computes pi to 30 decimal places (after optionally querying the time agent on port 8082).
4. The result flows back through the SSE connection to the master agent, which presents it in the web UI.
5. Users can also ask file-related questions (e.g., "list files in local_file"), which the master agent will route to `file_agent` instead.
