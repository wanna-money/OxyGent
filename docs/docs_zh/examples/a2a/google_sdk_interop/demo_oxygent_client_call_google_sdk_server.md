# OxyGent 客户端调用 Google A2A SDK 服务器

**源文件:** `examples/a2a/google_sdk_interop/demo_oxygent_client_call_google_sdk_server.py`

## 概述

本示例演示 OxyGent 的 `A2AClientAgent` 连接到使用 Google A2A SDK 构建的非 OxyGent A2A 服务器。它验证了 OxyGent 可以作为客户端连接到任何 A2A 兼容的服务器，而不仅仅是 OxyGent 服务器。示例还展示了如何传递自定义 HTTP 请求头用于认证或元数据。

## 前置条件

- 先启动 Google A2A SDK 服务器：`PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_google_sdk_a2a_server.py`
- 客户端和 Google SDK 服务器均不需要 LLM 凭证（服务器返回回显响应）。

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_oxygent_client_call_google_sdk_server.py
```

## 代码详解

### 配置

- `SERVER_URL = "http://127.0.0.1:8011"` -- Google A2A SDK 服务器端点。
- `CLIENT_NAME = "google_sdk_server_client"` -- 智能体在 MAS 中的名称。
- `DEMO_HEADERS` -- 随每个请求发送的自定义 HTTP 请求头：
  - `x-demo-client: "oxygent-a2a"` -- 标识客户端框架。
  - `x-demo-token` -- 从 `GOOGLE_A2A_DEMO_TOKEN` 环境变量读取，默认值为 `"demo-token"`。

### 组件（`oxy_space`）

一个组件：

- **`A2AClientAgent.minimal()`**：
  - `name=CLIENT_NAME` -- 智能体标识符。
  - `server_url=SERVER_URL` -- Google SDK 服务器端点。
  - `streaming=False` -- 同步消息发送。
  - `timeout=60` -- 请求超时时间。
  - `enable_task_polling=False` -- 不自动轮询。
  - `headers=DEMO_HEADERS` -- 附加到所有 HTTP 请求的自定义请求头。

### 自定义请求头

请求头通过两种方式传递：

1. **在智能体构造时**：`A2AClientAgent.minimal()` 中的 `headers=DEMO_HEADERS` -- 附加到每个发出的 HTTP 请求。
2. **通过 `shared_data` 按请求传递**：`OxyRequest` 中的 `shared_data={"_headers": DEMO_HEADERS}` -- 允许按请求覆盖请求头。

### 辅助函数：`call_once`

构造包含查询文本和 `shared_data` 中自定义请求头的 `OxyRequest`，然后分发给 A2A 客户端智能体。

### 入口

`main()` 协程：

1. 创建包含 A2A 客户端智能体的 MAS。
2. 打印请求头以供验证。
3. 发送查询 "Please introduce yourself in one short sentence."。
4. 打印响应文本和会话元数据。

## 核心概念

- **跨框架客户端**：OxyGent 的 `A2AClientAgent` 可以连接到任何 A2A 兼容的服务器，不仅限于 OxyGent 服务器。这验证了 A2A 协议的通用性。
- **自定义请求头**：`headers` 参数和 `shared_data["_headers"]` 提供了向服务器传递认证令牌、追踪请求头或其他元数据的机制。
- **无需 LLM**：由于 Google SDK 服务器返回回显响应，这个纯客户端示例不需要 LLM 配置。

## 预期行为

运行后（需先启动 Google SDK 服务器）：

1. 打印请求头字典。
2. 向 Google SDK 服务器发送查询。
3. 打印回显响应：`"Google SDK A2A server reply: I received your question: Please introduce yourself in one short sentence."`。
4. 打印会话标识符（`context_id` 和 `task_id`）。
