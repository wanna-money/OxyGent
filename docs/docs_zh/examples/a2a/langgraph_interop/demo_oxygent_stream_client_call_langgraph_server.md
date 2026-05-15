# OxyGent 流式客户端调用 LangGraph A2A 服务端

**源文件:** `examples/a2a/langgraph_interop/demo_oxygent_stream_client_call_langgraph_server.py`

## 概述

本示例使用 OxyGent 的 `A2AClientAgent` 以流式模式调用 LangGraph A2A 服务端。它使用 `message/stream` A2A 方法并消费来自服务端的 Server-Sent Events。这展示了 OxyGent 到 LangGraph 互操作的流式变体，是非流式示例的补充。

## 前置条件

- Python 3.10+
- 已安装 OxyGent（`pip install -r requirements.txt`）
- **必须先启动 LangGraph A2A 服务端：**
  ```bash
  PYTHONPATH=. python examples/a2a/langgraph_interop/demo_langgraph_a2a_server.py
  ```

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/langgraph_interop/demo_oxygent_stream_client_call_langgraph_server.py
```

## 代码详解

### 配置

- `SERVER_URL` 设为 `http://127.0.0.1:8102/a2a`。
- `CLIENT_NAME` 为 `"langgraph_stream_client"`，是此 agent 实例的 Oxy 名称。

### 组件

**`A2AClientAgent.minimal(...)`** -- 配置参数：
- `streaming=True` -- 使用 `message/stream` SSE 方法。
- `timeout=120` -- 更长的超时时间以适应流式传输。
- `enable_task_polling=False` -- 不需要，因为事件流本身会传递最终结果。

**`call_once(mas, query)`** -- 简化的辅助函数，构建 `OxyRequest` 并通过 MAS 执行。

### 入口

`main()` 协程：
1. 设置应用名称为 `"demo-oxygent-stream-client-call-langgraph-server"`。
2. 创建包含单个流式 `A2AClientAgent` 的 `oxy_space`。
3. 打开 `MAS` 上下文并发送一条查询，询问 LangGraph A2A 服务能力。
4. 打印最终聚合的响应和会话标识符。

## 核心概念

- **LangGraph 流式 A2A**：LangGraph 服务端的 `message/stream` 端点逐字符发送 SSE 事件，`A2AClientAgent` 消费并聚合这些事件。
- **最小代码变更**：与非流式 LangGraph 客户端相比，只有 `streaming=True` 和 `enable_task_polling=False` 不同 -- 其余 OxyGent 代码完全相同。
- **透明流式处理**：`A2AClientAgent` 在内部处理 SSE 解析，将最终结果以标准 `OxyResponse` 形式呈现。

## 预期行为

客户端发送查询并从 LangGraph 服务端接收流式响应。控制台显示：
- `[final]` -- 完整聚合的响应文本（如 `[LangGraph Server] <查询文本>`）。
- `session:` -- 来自流式会话的 `context_id` 和 `task_id`。

服务端逐字符发送部分更新，客户端将其聚合为最终输出。
