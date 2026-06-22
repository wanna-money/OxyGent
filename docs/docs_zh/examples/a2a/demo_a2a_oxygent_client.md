# A2A OxyGent 客户端（非流式）

**源文件:** `examples/a2a/demo_a2a_oxygent_client.py`

## 概述

本示例演示如何使用 OxyGent 内置的 `A2AClientAgent` 向 A2A 服务器发送非流式消息并获取任务结果。它创建了一个仅包含 A2A 客户端智能体的轻量级 MAS，发送单条查询，打印响应，然后通过 `get_task` 获取完整的任务对象。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`（服务端需要，客户端本身不需要）
- 先启动 A2A 服务器：`PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py`

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_client.py
```

## 代码详解

### 配置

- `SERVER_URL = "http://127.0.0.1:8090/a2a"` -- 指向由 `demo_a2a_oxygent_server.py` 启动的 OxyGent A2A 服务器。
- `Config.set_app_name("demo-a2a-oxygent-client")` -- 设置应用名称，用于日志和追踪。

### 组件（`oxy_space`）

注册了一个组件：

- **`A2AClientAgent.minimal()`** -- 创建最小化 A2A 客户端智能体的工厂方法：
  - `name="a2a_client"` -- 智能体在 MAS 中的标识符。
  - `server_url=SERVER_URL` -- A2A 服务器端点。
  - `timeout=60` -- HTTP 请求超时时间（秒）。
  - `streaming=False` -- 使用同步 `message/send` 而非 `message/stream`。
  - `enable_task_polling=False` -- 不自动轮询任务完成状态。

### 辅助函数：`call_once`

`call_once` 函数构造一个 `OxyRequest` 并分发给 `a2a_client` 智能体。它接受用于多轮对话的可选参数：

- `context_id` -- 标识 A2A 服务器上的会话。
- `task_id` -- 引用某个先前的特定任务。
- `reference_task_ids` -- 先前任务 ID 的列表，用于提供后续对话的上下文。

请求设置了 `is_send_message=False` 和 `is_save_history=False`，避免触发 MAS 内部的消息通知和历史持久化，因为这是一个仅包含客户端的 MAS。

### 入口

`main()` 协程：

1. 创建仅包含 A2A 客户端智能体的 MAS。
2. 通过 `call_once` 发送查询（"1+1等于几"）。
3. 提取并打印响应文本和会话元数据（`context_id`、`task_id`）。
4. 如果返回了 `task_id`，则调用 `client.get_task(task_id)` 从服务器获取完整的任务对象，并以格式化 JSON 打印。

## 核心概念

- **`A2AClientAgent.minimal()`**：便捷工厂方法，无需完整的智能体配置即可创建客户端智能体。它在内部处理智能体卡片解析、消息格式化和响应解析。
- **`OxyRequest` 参数**：`arguments` 中的 `query` 键是主要的用户消息。额外的键（`context_id`、`task_id`、`reference_task_ids`）用于多轮对话追踪。
- **`get_task`**：从 A2A 服务器获取任务的当前状态，可用于验证任务完成或检查产物。

## 预期行为

运行后（需先启动服务器）：

1. 向 A2A 服务器发送查询，收到 LLM 生成的答案（如 "1+1=2"）。
2. 打印响应文本。
3. 打印会话标识符（`context_id` 和 `task_id`）。
4. 从服务器获取并打印完整的任务 JSON，显示任务状态、产物和元数据。
