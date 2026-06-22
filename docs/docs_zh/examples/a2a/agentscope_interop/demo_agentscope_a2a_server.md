# AgentScope A2A 服务端

**源文件:** `examples/a2a/agentscope_interop/demo_agentscope_a2a_server.py`

## 概述

本示例使用 AgentScope 官方 A2A SDK 类型和 `A2AStarletteApplication` 构建器启动一个 A2A 协议兼容服务端。与 LangChain 和 LangGraph 服务端手动实现 JSON-RPC 端点不同，本服务端使用 `a2a` Python 包来处理协议细节。服务端实现了一个流式回显处理器，确认收到的输入后以固定响应逐字符通过 A2A `TaskStatusUpdateEvent` 事件发送。

## 前置条件

- Python 3.10+
- 额外依赖包：`pip install a2a agentscope uvicorn`
- 无需 LLM API 密钥 -- 服务端回显输入，不调用任何模型。

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/agentscope_interop/demo_agentscope_a2a_server.py
```

服务启动后监听地址为 `http://127.0.0.1:8003`。

## 代码详解

### 配置

| 常量 | 值 | 用途 |
|---|---|---|
| `HOST` | `0.0.0.0` | 监听地址（所有网络接口） |
| `PORT` | `8003` | 监听端口 |
| `BASE_URL` | `http://127.0.0.1:8003` | Agent Card 中发布的 URL |

### 组件

**`build_agent_card()`** -- 使用官方 `a2a.types` Pydantic 模型构造 `AgentCard`。声明了包括 `streaming=True` 和 `state_transition_history=True` 在内的能力，并注册了一个带有 AgentScope 相关标签的 `chat` 技能。

**`AgentScopeStreamHandler`** -- 核心处理器类。实现了 `on_message_send_stream` 方法，这是一个异步生成器，产出 A2A `Event` 对象：
1. **Working 事件** -- 产出状态为 `working` 的 `TaskStatusUpdateEvent`，表示处理已开始。
2. **流式内容** -- 构造一条确认用户输入的中文响应字符串，然后每个字符产出一个 `TaskStatusUpdateEvent`，其中的 `Message` 对象包含逐步增长的文本。
3. **Completed 事件** -- 产出状态为 `completed` 且 `final=True` 的最终 `TaskStatusUpdateEvent`。

**`A2AStarletteApplication`** -- `a2a` SDK 内置的应用构建器。接受 Agent Card 和处理器，`build()` 生成一个 Starlette ASGI 应用，预配置好所有 A2A 端点（Agent Card 发现、消息处理等）。

### 入口

`if __name__` 块配置日志并通过 Uvicorn 运行构建好的 Starlette 应用。

## 核心概念

- **A2A SDK（`a2a` 包）**：与 LangChain/LangGraph 示例中的手动 JSON-RPC 实现不同，本服务端使用官方 `a2a` Python SDK。SDK 自动处理协议兼容性、请求路由和响应格式化。
- **流处理器模式**：`on_message_send_stream` 异步生成器是主要的扩展点。每次 `yield` 都会向客户端发送一个 SSE 事件。
- **TaskStatusUpdateEvent**：A2A 事件类型，用于向客户端传达任务状态转换（`working` -> `completed`）和部分结果。
- **AgentScope 集成**：虽然本演示没有调用完整的 AgentScope `ReActAgent`（以避免模型依赖），但其结构反映了如何将 AgentScope agent 包装在 A2A 接口后面。

## 预期行为

启动后，服务端日志输出 `Starting AgentScope A2A server at 0.0.0.0:8003`。验证 Agent Card：

```bash
curl http://127.0.0.1:8003/.well-known/agent.json
```

当客户端发送消息时，服务端以流式状态更新序列响应，最终以已完成的任务结束。响应文本格式为："我是 AgentScope A2A 测试服务。我已收到你的问题：<输入>。这是一个流式演示回复。"
