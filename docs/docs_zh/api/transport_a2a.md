# Transport — A2A Protocol

---
模块所在位置:

```
oxygent/transport/a2a/
├── a2a_server_gateway.py  → A2AServerGateway
├── a2a_store.py           → A2AInMemoryStore
├── a2a_card.py            → agent card 辅助函数
├── a2a_mapper.py          → 请求/响应映射
└── a2a_protocol.py        → JSON-RPC 载荷构建器
```

---

## 简介

`transport/a2a` 子包实现了 OxyGent 的 Agent-to-Agent（A2A）协议网关。它将 MAS 暴露为一个 A2A 兼容的 Agent，提供 JSON-RPC 端点、流式传输支持和任务生命周期管理。网关将传入的 A2A 请求转换为 MAS 聊天调用，并将 MAS 响应转换回 A2A 协议消息。

---

## A2AServerGateway (BaseModel)

`A2AServerGateway`（`a2a_server_gateway.py`）是主类，用于构建包含所有 A2A 兼容端点的 FastAPI 路由。

### 参数

| 参数                              | 类型              | 默认值                                                                                  | 描述                                                     |
| -------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `mas`                                  | `Any`             | `None`                                                                                   | MAS 运行时引用。                                          |
| `target_agent_name`                    | `str`             | `"master_agent"`                                                                         | 解析后的目标 Agent 名称。                                     |
| `a2a_base_path`                        | `str`             | `"/a2a"`                                                                                 | A2A 端点挂载的基础 URL 路径。                  |
| `agent_version`                        | `str`             | `"0.1.0"`                                                                                | 服务端 Agent 版本字符串。                                     |
| `capabilities`                         | `dict`            | `{"streaming": True, "task_control": True, "stateTransitionHistory": True, "pushNotifications": False}` | A2A 能力声明。    |
| `parse_stream_delta`                   | `bool`            | `True`                                                                                   | 是否解析 OxyGent SSE 流并提取增量内容。         |
| `stream_task_update_char_interval`     | `int`             | `128`                                                                                    | 刷新任务快照前的最小字符增量。            |
| `stream_task_update_time_interval_seconds` | `float`       | `1.0`                                                                                    | 任务快照刷新的最大时间间隔（秒）。                    |
| `skills`                               | `list`            | `[]`                                                                                     | 可选的 Agent Card 静态技能覆盖。             |

### 方法

| 方法           | 协程 (async) | 返回值  | 用途                                                          |
| ---------------- | ----------------- | ------------- | -------------------------------------------------------------------------- |
| `set_mas(mas)`   | 否                | `None`        | 绑定 MAS 运行时，并将 `target_agent_name` 同步为 `mas.master_agent_name`。  |
| `build_router()` | 否                | `APIRouter`   | 构建并返回包含所有 A2A 端点的 FastAPI 路由。                  |

### 注册的路由

| 路由                                      | 方法 | 用途                                   |
| ------------------------------------------ | ------ | ----------------------------------------- |
| `{base}/.well-known/agent.json`            | GET    | 返回 A2A Agent Card。                |
| `{base}` / `{base}/`                       | POST   | 统一入口（JSON-RPC 调度）。  |
| `{base}/messages/send` / `{base}/messages/send/`   | POST   | 发送消息（同步或流式）。       |
| `{base}/tasks/get` / `{base}/tasks/get/`           | POST   | 按 ID 检索任务。                    |
| `{base}/tasks/cancel` / `{base}/tasks/cancel/`     | POST   | 取消正在运行的任务。                    |

---

## A2AInMemoryStore

`A2AInMemoryStore`（`a2a_store.py`）为网关提供内存中的任务和上下文存储。

### 参数

| 参数          | 类型        | 默认值  | 描述                                              |
| ------------------ | ----------- | -------- | -------------------------------------------------------- |
| `task_store`       | `dict`      | `{}`     | 将 `task_id` 映射到任务快照字典。                   |
| `context_store`    | `dict`      | `{}`     | 将 `context_id` 映射到上下文会话字典。              |
| `running_task_ids` | `set`       | `set()`  | 当前正在运行的任务 ID 集合。                       |

### 方法

| 方法                                                    | 协程 (async) | 返回值     | 用途                                         |
| --------------------------------------------------------- | ----------------- | ---------------- | --------------------------------------------------------- |
| `context_session(context_id)`                             | 否                | `dict`           | 返回指定 context_id 的上下文会话。              |
| `save_context(context_id, group_id, trace_id, task_id)`   | 否                | `None`           | 保存/覆盖上下文会话。                       |
| `is_running(task_id)`                                     | 否                | `bool`           | 检查任务是否在运行集合中。                    |
| `mark_running(task_id)`                                   | 否                | `None`           | 将任务添加到运行集合中。                            |
| `unmark_running(task_id)`                                 | 否                | `None`           | 将任务从运行集合中移除。                       |
| `get_task(task_id)`                                       | 否                | `Optional[dict]` | 按 ID 检索任务快照。                           |
| `build_task(task_id, context_id, answer, trace_id, ...)`  | 否                | `dict`           | 构建并缓存带有状态处理的任务快照。       |

---

## 辅助模块

### a2a_card.py — Agent Card 辅助函数

| 函数                                              | 返回值        | 用途                                                     |
| ----------------------------------------------------- | ------------------- | ----------------------------------------------------------- |
| `card_identity(mas)`                                  | `tuple[str, str]`   | 从 MAS 主 Agent 解析 Card 名称和描述。    |
| `effective_target(mas, target_agent_name)`             | `str`               | 解析传入 A2A 请求的目标 MAS Agent。     |
| `build_skills_from_org(mas, skills_override)`          | `list[dict]`        | 从 MAS 组织树构建 Card 技能列表。          |
| `build_agent_card(request_base_url, a2a_base_path, agent_version, capabilities, mas, skills_override)` | `dict` | 构建完整的 A2A 兼容 Agent Card 响应。 |

### a2a_mapper.py — 请求/响应映射

| 函数                                               | 返回值        | 用途                                                    |
| ------------------------------------------------------ | ------------------- | ---------------------------------------------------------- |
| `normalize_message_payload(payload)`                   | `dict`              | 从载荷中提取嵌套的 `"message"` 字典。            |
| `extract_text(payload)`                                | `str`               | 从各种 A2A 载荷格式中提取纯文本。        |
| `extract_metadata(payload)`                            | `dict`              | 安全地从载荷中提取元数据。                      |
| `extract_context_and_task(payload, fallback_message)`  | `tuple[str, str]`   | 提取 `contextId` 和 `taskId`，缺失时生成 UUID。 |
| `extract_reference_task_ids(payload, fallback_message)` | `list[str]`        | 提取可选的 `referenceTaskIds` 列表。                  |
| `build_mas_payload(text, context_id, task_id, target, ...)` | `Optional[dict]` | 将 A2A 请求转换为 MAS 兼容的聊天载荷。    |
| `extract_delta_from_sse_data(data, parse_delta)`       | `str`               | 从 OxyGent SSE 载荷中提取文本增量。               |

### a2a_protocol.py — JSON-RPC 载荷构建器

| 函数                                        | 返回值 | 用途                                              |
| ----------------------------------------------- | ------------ | ---------------------------------------------------- |
| `rpc_ok(req_id, result)`                        | `dict`       | 构建 JSON-RPC 2.0 成功响应封装。               |
| `rpc_error(req_id, code, message)`              | `dict`       | 构建 JSON-RPC 2.0 错误响应封装。                 |
| `build_message_event(text, task_id, context_id)` | `dict`      | 构建标准化的 A2A 消息事件载荷。        |
| `build_agent_message(text, task_id, context_id)` | `dict`      | 构建用于任务状态的 Agent 消息。              |
| `build_final_artifact(text)`                    | `dict`       | 构建带有生成的 `artifactId` 的文本制品。   |
