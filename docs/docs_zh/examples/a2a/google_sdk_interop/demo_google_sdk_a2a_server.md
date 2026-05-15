# Google A2A SDK 服务器

**源文件:** `examples/a2a/google_sdk_interop/demo_google_sdk_a2a_server.py`

## 概述

本示例使用 Google 官方 A2A SDK（`a2a-sdk`）实现了一个最小化的 A2A 服务器。它完全不使用 OxyGent，而是作为独立的 A2A 兼容服务器运行，供 OxyGent 客户端连接，从另一个方向验证跨框架互操作性。服务器支持同步和流式消息处理，使用简单的回显式响应。

## 前置条件

- 额外依赖包：`pip install a2a-sdk uvicorn`
- 不需要 LLM 凭证——此服务器返回硬编码的回显响应。

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_google_sdk_a2a_server.py
```

服务器启动后运行在 `http://127.0.0.1:8011`。

## 代码详解

### 配置

- `HOST = "0.0.0.0"` -- 绑定到所有网络接口。
- `PORT = 8011` -- HTTP 端口。
- `BASE_URL = f"http://127.0.0.1:{PORT}"` -- 在智能体卡片中公布的 URL。

### 智能体卡片：`build_agent_card`

构造描述服务器能力的 `AgentCard`：

- **`name`**：`"google_sdk_demo_server"` -- 智能体的显示名称。
- **`capabilities`**：`push_notifications=False`、`state_transition_history=True`、`streaming=True`。
- **`default_input_modes` / `default_output_modes`**：均设置为 `["text/plain"]`。
- **`skills`**：一个名为 `"chat"` 的技能，标签为 `["a2a", "sdk", "interop"]`。

### 处理器：`SimpleA2AHandler`

处理器类实现了 A2A SDK 框架分发消息时调用的两个方法：

#### `on_message_send`

处理同步 `message/send` 请求：

1. 通过 `get_message_text` 从 `params.message` 提取查询文本。
2. 保留传入消息的 `context_id` 和 `task_id`。
3. 返回一个包含回显式回复的 `Message`：`"Google SDK A2A server reply: I received your question: {query}"`。

#### `on_message_send_stream`

处理流式 `message/stream` 请求：

1. 产出一个初始 `TaskStatusUpdateEvent`，状态为 `TaskState.working`。
2. 逐字符遍历响应文本，为每个字符产出一个 `TaskStatusUpdateEvent`，包含累积文本。每个事件之间有 0.1 秒的延迟，模拟实时生成。
3. 产出一个最终的 `TaskStatusUpdateEvent`，状态为 `TaskState.completed`。

### 应用设置

Google SDK 的 `A2AStarletteApplication` 将智能体卡片和处理器组装成 Starlette ASGI 应用：

```python
app = A2AStarletteApplication(
    agent_card=build_agent_card(),
    http_handler=handler,
).build()
```

通过 `uvicorn.run()` 启动服务。

## 核心概念

- **Google A2A SDK 服务器**：`a2a-sdk` 包提供 `A2AStarletteApplication`，用于构建不依赖 OxyGent 的 A2A 兼容服务器。这是互操作性故事的"另一面"。
- **处理器模式**：SDK 使用包含 `on_message_send` 和 `on_message_send_stream` 方法的处理器类。框架将传入的 JSON-RPC 请求分发到相应的处理器。
- **通过 AsyncGenerator 实现流式传输**：流式响应实现为产出 `Event` 对象（具体为 `TaskStatusUpdateEvent`）的 Python 异步生成器。SDK 将这些转换为 SSE 事件。
- **逐字符流式传输**：流式处理器通过每隔 100ms 发出一个字符来模拟 token 级别的流式传输。

## 预期行为

启动后：

1. 日志输出 `"Starting Google SDK A2A demo server at 0.0.0.0:8011"`。
2. 在 `http://127.0.0.1:8011/.well-known/agent.json` 提供智能体卡片。
3. 对于非流式请求：立即返回回显响应。
4. 对于流式请求：逐字符发出 SSE 事件，最后发出 `completed` 事件。
5. 持续运行直到手动终止（Ctrl+C）。
