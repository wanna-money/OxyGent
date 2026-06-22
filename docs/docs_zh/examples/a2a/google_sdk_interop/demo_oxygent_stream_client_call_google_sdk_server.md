# OxyGent 流式客户端调用 Google A2A SDK 服务器

**源文件:** `examples/a2a/google_sdk_interop/demo_oxygent_stream_client_call_google_sdk_server.py`

## 概述

本示例演示 OxyGent 的流式 `A2AClientAgent` 连接到 Google A2A SDK 服务器。它通过流式端点发送消息并增量接收响应。此示例完成了互操作性矩阵，测试了 OxyGent 流式客户端对接非 OxyGent 流式服务器的场景。

## 前置条件

- 先启动 Google A2A SDK 服务器：`PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_google_sdk_a2a_server.py`
- 不需要 LLM 凭证（Google SDK 服务器返回回显响应）。

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_oxygent_stream_client_call_google_sdk_server.py
```

## 代码详解

### 配置

- `SERVER_URL = "http://127.0.0.1:8011"` -- Google A2A SDK 服务器端点。
- `CLIENT_NAME = "google_sdk_stream_client"` -- 智能体标识符。
- `Config.set_app_name("demo-oxygent-stream-client-call-google-sdk-server")` -- 应用名称用于追踪。

### 组件（`oxy_space`）

一个组件：

- **`A2AClientAgent.minimal()`**：
  - `name=CLIENT_NAME` -- 智能体标识符。
  - `server_url=SERVER_URL` -- Google SDK 服务器。
  - `streaming=True` -- 通过 `message/stream` 启用 SSE 流式传输。
  - `timeout=120` -- 更长的超时时间以适应流式传输。
  - `enable_task_polling=False` -- 不自动轮询。

### 辅助函数：`call_once`

最小化的请求构建器，创建 `OxyRequest` 并分发给流式客户端智能体。流式传输由 `A2AClientAgent` 内部处理。

### 入口

`main()` 协程：

1. 创建包含流式客户端智能体的 MAS。
2. 发送查询 "Please explain A2A in one short paragraph."。
3. 打印 `[final]` 前缀加上最终组装的响应。
4. 打印会话标识符。

## 核心概念

- **流式互操作性**：验证了 OxyGent 的流式客户端能正确处理来自非 OxyGent 服务器的 SSE 事件。Google SDK 服务器逐字符发出 `TaskStatusUpdateEvent` 数据块，OxyGent 客户端将它们累积为最终响应。
- **最小化客户端配置**：`.minimal()` 工厂方法仅需几个参数即可创建功能完整的流式客户端——不需要 LLM、智能体卡片或复杂配置。
- **互操作矩阵**：与其他互操作示例一起，完成了所有四种组合：OxyGent 客户端/服务器、OxyGent 客户端 + Google 服务器、Google 客户端 + OxyGent 服务器、Google 客户端/服务器。

## 预期行为

运行后（需先启动 Google SDK 服务器）：

1. `A2AClientAgent` 从 `http://127.0.0.1:8011/.well-known/agent.json` 解析智能体卡片。
2. 通过流式端点发送查询。
3. 从 Google SDK 服务器接收逐字符的 SSE 事件。
4. 打印 `[final]` 加上完整的回显响应：`"Google SDK stream reply: Please explain A2A in one short paragraph."`。
5. 打印会话标识符（`context_id` 和 `task_id`）。
