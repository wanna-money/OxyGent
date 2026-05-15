# A2AClientAgent
---
The position of the class is:


```markdown
[Oxy](./base_oxy.md)
├── [BaseFlow](./base_flow.md)
│   └── [BaseAgent](./base_agent.md)
│       ├── [LocalAgent](./local_agent.md)
│       │   ├── [ChatAgent](./chat_agent.md)
│       │   │   └── [RAGAgent](./rag_agent.md)
│       │   ├── [ReActAgent](./react_agent.md)
│       │   │   ├── [ShellUseAgent](./shell_use_agent.md)
│       │   │   └── [SkillAgent](./skill_agent.md)
│       │   ├── [ParallelAgent](./parallel_agent.md)
│       │   ├── [WorkflowAgent](./workflow_agent.md)
│       │   └── [PlanAndSolveAgent](./plan_and_solve_agent.md)
│       └── [RemoteAgent](./remote_agent.md)
│           ├── [SSEOxyGent](./sse_oxy_agent.md)
│           └── [A2AClientAgent](./a2a_client_agent.md)
└── [BaseTool](../tools/base_tools.md)
```

---

## Introduction

`A2AClientAgent` is a remote agent adapter for [A2A (Agent-to-Agent)](https://github.com/google/A2A)-compatible servers. It resolves the remote agent card, sends messages through the A2A protocol (`message/send` or `message/stream`), and normalizes A2A responses into `OxyResponse`. It supports both synchronous and streaming request modes, optional task polling, and session persistence via `context_id`/`task_id`.

## Parameters


| Parameter                      | Type / Allowed value  | Default                    | Description                                                                                     |
| ------------------------------ | --------------------- | -------------------------- | ----------------------------------------------------------------------------------------------- |
| `agent_card_url`               | `str \| None`         | `None`                     | Full URL to the agent card (e.g. `http://host/.well-known/agent.json?token=...`).               |
| `card_path`                    | `str \| None`         | `".well-known/agent.json"` | Relative card path appended to `server_url` when `agent_card_url` is not set.                   |
| `metadata`                     | `dict[str, Any]`      | `{}`                       | Default A2A metadata sent with every request.                                                   |
| `headers`                      | `dict[str, str]`      | `{}`                       | Static HTTP headers for A2A calls.                                                              |
| `streaming`                    | `bool`                | `False`                    | Use `message/stream` instead of `message/send`.                                                 |
| `append_stream_suffix_to_url`  | `bool`                | `False`                    | Whether to append `/stream` to the card URL when `streaming=True`.                              |
| `enable_task_polling`          | `bool`                | `True`                     | Whether to poll `tasks/get` until the task reaches a terminal state.                            |
| `task_poll_interval_seconds`   | `float`               | `3.0`                      | Seconds between task polling requests.                                                          |
| `task_poll_max_wait_seconds`   | `float`               | `60.0`                     | Maximum seconds to wait for task completion during polling.                                      |
| `task_terminal_states`         | `list[str]`           | `["completed", "failed", "canceled", "rejected"]` | Task states considered final for polling.                             |

## Methods


| Method                                       | Coroutine (async) | Return Value         | Purpose (concise)                                                                                                |
| -------------------------------------------- | ----------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `minimal(**kwargs)`                          | No (classmethod)  | `A2AClientAgent`     | Factory method for creating an instance with convenient defaults.                                                |
| `init()`                                     | Yes               | `None`               | Resolve agent card, create A2A SDK client, and populate `org` tree.                                              |
| `_execute(oxy_request)`                      | Yes               | `OxyResponse`        | Send query to A2A server (streaming or non-streaming), poll if needed, and return normalized `OxyResponse`.      |
| `get_task(task_id, metadata, oxy_request)`   | Yes               | `dict[str, Any]`     | Retrieve a task by ID from the remote A2A server.                                                                |
| `cancel_task(task_id, oxy_request)`          | Yes               | `dict[str, Any]`     | Cancel a running task on the remote A2A server.                                                                  |
| `resubscribe(task_id, oxy_request)`          | Yes               | `list[dict[str, Any]]`| Resubscribe to a streaming task and collect events.                                                             |

## Inherited
 Please refer to the [RemoteAgent](./remote_agent.md) class for inherited parameters and methods.

## Usage

A simple usage of `A2AClientAgent` is like:

```python
    oxy.A2AClientAgent(
        name="remote_a2a_agent",
        desc="An agent that communicates with an A2A server",
        server_url="http://127.0.0.1:8082",
    ),
```

For streaming mode with task polling:

```python
    oxy.A2AClientAgent(
        name="streaming_a2a_agent",
        desc="Streaming A2A client",
        server_url="http://127.0.0.1:8082",
        streaming=True,
        enable_task_polling=True,
        task_poll_interval_seconds=2.0,
        task_poll_max_wait_seconds=30.0,
    ),
```

Or use the `minimal()` factory:

```python
    oxy.A2AClientAgent.minimal(
        name="quick_a2a",
        server_url="http://127.0.0.1:8082",
        streaming=True,
    ),
```
