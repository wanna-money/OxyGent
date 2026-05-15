# A2A OxyGent 流式客户端

**源文件:** `examples/a2a/demo_a2a_oxygent_stream_client.py`

## 概述

本示例演示 OxyGent 的流式 A2A 客户端能力。它使用流式模式的 `A2AClientAgent` 向 A2A 服务器发送消息，并通过 Server-Sent Events（SSE）增量接收响应。流式传输完成后，还会获取最终的任务状态。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`（服务端需要）
- 先启动 A2A 服务器：`PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py`

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_stream_client.py
```

## 代码详解

### 配置

- `SERVER_URL = "http://127.0.0.1:8090/a2a"` -- A2A 服务器端点。
- `Config.set_app_name("demo-a2a-stream-client-agent")` -- 设置应用名称用于日志记录。

### 组件（`oxy_space`）

一个组件：

- **`A2AClientAgent.minimal()`**：
  - `name="stream_client"` -- 智能体标识符。
  - `server_url=SERVER_URL` -- 目标 A2A 服务器。
  - `streaming=True` -- 启用通过 `message/stream` 端点的 SSE 流式传输。
  - `timeout=120` -- 更长的超时时间以适应流式响应。
  - `enable_task_polling=False` -- 不进行自动后台轮询。

### 辅助函数：`call_once`

构造一个指向 `stream_client` 智能体的 `OxyRequest`，包含用户查询。流式行为由 `A2AClientAgent` 内部处理——调用方仍然 await 一个 `OxyResponse`，但智能体在内部处理 SSE 数据块并组装最终输出。

### 入口

`main()` 协程：

1. 创建包含流式客户端智能体的 MAS。
2. 发送查询，要求讲一个100字的故事。
3. 打印最终组装的响应和会话元数据。
4. 通过 `get_task` 获取并打印完整的任务 JSON。

## 核心概念

- **流式与非流式**：当 `streaming=True` 时，`A2AClientAgent` 使用 A2A `message/stream` 端点，通过 SSE 接收增量的 `TaskStatusUpdateEvent` 和 `TaskArtifactUpdateEvent` 数据块。智能体在内部将这些数据块累积为最终响应。
- **超时设置**：流式响应可能比同步响应耗时更长，因此超时设为 120 秒而非 60 秒。
- **任务获取**：即使流式传输完成后，仍可使用 `get_task` 从服务器获取最终确定的任务状态。

## 预期行为

运行后（需先启动服务器）：

1. 通过流式端点向 A2A 服务器发送查询。
2. `A2AClientAgent` 在内部接收 SSE 数据块并组装响应。
3. 打印 `[final]` 加上完整的响应文本（一个短故事）。
4. 打印会话标识符（`context_id` 和 `task_id`）。
5. 获取并打印显示 `completed` 状态的完整任务 JSON。
