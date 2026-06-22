# A2A OxyGent Server

**Source:** `examples/a2a/demo_a2a_oxygent_server.py`

## Overview

This example launches an OxyGent MAS (Multi-Agent System) with built-in A2A (Agent-to-Agent) server endpoints. It sets up a minimal `ChatAgent` backed by an HTTP LLM and exposes the MAS as an A2A-compatible server on port 8090. Other A2A clients -- whether OxyGent-native or Google A2A SDK-based -- can then send messages to this server.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- Dependencies installed via `pip install -r requirements.txt`

## How to Run

```bash
PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py
```

The server starts on `http://127.0.0.1:8090` with A2A endpoints under `/a2a`.

## Code Walkthrough

### Configuration

Two constants control the server binding:

- `PORT = 8090` -- the HTTP port for the FastAPI web service.
- `A2A_BASE_PATH = "/a2a"` -- the URL prefix for all A2A protocol endpoints (e.g., `/a2a/.well-known/agent.json`, `/a2a/` for message send).

`Config.set_server_port(PORT)` overrides the default port (8080) before the MAS starts.

### Components (`oxy_space`)

The `oxy_space` list defines two Oxy components:

1. **`HttpLLM`** (`name="default_llm"`) -- An HTTP-based LLM client configured from environment variables. This provides the language model backend for the agent.

2. **`ChatAgent`** (`name="master_agent"`) -- A conversational agent that uses `default_llm`. It is marked `is_master=True`, making it the default entry point for incoming messages routed through the MAS.

### Entry Point

The `main()` coroutine:

1. Sets the server port via `Config.set_server_port(PORT)`.
2. Creates a `MAS` instance with `enable_a2a_server=True` and `a2a_base_path=A2A_BASE_PATH`, which instructs the MAS to mount A2A protocol routes on the FastAPI application.
3. Calls `mas.start_web_service(first_query="A2A MAS server is running.")` to launch the web server. The `first_query` parameter triggers an initial self-test message.

The script uses `asyncio.run(main())` as the top-level entry point.

## Key Concepts

- **A2A Protocol**: Agent-to-Agent is a protocol for inter-agent communication. OxyGent implements it natively, allowing any A2A-compliant client to interact with the MAS.
- **`enable_a2a_server`**: A MAS constructor flag that adds A2A endpoints (agent card, message send, streaming, task management) to the web service.
- **`a2a_base_path`**: Controls the URL prefix for A2A endpoints, enabling co-location with the standard OxyGent web UI and chat APIs.
- **Master Agent**: The agent with `is_master=True` receives all top-level messages routed through `MAS.chat_with_agent()`.

## Expected Behavior

When started, the server:

1. Prints startup logs and serves the OxyGent web UI at `http://127.0.0.1:8090`.
2. Exposes the A2A agent card at `http://127.0.0.1:8090/a2a/.well-known/agent.json`.
3. Accepts A2A `message/send` and `message/stream` requests at `http://127.0.0.1:8090/a2a/`.
4. Routes incoming A2A messages to `master_agent`, which generates responses using the configured LLM.
5. Remains running until manually terminated (Ctrl+C).
