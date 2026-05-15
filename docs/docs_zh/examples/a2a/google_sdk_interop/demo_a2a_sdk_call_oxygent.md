# Google A2A SDK 客户端调用 OxyGent 服务器

**源文件:** `examples/a2a/google_sdk_interop/demo_a2a_sdk_call_oxygent.py`

## 概述

本示例使用 Google 官方 A2A SDK（`a2a-sdk`）客户端调用 OxyGent A2A 服务器。它演示了跨框架互操作性：客户端完全使用 Google A2A SDK 的类型和客户端类构建，而服务器是启用了 A2A 的标准 OxyGent MAS。示例解析智能体卡片、发送非流式消息，并可选地轮询任务完成状态。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`（服务端需要）
- 额外依赖包：`pip install a2a-sdk`
- 先启动 OxyGent A2A 服务器：`PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py`

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_a2a_sdk_call_oxygent.py
```

## 代码详解

### 配置

- `base_url = "http://127.0.0.1:8090/a2a"` -- OxyGent A2A 服务器端点。
- `agent_card_path = ".well-known/agent.json"` -- 标准 A2A 智能体卡片发现路径。
- `streaming = False` -- 使用同步 `message/send`。
- `enable_polling = True` -- 在初始响应后启用任务轮询。

### 智能体卡片解析

示例使用 Google SDK 的 `A2ACardResolver` 发现智能体卡片：

```python
resolver = A2ACardResolver(
    httpx_client=httpx_client,
    base_url=base_url,
    agent_card_path=agent_card_path,
)
card: AgentCard = await resolver.get_agent_card()
```

解析出的 `AgentCard` 包含智能体的名称、能力、技能和 URL，`A2AClient` 使用这些信息来验证和路由请求。

### 发送消息

消息负载遵循 A2A 协议结构：

- `message.role` -- 设置为 `"user"`。
- `message.parts` -- 包含查询文本的 `TextPart` 列表。
- `message.messageId` -- 通过 `uuid4().hex` 生成的唯一标识符。

负载被封装在 `SendMessageRequest`（或 `SendStreamingMessageRequest`，如果 `streaming=True`）中，通过 `client.send_message()` 发送。

### 任务轮询：`poll_task`

`poll_task` 函数反复调用 `client.get_task()`，直到任务达到终态（`completed`、`failed`、`canceled`、`rejected`）或轮询超时：

1. 构造 `GetTaskRequest`，指定目标 `task_id`。
2. 检查响应中任务的 `status.state`。
3. 在两次轮询之间休眠 `interval_seconds`。
4. `max_wait_seconds` 后超时。

### 入口

`main()` 协程：

1. 创建 `httpx.AsyncClient`，超时时间 60 秒。
2. 解析智能体卡片并打印。
3. 创建绑定到已解析卡片的 `A2AClient`。
4. 发送查询（"计算1+1的结果"）。
5. 打印服务器返回的完整 JSON 响应。

## 核心概念

- **跨框架互操作性**：本示例证明 OxyGent 的 A2A 服务器实现与 Google A2A SDK 客户端完全兼容，验证了协议合规性。
- **`A2ACardResolver`**：Google SDK 通过 `.well-known/agent.json` 端点发现智能体能力的机制。
- **`A2AClient`**：Google SDK 的 HTTP 客户端，用于向 A2A 兼容服务器发送消息和管理任务。
- **任务轮询**：一种处理异步任务完成的模式，适用于服务器不立即返回结果的场景。

## 预期行为

运行后（需先启动 OxyGent 服务器）：

1. 打印智能体卡片 JSON，显示服务器的能力和技能。
2. 发送数学查询并打印完整的 JSON-RPC 响应，包含任务 ID、状态和智能体的答案。
3. 如果启用了轮询且任务未立即完成，则轮询直到任务达到终态。
