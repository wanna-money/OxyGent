# A2AClientAgent
---
该类在类层次结构中的位置：


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

## 简介

`A2AClientAgent` 是用于 [A2A (Agent-to-Agent)](https://github.com/google/A2A) 兼容服务器的远程 Agent 适配器。它解析远程 Agent 卡片，通过 A2A 协议（`message/send` 或 `message/stream`）发送消息，并将 A2A 响应标准化为 `OxyResponse`。它支持同步和流式请求模式、可选的任务轮询，以及通过 `context_id`/`task_id` 实现会话持久化。

## 参数


| 参数                               | 类型 / 允许的值           | 默认值                         | 描述                                                                                    |
| ------------------------------ | --------------------- | -------------------------- | ----------------------------------------------------------------------------------------------- |
| `agent_card_url`               | `str \| None`         | `None`                     | Agent 卡片的完整 URL（例如 `http://host/.well-known/agent.json?token=...`）。                     |
| `card_path`                    | `str \| None`         | `".well-known/agent.json"` | 当未设置 `agent_card_url` 时，追加到 `server_url` 的相对卡片路径。                                 |
| `metadata`                     | `dict[str, Any]`      | `{}`                       | 每次请求发送的默认 A2A 元数据。                                                                   |
| `headers`                      | `dict[str, str]`      | `{}`                       | A2A 调用的静态 HTTP 请求头。                                                                      |
| `streaming`                    | `bool`                | `False`                    | 使用 `message/stream` 代替 `message/send`。                                                      |
| `append_stream_suffix_to_url`  | `bool`                | `False`                    | 当 `streaming=True` 时，是否在卡片 URL 后追加 `/stream`。                                          |
| `enable_task_polling`          | `bool`                | `True`                     | 是否轮询 `tasks/get` 直到任务达到终态。                                                            |
| `task_poll_interval_seconds`   | `float`               | `3.0`                      | 任务轮询请求之间的间隔秒数。                                                                       |
| `task_poll_max_wait_seconds`   | `float`               | `60.0`                     | 轮询期间等待任务完成的最大秒数。                                                                    |
| `task_terminal_states`         | `list[str]`           | `["completed", "failed", "canceled", "rejected"]` | 被视为终态的任务状态。                                            |

## 方法


| 方法                                           | 协程（async）        | 返回值                 | 用途（简要）                                                                                                   |
| -------------------------------------------- | ----------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `minimal(**kwargs)`                          | 否（类方法）        | `A2AClientAgent`     | 使用便捷默认值创建实例的工厂方法。                                                                                |
| `init()`                                     | 是                | `None`               | 解析 Agent 卡片，创建 A2A SDK 客户端，并填充 `org` 组织结构树。                                                    |
| `_execute(oxy_request)`                      | 是                | `OxyResponse`        | 向 A2A 服务器发送查询（流式或非流式），必要时进行轮询，并返回标准化的 `OxyResponse`。                                 |
| `get_task(task_id, metadata, oxy_request)`   | 是                | `dict[str, Any]`     | 通过 ID 从远程 A2A 服务器获取任务。                                                                              |
| `cancel_task(task_id, oxy_request)`          | 是                | `dict[str, Any]`     | 取消远程 A2A 服务器上正在运行的任务。                                                                             |
| `resubscribe(task_id, oxy_request)`          | 是                | `list[dict[str, Any]]`| 重新订阅流式任务并收集事件。                                                                                     |

## 继承
 请参阅 [RemoteAgent](./remote_agent.md) 类以了解继承的参数和方法。

## 使用方式

`A2AClientAgent` 的简单用法如下：

```python
    oxy.A2AClientAgent(
        name="remote_a2a_agent",
        desc="An agent that communicates with an A2A server",
        server_url="http://127.0.0.1:8082",
    ),
```

流式模式与任务轮询：

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

或使用 `minimal()` 工厂方法：

```python
    oxy.A2AClientAgent.minimal(
        name="quick_a2a",
        server_url="http://127.0.0.1:8082",
        streaming=True,
    ),
```
