# Transport — A2A Protocol

---
The position of the modules is:

```
oxygent/transport/a2a/
├── a2a_server_gateway.py  → A2AServerGateway
├── a2a_store.py           → A2AInMemoryStore
├── a2a_card.py            → agent card helpers
├── a2a_mapper.py          → request/response mapping
└── a2a_protocol.py        → JSON-RPC payload builders
```

---

## Introduction

The `transport/a2a` subpackage implements the Agent-to-Agent (A2A) protocol gateway for OxyGent. It exposes the MAS as an A2A-compatible agent with JSON-RPC endpoints, streaming support, and task lifecycle management. The gateway translates incoming A2A requests into MAS chat calls and converts MAS responses back into A2A protocol messages.

---

## A2AServerGateway (BaseModel)

`A2AServerGateway` (`a2a_server_gateway.py`) is the main class that builds a FastAPI router with all A2A-compatible endpoints.

### Parameters

| Parameter                              | Type              | Default                                                                                  | Description                                                     |
| -------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `mas`                                  | `Any`             | `None`                                                                                   | MAS runtime reference.                                          |
| `target_agent_name`                    | `str`             | `"master_agent"`                                                                         | Resolved target agent name.                                     |
| `a2a_base_path`                        | `str`             | `"/a2a"`                                                                                 | Base URL path where A2A endpoints are mounted.                  |
| `agent_version`                        | `str`             | `"0.1.0"`                                                                                | Server agent version string.                                    |
| `capabilities`                         | `dict`            | `{"streaming": True, "task_control": True, "stateTransitionHistory": True, "pushNotifications": False}` | A2A capability declaration.    |
| `parse_stream_delta`                   | `bool`            | `True`                                                                                   | Whether to parse OxyGent SSE stream and extract deltas.         |
| `stream_task_update_char_interval`     | `int`             | `128`                                                                                    | Min character delta before refreshing task snapshot.            |
| `stream_task_update_time_interval_seconds` | `float`       | `1.0`                                                                                    | Max seconds between task snapshot refreshes.                    |
| `skills`                               | `list`            | `[]`                                                                                     | Optional static skills override for the agent card.             |

### Methods

| Method           | Coroutine (async) | Return Value  | Purpose (concise)                                                          |
| ---------------- | ----------------- | ------------- | -------------------------------------------------------------------------- |
| `set_mas(mas)`   | No                | `None`        | Bind MAS runtime and sync `target_agent_name` to `mas.master_agent_name`.  |
| `build_router()` | No                | `APIRouter`   | Build and return a FastAPI router with all A2A endpoints.                  |

### Registered Routes

| Route                                      | Method | Purpose                                   |
| ------------------------------------------ | ------ | ----------------------------------------- |
| `{base}/.well-known/agent.json`            | GET    | Return the A2A agent card.                |
| `{base}` / `{base}/`                       | POST   | Unified entry point (JSON-RPC dispatch).  |
| `{base}/messages/send` / `{base}/messages/send/`   | POST   | Send a message (sync or streaming).       |
| `{base}/tasks/get` / `{base}/tasks/get/`           | POST   | Retrieve a task by ID.                    |
| `{base}/tasks/cancel` / `{base}/tasks/cancel/`     | POST   | Cancel a running task.                    |

---

## A2AInMemoryStore

`A2AInMemoryStore` (`a2a_store.py`) provides in-memory task and context storage for the gateway.

### Parameters

| Parameter          | Type        | Default  | Description                                              |
| ------------------ | ----------- | -------- | -------------------------------------------------------- |
| `task_store`       | `dict`      | `{}`     | Maps `task_id` to task snapshot dicts.                   |
| `context_store`    | `dict`      | `{}`     | Maps `context_id` to context session dicts.              |
| `running_task_ids` | `set`       | `set()`  | Set of currently-running task IDs.                       |

### Methods

| Method                                                    | Coroutine (async) | Return Value     | Purpose (concise)                                         |
| --------------------------------------------------------- | ----------------- | ---------------- | --------------------------------------------------------- |
| `context_session(context_id)`                             | No                | `dict`           | Return the context session for a context_id.              |
| `save_context(context_id, group_id, trace_id, task_id)`   | No                | `None`           | Save/overwrite the context session.                       |
| `is_running(task_id)`                                     | No                | `bool`           | Check if a task is in the running set.                    |
| `mark_running(task_id)`                                   | No                | `None`           | Add a task to the running set.                            |
| `unmark_running(task_id)`                                 | No                | `None`           | Remove a task from the running set.                       |
| `get_task(task_id)`                                       | No                | `Optional[dict]` | Retrieve a task snapshot by ID.                           |
| `build_task(task_id, context_id, answer, trace_id, ...)`  | No                | `dict`           | Build and cache a task snapshot with state handling.       |

---

## Helper Modules

### a2a_card.py — Agent Card Helpers

| Function                                              | Return Value        | Purpose                                                     |
| ----------------------------------------------------- | ------------------- | ----------------------------------------------------------- |
| `card_identity(mas)`                                  | `tuple[str, str]`   | Resolve card name and description from MAS master agent.    |
| `effective_target(mas, target_agent_name)`             | `str`               | Resolve the target MAS agent for incoming A2A requests.     |
| `build_skills_from_org(mas, skills_override)`          | `list[dict]`        | Build card skills list from MAS organization tree.          |
| `build_agent_card(request_base_url, a2a_base_path, agent_version, capabilities, mas, skills_override)` | `dict` | Build a full A2A-compatible agent card response. |

### a2a_mapper.py — Request/Response Mapping

| Function                                               | Return Value        | Purpose                                                    |
| ------------------------------------------------------ | ------------------- | ---------------------------------------------------------- |
| `normalize_message_payload(payload)`                   | `dict`              | Extract nested `"message"` dict from a payload.            |
| `extract_text(payload)`                                | `str`               | Extract plain text from various A2A payload shapes.        |
| `extract_metadata(payload)`                            | `dict`              | Safely extract metadata from payload.                      |
| `extract_context_and_task(payload, fallback_message)`  | `tuple[str, str]`   | Extract `contextId` and `taskId`, generating UUIDs if missing. |
| `extract_reference_task_ids(payload, fallback_message)` | `list[str]`        | Extract optional `referenceTaskIds` list.                  |
| `build_mas_payload(text, context_id, task_id, target, ...)` | `Optional[dict]` | Translate A2A request into MAS-compatible chat payload.    |
| `extract_delta_from_sse_data(data, parse_delta)`       | `str`               | Extract text delta from OxyGent SSE payload.               |

### a2a_protocol.py — JSON-RPC Payload Builders

| Function                                        | Return Value | Purpose                                              |
| ----------------------------------------------- | ------------ | ---------------------------------------------------- |
| `rpc_ok(req_id, result)`                        | `dict`       | Build a JSON-RPC 2.0 success envelope.               |
| `rpc_error(req_id, code, message)`              | `dict`       | Build a JSON-RPC 2.0 error envelope.                 |
| `build_message_event(text, task_id, context_id)` | `dict`      | Build a normalized A2A message event payload.        |
| `build_agent_message(text, task_id, context_id)` | `dict`      | Build an agent message for task status.              |
| `build_final_artifact(text)`                    | `dict`       | Build a text artifact with generated `artifactId`.   |
