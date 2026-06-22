# Google A2A SDK 流式客户端调用 OxyGent 服务器

**源文件:** `examples/a2a/google_sdk_interop/demo_a2a_sdk_stream_call_oxygent.py`

## 概述

本示例使用 Google A2A SDK 以流式模式调用 OxyGent A2A 服务器。它通过 `message/stream` 端点发送消息，并实时处理 SSE 数据块，在数据到达时逐步打印文本增量。示例包含辅助逻辑，用于从各种 A2A 事件类型（`Message`、`Task`、`TaskStatusUpdateEvent`、`TaskArtifactUpdateEvent`）中提取文本。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`（服务端需要）
- 额外依赖包：`pip install a2a-sdk`
- 先启动 OxyGent A2A 服务器：`PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py`

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_a2a_sdk_stream_call_oxygent.py
```

## 代码详解

### 配置

- `base_url = "http://127.0.0.1:8090/a2a"` -- OxyGent A2A 服务器端点。
- `card_path = ".well-known/agent.json"` -- 智能体卡片发现路径。
- HTTP 超时设置为 120 秒以适应流式传输。

### 辅助函数：`extract_text`

工具函数，从 A2A 流式数据块中可能出现的各种结果类型中提取文本内容：

- **`Message`**：使用 A2A SDK 工具函数 `get_message_text()`。
- **`Task`**：从任务的状态消息和任何产物中提取文本。
- **`TaskStatusUpdateEvent`**：从事件的状态消息中提取文本。
- **`TaskArtifactUpdateEvent`**：从产物的 parts 中提取文本。

该函数处理了 A2A 流式响应的多态性，不同类型的数据块以不同的结构承载文本。

### 流式消息发送

消息负载的构造与非流式示例相同，然后封装在 `SendStreamingMessageRequest` 中：

```python
req = SendStreamingMessageRequest(
    id=str(uuid4()),
    params=MessageSendParams(**payload),
)
```

响应通过异步迭代器消费：

```python
async for chunk in client.send_message_streaming(req):
    ...
```

### 增量计算

流式循环维护一个 `emitted` 字符串，跟踪已打印的所有文本。对于每个数据块：

1. 通过 `extract_text` 提取文本内容。
2. 计算增量（尚未打印的新字符）。
3. 使用 `end=''` 立即打印增量，实现打字机效果。
4. 更新 `emitted` 累积器。

这种方法同时处理发送累积文本的服务器（每个数据块包含到目前为止的完整文本）和仅发送增量文本的服务器。

### 入口

`main()` 协程：

1. 解析智能体卡片并打印服务器 URL。
2. 创建 `A2AClient`。
3. 发送流式请求，要求服务器分三点介绍 OxyGent A2A 流式能力。
4. 实时打印到达的数据块。
5. 流结束后打印最终累积的完整文本。

## 核心概念

- **SSE 流式传输**：A2A 协议支持 Server-Sent Events 进行实时响应传递。每个 SSE 事件携带一个 JSON-RPC 响应，包含 `TaskStatusUpdateEvent` 或 `TaskArtifactUpdateEvent`。
- **多态数据块类型**：A2A 流式响应可以包含 `Message`、`Task`、`TaskStatusUpdateEvent` 或 `TaskArtifactUpdateEvent` 对象。健壮的客户端必须处理所有类型。
- **增量累积**：由于不同的 A2A 服务器可能发送累积文本或增量文本，增量逻辑确保无论服务器行为如何都能正确显示。
- **跨框架流式传输**：验证了 OxyGent 的流式 A2A 端点与 Google A2A SDK 的流式客户端兼容。

## 预期行为

运行后（需先启动 OxyGent 服务器）：

1. 打印 `[card]` 加上服务器 URL。
2. 打印 `[stream begin]`，然后逐字符（或逐块）流式输出响应文本。
3. SSE 流关闭时打印 `[stream end]`。
4. 打印 `[final]` 加上完整的累积响应文本。
