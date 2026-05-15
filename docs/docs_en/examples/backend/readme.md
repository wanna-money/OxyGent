# Backend & Infrastructure Examples

> This directory contains examples that demonstrate OxyGent's backend capabilities, including MAS launch modes, configuration, concurrency control, data scoping, hooks, message handling, and Oxy customization.

---

### Loading Configuration from JSON

**File:** `examples/backend/demo_config.py`

This example shows how to load configuration from a JSON file using `Config.load_from_json()`. The configuration system supports a `default` profile that can be merged with environment-specific overlays (e.g., `dev`, `prod`) selected by the `env` parameter. At deploy time, set the `APP_ENV` environment variable to switch profiles automatically without changing code.

**Key Components:** `Config`, `HttpLLM`, `ReActAgent`

**[Detailed Guide →](./demo_config.md)**

---

### MAS Launch Modes

**File:** `examples/backend/demo_launch_mas.py`

A comprehensive walkthrough of every way to launch and interact with a MAS instance. It demonstrates direct Oxy invocation via `mas.call()` (calling agents, tools, and LLMs by name), the high-level `mas.chat_with_agent()` entry point, interactive REPL via `start_cli_mode()`, concurrent batch execution via `start_batch_processing()`, web service via `start_web_service()`, and the factory method `MAS.create()` for non-context-manager usage.

**Key Components:** `MAS`, `HttpLLM`, `StdioMCPClient`, `ReActAgent`

**[Detailed Guide →](./demo_launch_mas.md)**

---

### Batch Processing with Semaphore

**File:** `examples/backend/demo_batch_and_semaphore.py`

Demonstrates how to run batch processing with concurrency control. The `semaphore` parameter on both `HttpLLM` and `ChatAgent` caps the number of concurrent executions, preventing resource exhaustion when processing many requests in parallel. In this example the LLM is limited to 4 concurrent calls and the agent to 6, while 10 queries are dispatched simultaneously via `start_batch_processing()`.

**Key Components:** `HttpLLM(semaphore=4)`, `ChatAgent(semaphore=6)`

**[Detailed Guide →](./demo_batch_and_semaphore.md)**

---

### Adding a Custom FastAPI Router

**File:** `examples/backend/demo_add_router.py`

Shows how to extend the MAS web service with custom FastAPI endpoints by passing an `APIRouter` instance through the `MAS(routers=[router])` parameter. The example registers a GET endpoint (`/api_name`) that returns a `WebResponse`, and a `WorkflowAgent` that calls this custom endpoint internally using `httpx`, illustrating how agents can interact with user-defined APIs within the same server.

**Key Components:** `APIRouter`, `WorkflowAgent`, `WebResponse`

**[Detailed Guide →](./demo_add_router.md)**

---

### Sending Attachments

**File:** `examples/backend/demo_attachment.py`

Demonstrates how to send file attachments alongside user queries for multimodal processing. By setting `is_multimodal_supported=True` on the LLM and including an `attachments` list in the payload, files (such as `README.md`) are passed to the model together with the query. This pattern supports image, document, and other file-based inputs when the underlying LLM supports multimodal content.

**Key Components:** `HttpLLM(is_multimodal_supported)`, `ChatAgent`

**[Detailed Guide →](./demo_attachment.md)**

---

### Custom Shared Data Schema

**File:** `examples/backend/demo_custom_shared_data_schema.py`

Illustrates how to define a custom Elasticsearch schema for `shared_data` using `Config.set_es_schema_shared_data()`, and how to populate shared data fields inside a `func_process_input` callback. The example registers a schema with `user_pin` and `user_name` keyword fields, then sets their values via `oxy_request.set_shared_data()` before the agent executes, making structured metadata available throughout the request lifecycle.

**Key Components:** `Config`, `HttpLLM`, `ReActAgent`

**[Detailed Guide →](./demo_custom_shared_data_schema.md)**

---

### Data Scoping

**File:** `examples/backend/demo_data_scope.py`

Explains the three data scoping levels in OxyGent and their visibility across agent calls. `shared_data` is scoped to a single trace and visible to the called agent and its sub-agents; `group_data` is scoped to a session group and persists across traces sharing the same `from_trace_id`; `global_data` is shared across the entire MAS instance. The example uses two ReActAgents (master and sub-agent) with `func_process_input` callbacks that print all data scopes at each step for inspection.

**Key Components:** `HttpLLM`, `StdioMCPClient`, `ReActAgent` (x2)

**[Detailed Guide →](./demo_data_scope.md)**

---

### Global Data

**File:** `examples/backend/demo_global_data.py`

Shows how to read and write `global_data` from inside a custom `BaseAgent` subclass. The example implements a `CounterAgent` that increments a call counter stored in `global_data` on every request, demonstrating how state persists across multiple calls within the same MAS instance. The counter is accessed via `oxy_request.get_global_data()` and updated via `oxy_request.set_global_data()`.

**Key Components:** `BaseAgent` (custom subclass), `HttpLLM`

**[Detailed Guide →](./demo_global_data.md)**

---

### Logger Setup

**File:** `examples/backend/demo_logger_setup.py`

Demonstrates how to configure custom logging in an OxyGent application using the `setup_logging()` utility from `oxygent.log_setup`. The logger is initialized at module level and then used inside a `func_process_input` callback to log incoming queries before they reach the agent. This pattern is useful for adding structured logging, debugging request flows, or integrating with external logging systems.

**Key Components:** `setup_logging`, `HttpLLM`, `ChatAgent`

**[Detailed Guide →](./demo_logger_setup.md)**

---

### MAS-Level Hooks

**File:** `examples/backend/demo_mas_hook.py`

Demonstrates the two MAS-level hook mechanisms for request interception. `func_filter` receives the incoming payload and can modify it before processing (e.g., injecting `group_data` with a user identifier). `func_interceptor` also receives the payload but can short-circuit the request entirely by returning a response dict (e.g., a 403 permission-denied error). Both hooks are passed as parameters to the `MAS` constructor.

**Key Components:** `HttpLLM`, `ChatAgent`

**[Detailed Guide →](./demo_mas_hook.md)**

---

### Controlling Message Storage and Sending

**File:** `examples/backend/demo_save_message.py`

Shows how to fine-tune message behavior using the `_is_stored` and `_is_send` flags on outbound messages. When sending messages via `oxy_request.send_message()`, `_is_stored` controls whether the message is persisted to the database, while `_is_send` controls whether it is pushed to the frontend via SSE. The example demonstrates all four combinations of these flags, along with global defaults set through `Config.set_message_is_stored()` and `Config.set_message_is_show_in_terminal()`.

**Key Components:** `HttpLLM(stream)`, `ChatAgent(func_process_input)`

**[Detailed Guide →](./demo_save_message.md)**

---

### Post-Processing Outbound Messages

**File:** `examples/backend/demo_process_message.py`

Demonstrates how to apply post-processing to all outbound messages using the `func_process_message` callback on MAS. The callback receives each message dict and the current `OxyRequest`, and can modify the message content before it reaches the frontend. In this example, every streaming token has a dash character appended to it, illustrating how to transform, filter, or enrich messages globally.

**Key Components:** `HttpLLM(stream)`, `ChatAgent`

**[Detailed Guide →](./demo_process_message.md)**

---

### Human-in-the-Loop

**File:** `examples/backend/demo_human_in_the_loop.py`

Implements a human-in-the-loop pattern using a `WorkflowAgent`. The workflow function sends a message to the frontend, then blocks on `oxy_request.get_feedback_stream()` to asynchronously receive user feedback via an SSE channel. The frontend can POST to the `/feedback` endpoint with the matching `channel_id` (defaults to `trace_id`) to send data back. Collected feedback is aggregated and returned as the workflow result.

**Key Components:** `HttpLLM`, `WorkflowAgent(func_workflow)`

**[Detailed Guide →](./demo_human_in_the_loop.md)**

---

### Subclassing an Oxy Component

**File:** `examples/backend/demo_rewrite_oxy.py`

Shows how to subclass `oxy.HttpLLM` and override the `_execute` method with a fully custom HTTP call implementation. The `MyHttpLLM` class builds its own request payload, makes a direct `httpx` POST call, parses the response JSON, and returns an `OxyResponse`. This pattern is useful when you need to integrate with non-standard LLM APIs, add custom authentication, or implement proprietary request/response transformations.

**Key Components:** `HttpLLM` (subclassed), `OxyResponse`

**[Detailed Guide →](./demo_rewrite_oxy.md)**
