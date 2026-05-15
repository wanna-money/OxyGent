# LangChain Client Calling OxyGent A2A Server

**Source:** `examples/a2a/langchain_interop/demo_langchain_client_call_oxygent_server.py`

## Overview

This example demonstrates a LangChain-based client sending requests to an OxyGent A2A server. It uses LangChain `RunnableLambda` primitives for pre-processing and post-processing, while the actual A2A communication is handled via raw HTTP (httpx). This shows how a LangChain pipeline can interoperate with OxyGent through the A2A protocol.

## Prerequisites

- Python 3.10+
- Extra packages: `pip install langchain-core httpx`
- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME` (required by the OxyGent server)
- **The OxyGent A2A server must be running first:**
  ```bash
  PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py
  ```

## How to Run

```bash
PYTHONPATH=. python examples/a2a/langchain_interop/demo_langchain_client_call_oxygent_server.py
```

## Code Walkthrough

### Configuration

The client connects to `http://127.0.0.1:8090/a2a`, which is the default endpoint of the OxyGent A2A server.

### Components

**`extract_task_text(task)`** -- Utility that extracts the text answer from an A2A task response. It first checks `status.message.parts`, then falls back to `artifacts[0].parts`.

**`send_once(client, query, context_id, task_id)`** -- Constructs and sends an A2A `message/send` JSON-RPC request. Builds the proper A2A message envelope with role `user`, a text part, and optional `contextId`/`taskId` for multi-turn sessions. Returns both the raw task and extracted text.

**LangChain Runnables:**
- `pre` -- A `RunnableLambda` that prepends `[LangChain Client]` to the query before sending.
- `post` -- A `RunnableLambda` that strips whitespace from the response text.

### Entry Point

The `main()` coroutine runs a single conversation turn:
1. Pre-processes the query through the `pre` runnable.
2. Sends the query to the OxyGent server via `send_once`.
3. Prints the raw task JSON and the post-processed text.

## Key Concepts

- **Cross-Framework Interop**: A LangChain pipeline acts as a client to an OxyGent-hosted agent, demonstrating that A2A enables seamless communication regardless of the underlying framework.
- **A2A Message Envelope**: The client constructs standard A2A JSON-RPC payloads with `message/send` method, message parts, and optional session identifiers.
- **RunnableLambda as Glue**: LangChain runnables handle the pre/post processing, while raw HTTP handles the A2A transport -- showing how A2A fits into existing pipelines.

## Expected Behavior

When both the OxyGent server and this client are running, the client sends a query asking "which number is largest: 1, 5, 7" (in Chinese). The console output includes:
- `[turn1 raw]` -- the full A2A task JSON from the OxyGent server
- `[turn1]` -- the extracted and trimmed answer text from the LLM
