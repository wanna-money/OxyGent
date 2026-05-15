# OxyGent 客户端调用 AgentScope A2A 服务端

**源文件:** `examples/a2a/agentscope_interop/demo_oxygent_client_call_agentscope_server.py`

## 概述

本示例使用 OxyGent 内置的 `A2AClientAgent` 调用远程 AgentScope A2A 服务端。它展示了流式 A2A 路径（`message/stream`）与 AgentScope 服务端基于 `TaskStatusUpdateEvent` 的流式处理器的配合。`A2AClientAgent` 自动发现 Agent Card、发送请求并将流式响应聚合为最终的 `OxyResponse`。

## 前置条件

- Python 3.10+
- 已安装 OxyGent（`pip install -r requirements.txt`）
- **必须先启动 AgentScope A2A 服务端：**
  ```bash
  PYTHONPATH=. python examples/a2a/agentscope_interop/demo_agentscope_a2a_server.py
  ```

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/agentscope_interop/demo_oxygent_client_call_agentscope_server.py
```

## 代码详解

### 配置

- `SERVER_URL` 设为 `http://127.0.0.1:8003`，与 AgentScope 服务端地址一致。
- `Config.set_app_name(...)` 设置应用标识用于日志记录。

### 组件

**`A2AClientAgent.minimal(...)`** -- 创建最小化的 A2A 客户端 agent，参数包括：
- `name="agentscope_client"` -- MAS 内部路由使用的 Oxy 名称。
- `server_url` -- AgentScope 服务端的基础 URL。Agent Card 路径（`.well-known/agent.json`）默认自动附加。
- `streaming=True` -- 使用 `message/stream` 方法，与 AgentScope 服务端的流处理器匹配。
- `timeout=120` -- 120 秒 HTTP 超时，适应流式传输。
- `enable_task_polling=False` -- 不需要，因为事件流本身传递最终结果。
- `task_poll_interval_seconds=1` 和 `task_poll_max_wait_seconds=30` -- 轮询参数（流式时未使用，但作为后备配置）。

**`call_once(mas, query, context_id, task_id)`** -- 辅助函数，构建指向 `agentscope_client` agent 的 `OxyRequest` 并执行。可选的 `context_id` 和 `task_id` 支持多轮会话。

### 入口

`main()` 协程：
1. 设置应用名称。
2. 创建包含单个流式 `A2AClientAgent` 的 `oxy_space`。
3. 通过异步上下文管理器打开 `MAS`。
4. 发送一条查询，要求 AgentScope 服务端用一句话介绍自己。
5. 打印响应输出和会话标识符（`context_id`、`task_id`）。

## 核心概念

- **A2AClientAgent 与 AgentScope 配合**：同一个 `A2AClientAgent` 类可以与任何 A2A 兼容服务端配合工作，无论它是用 LangChain、LangGraph、AgentScope 还是其他框架构建的。
- **自动 Agent Card 发现**：客户端从服务端 URL 获取 `.well-known/agent.json` 以在发送消息前了解其能力。
- **与 A2A SDK 服务端的流式交互**：AgentScope 服务端使用官方 `a2a` SDK 的 `A2AStarletteApplication`，其 SSE 流式处理方式与手动 FastAPI 实现不同 -- `A2AClientAgent` 透明地处理两种方式。
- **会话元数据**：响应包含 `context_id` 和 `task_id`，可用于多轮对话。

## 预期行为

客户端发送查询并从 AgentScope 服务端接收流式响应。控制台输出包括：
- `[turn1]` -- AgentScope 服务端聚合后的响应文本，格式为："我是 AgentScope A2A 测试服务。我已收到你的问题：<输入>。这是一个流式演示回复。"
- `session:` -- 会话的 `context_id` 和 `task_id`，可用于后续对话轮次。
