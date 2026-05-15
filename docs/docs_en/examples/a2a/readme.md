# A2A Protocol Examples

These examples demonstrate OxyGent's implementation of the Agent-to-Agent (A2A) protocol, covering both native OxyGent-to-OxyGent communication and cross-framework interoperability with Google A2A SDK, LangChain, LangGraph, and AgentScope.

---

## OxyGent Native A2A

### A2A Server

**File:** `examples/a2a/demo_a2a_oxygent_server.py`

Starts an OxyGent MAS instance with the built-in A2A server enabled. The server registers a `ChatAgent` backed by an `HttpLLM` as the master agent and exposes A2A endpoints at a configurable base path (`/a2a`). The key configuration is passing `enable_a2a_server=True` and `a2a_base_path` to the `MAS` constructor, which automatically mounts A2A protocol routes (including the `.well-known/agent.json` agent card endpoint) onto the FastAPI web service. This server is used as the prerequisite for most client examples in this directory.

**Key Components:**
- `HttpLLM` -- LLM backend for the agent
- `ChatAgent` -- master agent that handles incoming A2A requests
- `MAS` -- runtime container with `enable_a2a_server=True`

**[Detailed Guide →](./demo_a2a_oxygent_server.md)**

---

### A2A Client (Non-Streaming)

**File:** `examples/a2a/demo_a2a_oxygent_client.py`

Demonstrates calling an OxyGent A2A server using the `A2AClientAgent` in non-streaming mode. The client is created via the `A2AClientAgent.minimal()` factory method with `streaming=False`. After sending a query, it extracts the `task_id` from the response and uses `client.get_task()` to retrieve the full task object, demonstrating both the `message/send` and `tasks/get` A2A protocol methods. The example also shows how to access `context_id` and `task_id` from the response's `extra` dict.

**Key Components:**
- `A2AClientAgent.minimal()` -- lightweight A2A client agent factory
- `MAS` -- runtime container for the client agent
- `OxyRequest` -- request object carrying query arguments

**[Detailed Guide →](./demo_a2a_oxygent_client.md)**

---

### A2A Client (Streaming)

**File:** `examples/a2a/demo_a2a_oxygent_stream_client.py`

Shows how to use `A2AClientAgent` in streaming mode by setting `streaming=True` in the `minimal()` factory. The client sends a query and receives the response via the `message/stream` A2A protocol method, with incremental token delivery. After the stream completes, it retrieves the full task using `get_task()` and prints the final output along with session metadata (`context_id`, `task_id`).

**Key Components:**
- `A2AClientAgent.minimal()` -- with `streaming=True`
- `MAS` -- runtime container
- `OxyRequest` -- request with query arguments

**[Detailed Guide →](./demo_a2a_oxygent_stream_client.md)**

---

### A2A Task Follow-Up Client

**File:** `examples/a2a/demo_a2a_oxygent_task_followup_client.py`

Validates multi-turn conversation continuity through the A2A protocol using `context_id` and `reference_task_ids`. The client sends an initial query, captures the returned `context_id` and `task_id`, then sends a follow-up query that references the first task via `reference_task_ids`. This demonstrates the A2A protocol's support for stateful, multi-turn conversations where the server can use prior task context. The client also enables `enable_task_polling=True` to support asynchronous task completion patterns.

**Key Components:**
- `A2AClientAgent.minimal()` -- with `enable_task_polling=True`
- `context_id` / `reference_task_ids` -- A2A session continuity fields
- `MAS`, `OxyRequest` -- standard OxyGent runtime and request types

**[Detailed Guide →](./demo_a2a_oxygent_task_followup_client.md)**

---

## Google A2A SDK Interop

### Google SDK A2A Server

**File:** `examples/a2a/google_sdk_interop/demo_google_sdk_a2a_server.py`

Implements a standalone A2A server using the official Google A2A SDK (`a2a` package). The server defines an `AgentCard` with streaming capabilities and a `SimpleA2AHandler` class that handles both `on_message_send` (synchronous) and `on_message_send_stream` (streaming with character-by-character `TaskStatusUpdateEvent` emissions). The application is built with `A2AStarletteApplication` and served via uvicorn. This server is used as the target when testing OxyGent clients against a Google SDK-based server.

**Key Components:**
- `A2AStarletteApplication` -- Google SDK's Starlette-based A2A app builder
- `AgentCard` / `AgentSkill` -- A2A agent metadata definitions
- `SimpleA2AHandler` -- implements `on_message_send` and `on_message_send_stream`
- `TaskStatusUpdateEvent` -- streaming status updates with partial messages

**[Detailed Guide →](./google_sdk_interop/demo_google_sdk_a2a_server.md)**

---

### Google SDK Client Calls OxyGent Server (Non-Streaming)

**File:** `examples/a2a/google_sdk_interop/demo_a2a_sdk_call_oxygent.py`

Uses the Google A2A SDK's `A2AClient` and `A2ACardResolver` to call an OxyGent A2A server. The client resolves the agent card from the server's `.well-known/agent.json` endpoint, then sends a `SendMessageRequest` using the SDK's typed request/response models. It also includes a `poll_task()` utility that repeatedly calls `tasks/get` until the task reaches a terminal state (completed, failed, canceled, or rejected). This demonstrates that OxyGent's A2A server is fully compatible with standard Google A2A SDK clients.

**Key Components:**
- `A2ACardResolver` -- resolves agent cards from a server URL
- `A2AClient` -- Google SDK's A2A client
- `SendMessageRequest` / `MessageSendParams` -- typed A2A request models
- `poll_task()` -- task polling utility with timeout

**[Detailed Guide →](./google_sdk_interop/demo_a2a_sdk_call_oxygent.md)**

---

### Google SDK Client Calls OxyGent Server (Streaming)

**File:** `examples/a2a/google_sdk_interop/demo_a2a_sdk_stream_call_oxygent.py`

Demonstrates streaming interop by using the Google A2A SDK's `send_message_streaming()` method against an OxyGent A2A server. The client resolves the agent card, sends a `SendStreamingMessageRequest`, and iterates over the streamed chunks. An `extract_text()` helper function handles multiple result types (`Message`, `Task`, `TaskStatusUpdateEvent`, `TaskArtifactUpdateEvent`) to extract text content, computing deltas for incremental display. This validates that OxyGent's streaming A2A responses are correctly consumed by standard SDK clients.

**Key Components:**
- `A2AClient.send_message_streaming()` -- SDK streaming method
- `SendStreamingMessageRequest` -- typed streaming request
- `extract_text()` -- multi-type text extraction helper

**[Detailed Guide →](./google_sdk_interop/demo_a2a_sdk_stream_call_oxygent.md)**

---

### OxyGent Client Calls Google SDK Server (Non-Streaming)

**File:** `examples/a2a/google_sdk_interop/demo_oxygent_client_call_google_sdk_server.py`

Uses OxyGent's `A2AClientAgent` to call a Google A2A SDK server in non-streaming mode. The example also demonstrates passing custom HTTP headers (e.g., authentication tokens) to the A2A client via both the `headers` parameter in `A2AClientAgent.minimal()` and the `shared_data["_headers"]` field in `OxyRequest`. This is useful for scenarios where the remote A2A server requires authentication or custom request metadata.

**Key Components:**
- `A2AClientAgent.minimal()` -- with custom `headers` parameter
- `OxyRequest.shared_data["_headers"]` -- per-request header injection
- `MAS` -- runtime container

**[Detailed Guide →](./google_sdk_interop/demo_oxygent_client_call_google_sdk_server.md)**

---

### OxyGent Client Calls Google SDK Server (Streaming)

**File:** `examples/a2a/google_sdk_interop/demo_oxygent_stream_client_call_google_sdk_server.py`

Uses OxyGent's `A2AClientAgent` in streaming mode (`streaming=True`) to call a Google A2A SDK server. The client receives streaming responses and prints the final aggregated output along with session identifiers. This is the streaming counterpart to the non-streaming Google SDK interop example above, confirming bidirectional streaming compatibility between OxyGent clients and Google SDK servers.

**Key Components:**
- `A2AClientAgent.minimal()` -- with `streaming=True`
- `MAS`, `OxyRequest` -- standard OxyGent runtime types

**[Detailed Guide →](./google_sdk_interop/demo_oxygent_stream_client_call_google_sdk_server.md)**

---

## LangChain Interop

### LangChain A2A Server

**File:** `examples/a2a/langchain_interop/demo_langchain_a2a_server.py`

Implements a custom A2A-compatible server powered by LangChain. The server uses a `RunnableLambda` chain as its processing backend and exposes a FastAPI application with a JSON-RPC-style unified endpoint that handles `message/send`, `message/stream`, `tasks/get`, and `tasks/cancel` methods. The `message/stream` path returns an `EventSourceResponse` (SSE) that emits character-by-character incremental updates. An in-memory `TASKS` dict stores completed tasks for retrieval. The agent card is served at `/.well-known/agent.json`.

**Key Components:**
- `RunnableLambda` -- LangChain's minimal runnable for text processing
- `FastAPI` + `EventSourceResponse` -- SSE-based streaming endpoint
- JSON-RPC dispatch -- `message/send`, `message/stream`, `tasks/get`, `tasks/cancel`

**[Detailed Guide →](./langchain_interop/demo_langchain_a2a_server.md)**

---

### LangChain Client Calls OxyGent Server

**File:** `examples/a2a/langchain_interop/demo_langchain_client_call_oxygent_server.py`

Demonstrates calling an OxyGent A2A server from LangChain-style code. A `RunnableLambda` preprocesses the user query (adding a framework label prefix), and the client sends JSON-RPC `message/send` requests via `httpx.AsyncClient` to the OxyGent server. A post-processing `RunnableLambda` cleans up the response text. This shows how to integrate OxyGent A2A endpoints into existing LangChain pipelines using standard HTTP calls.

**Key Components:**
- `RunnableLambda` -- pre/post-processing wrappers
- `httpx.AsyncClient` -- direct HTTP JSON-RPC calls to OxyGent server
- A2A JSON-RPC protocol -- `message/send` method

**[Detailed Guide →](./langchain_interop/demo_langchain_client_call_oxygent_server.md)**

---

### OxyGent Client Calls LangChain Server (Non-Streaming)

**File:** `examples/a2a/langchain_interop/demo_oxygent_client_call_langchain_server.py`

Uses OxyGent's `A2AClientAgent` with `enable_task_polling=True` to call the LangChain A2A server in non-streaming mode. After sending a query, it prints the agent's response and session identifiers. This demonstrates that OxyGent's A2A client can seamlessly communicate with any third-party server that implements the A2A protocol, regardless of the underlying framework.

**Key Components:**
- `A2AClientAgent.minimal()` -- with `enable_task_polling=True`
- `MAS`, `OxyRequest` -- standard OxyGent runtime types

**[Detailed Guide →](./langchain_interop/demo_oxygent_client_call_langchain_server.md)**

---

### OxyGent Client Calls LangChain Server (Streaming)

**File:** `examples/a2a/langchain_interop/demo_oxygent_stream_client_call_langchain_server.py`

Uses OxyGent's `A2AClientAgent` in streaming mode to call the LangChain A2A server. The client receives incremental streaming responses via the `message/stream` protocol method and prints the final aggregated output. This is the streaming counterpart to the non-streaming LangChain interop client example.

**Key Components:**
- `A2AClientAgent.minimal()` -- with `streaming=True`
- `MAS`, `OxyRequest` -- standard OxyGent runtime types

**[Detailed Guide →](./langchain_interop/demo_oxygent_stream_client_call_langchain_server.md)**

---

## LangGraph Interop

### LangGraph A2A Server

**File:** `examples/a2a/langgraph_interop/demo_langgraph_a2a_server.py`

Implements an A2A-compatible server powered by LangGraph. The server defines a `StateGraph` with a single `answer_node` that processes queries and produces responses. Like the LangChain server, it exposes a FastAPI unified endpoint handling `message/send`, `message/stream`, `tasks/get`, and `tasks/cancel` via JSON-RPC dispatch. The `message/stream` path provides SSE-based character-by-character streaming. The graph state is typed using `TypedDict` (`GraphState`) with `query` and `answer` fields.

**Key Components:**
- `StateGraph` / `GraphState` -- LangGraph's state-based computation graph
- `FastAPI` + `EventSourceResponse` -- SSE streaming endpoint
- JSON-RPC dispatch -- `message/send`, `message/stream`, `tasks/get`, `tasks/cancel`

**[Detailed Guide →](./langgraph_interop/demo_langgraph_a2a_server.md)**

---

### LangGraph Client Calls OxyGent Server

**File:** `examples/a2a/langgraph_interop/demo_langgraph_client_call_oxygent_server.py`

Demonstrates calling an OxyGent A2A server from within a LangGraph graph. A `StateGraph` wraps the A2A call in a `call_node` that sends JSON-RPC `message/send` requests to the OxyGent server via `httpx.AsyncClient` and parses the response into the graph state (extracting `context_id`, `task_id`, and answer text). The graph is invoked asynchronously using `graph.ainvoke()`. This shows how to integrate OxyGent A2A endpoints as nodes in a LangGraph workflow.

**Key Components:**
- `StateGraph` / `GraphState` -- LangGraph computation graph with typed state
- `call_node` -- async graph node wrapping A2A HTTP calls
- `httpx.AsyncClient` -- direct JSON-RPC calls to OxyGent server

**[Detailed Guide →](./langgraph_interop/demo_langgraph_client_call_oxygent_server.md)**

---

### OxyGent Client Calls LangGraph Server (Non-Streaming)

**File:** `examples/a2a/langgraph_interop/demo_oxygent_client_call_langgraph_server.py`

Uses OxyGent's `A2AClientAgent` with `enable_task_polling=True` to call the LangGraph A2A server. This example performs a two-turn conversation: the first call sends a query, and the second call references the first turn's `context_id` and `task_id` to continue the conversation. This demonstrates multi-turn session continuity when OxyGent communicates with a LangGraph-based A2A server.

**Key Components:**
- `A2AClientAgent.minimal()` -- with `enable_task_polling=True`
- `context_id` / `task_id` -- multi-turn session tracking
- `MAS`, `OxyRequest` -- standard OxyGent runtime types

**[Detailed Guide →](./langgraph_interop/demo_oxygent_client_call_langgraph_server.md)**

---

### OxyGent Client Calls LangGraph Server (Streaming)

**File:** `examples/a2a/langgraph_interop/demo_oxygent_stream_client_call_langgraph_server.py`

Uses OxyGent's `A2AClientAgent` in streaming mode to call the LangGraph A2A server. The client receives incremental streaming responses and prints the final aggregated output with session metadata. This is the streaming counterpart to the non-streaming LangGraph interop client example.

**Key Components:**
- `A2AClientAgent.minimal()` -- with `streaming=True`
- `MAS`, `OxyRequest` -- standard OxyGent runtime types

**[Detailed Guide →](./langgraph_interop/demo_oxygent_stream_client_call_langgraph_server.md)**

---

## AgentScope Interop

### AgentScope A2A Server

**File:** `examples/a2a/agentscope_interop/demo_agentscope_a2a_server.py`

Implements an A2A server using the Google A2A SDK with AgentScope-style handling. The `AgentScopeStreamHandler` class implements `on_message_send_stream` to echo received messages back as character-by-character streaming responses via `TaskStatusUpdateEvent` emissions. The server is built with `A2AStarletteApplication` and its `AgentCard` advertises streaming and state transition history capabilities. The handler intentionally avoids external model dependencies, making it a self-contained interop test target.

**Key Components:**
- `A2AStarletteApplication` -- Google SDK's Starlette-based A2A app builder
- `AgentScopeStreamHandler` -- streaming handler with `on_message_send_stream`
- `AgentCard` / `AgentSkill` -- A2A agent metadata
- `TaskStatusUpdateEvent` -- incremental streaming status updates

**[Detailed Guide →](./agentscope_interop/demo_agentscope_a2a_server.md)**

---

### AgentScope Client Calls OxyGent Server

**File:** `examples/a2a/agentscope_interop/demo_agentscope_client_call_oxygent_server.py`

Uses AgentScope's native `A2AAgent` class to call an OxyGent A2A server. The client constructs an `AgentCard` pointing to the OxyGent server URL, creates an `A2AAgent` instance with that card, and sends a message using AgentScope's `Msg` class. Streaming is explicitly disabled in the agent card's capabilities to avoid async stream-close race conditions in the AgentScope demo runtime. This demonstrates that OxyGent's A2A server is compatible with AgentScope's native A2A client.

**Key Components:**
- `A2AAgent` -- AgentScope's built-in A2A client agent
- `AgentCard` -- pointing to OxyGent server with `streaming=False`
- `Msg` -- AgentScope's message type

**[Detailed Guide →](./agentscope_interop/demo_agentscope_client_call_oxygent_server.md)**

---

### OxyGent Client Calls AgentScope Server

**File:** `examples/a2a/agentscope_interop/demo_oxygent_client_call_agentscope_server.py`

Uses OxyGent's `A2AClientAgent` in streaming mode to call the AgentScope A2A server. The client is configured with `streaming=True` and includes task polling parameters (`task_poll_interval_seconds`, `task_poll_max_wait_seconds`) for flexibility. After sending a query, it prints the response and session metadata. This demonstrates OxyGent's ability to consume streaming A2A responses from an AgentScope-based server.

**Key Components:**
- `A2AClientAgent.minimal()` -- with `streaming=True` and polling parameters
- `MAS`, `OxyRequest` -- standard OxyGent runtime types

**[Detailed Guide →](./agentscope_interop/demo_oxygent_client_call_agentscope_server.md)**
