# OxyGent 流式客户端调用 LangChain A2A 服务端

**源文件:** `examples/a2a/langchain_interop/demo_oxygent_stream_client_call_langchain_server.py`

## 概述

本示例使用 OxyGent 的 `A2AClientAgent` 以流式模式调用 LangChain A2A 服务端。与非流式变体不同，本客户端使用 `message/stream` A2A 方法，并消费来自服务端的 Server-Sent Events（SSE）。它展示了 OxyGent 如何通过相同的 `A2AClientAgent` 接口透明地处理流式 A2A 响应。

## 前置条件

- Python 3.10+
- 已安装 OxyGent（`pip install -r requirements.txt`）
- **必须先启动 LangChain A2A 服务端：**
  ```bash
  PYTHONPATH=. python examples/a2a/langchain_interop/demo_langchain_a2a_server.py
  ```

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/langchain_interop/demo_oxygent_stream_client_call_langchain_server.py
```

## 代码详解

### 配置

- `SERVER_URL` 设为 `http://127.0.0.1:8101/a2a`。
- `CLIENT_NAME` 为 `"langchain_stream_client"`，是此 agent 实例的 Oxy 名称。

### 组件

**`A2AClientAgent.minimal(...)`** -- 配置参数：
- `streaming=True` -- 使用 `message/stream` SSE 方法替代 `message/send`。
- `timeout=120` -- 更长的超时时间以适应流式传输。
- `enable_task_polling=False` -- 不需要，因为事件流本身会传递最终结果。

**`call_once(mas, query)`** -- 简化的辅助函数（无多轮会话参数），构建 `OxyRequest` 并执行。

### 入口

`main()` 协程：
1. 设置应用名称为 `"demo-oxygent-stream-client-call-langchain-server"`。
2. 创建包含单个流式 `A2AClientAgent` 的 `oxy_space`。
3. 打开 `MAS` 上下文并发送一条查询，要求服务端描述其能力。
4. 打印最终聚合的响应和会话标识符。

## 核心概念

- **流式 A2A**：`message/stream` 方法以 SSE 事件形式逐步返回结果。`A2AClientAgent` 消费这些事件并将其聚合为最终的 `OxyResponse`。
- **相同接口，不同传输**：从非流式切换到流式只需设置 `streaming=True` -- 其余 OxyGent 代码保持不变。
- **无需任务轮询**：流式传输时，服务端通过事件流发送完整结果，因此不需要任务轮询。

## 预期行为

客户端发送查询并从 LangChain 服务端接收流式响应。控制台显示：
- `[final]` -- 完整聚合的响应文本（如 `[LangChain Server] <查询文本>`）。
- `session:` -- 来自流式会话的 `context_id` 和 `task_id`。

响应在 SSE 流完成后到达，服务端之前逐字符发送了部分更新。
