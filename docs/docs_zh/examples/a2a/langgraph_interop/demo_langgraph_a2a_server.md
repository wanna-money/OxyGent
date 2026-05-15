# LangGraph A2A 服务端

**源文件:** `examples/a2a/langgraph_interop/demo_langgraph_a2a_server.py`

## 概述

本示例启动一个基于 LangGraph 的最小化 A2A 协议兼容服务端。它在端口 8102 上运行 FastAPI 应用，实现了核心 A2A JSON-RPC 方法（`message/send`、`message/stream`、`tasks/get`、`tasks/cancel`），并在 `.well-known/agent.json` 端点提供 Agent Card 发现服务。底层逻辑是一个编译后的 LangGraph `StateGraph`，包含一个节点，在输入前添加 `[LangGraph Server]` 前缀后回显。

## 前置条件

- Python 3.10+
- 额外依赖包：`pip install langgraph fastapi uvicorn sse-starlette`
- 无需 LLM API 密钥 -- 服务端使用确定性的回显图。

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/langgraph_interop/demo_langgraph_a2a_server.py
```

服务启动后监听地址为 `http://127.0.0.1:8102/a2a`。

## 代码详解

### 配置

| 常量 | 值 | 用途 |
|---|---|---|
| `APP_HOST` | `127.0.0.1` | 监听地址 |
| `APP_PORT` | `8102` | 监听端口 |
| `BASE_PATH` | `/a2a` | 所有 A2A 端点的根路径 |

内存中的 `TASKS` 字典用于存储已完成的任务，以便通过 `tasks/get` 检索。

### 组件

**`GraphState`** -- 一个 `TypedDict`，定义了 LangGraph 的状态模式，包含 `query` 和 `answer` 字段。

**`answer_node(state)`** -- 唯一的图节点。接受输入查询并返回状态，其中答案被设置为 `[LangGraph Server] <query>`。

**编译后的图** -- 一个 `StateGraph`，包含一个节点（`answer`）直接连接到 `END`。`builder.compile()` 调用生成可执行的图。这个最小化的图可以通过添加额外的节点、条件边和循环来扩展为更复杂的 agent 行为。

**辅助函数** -- `extract_text`、`build_message` 和 `build_task` 的作用与 LangChain 服务端示例相同：解析 A2A 消息负载并构造 A2A 兼容的响应对象。

**A2A 端点：**

| 方法 | 行为 |
|---|---|
| `message/send` | 同步调用图并返回已完成的任务。 |
| `message/stream` | 调用图后逐字符通过 SSE 事件发送答案。 |
| `tasks/get` | 通过 ID 检索先前完成的任务。 |
| `tasks/cancel` | 将任务标记为 `canceled`。 |

**Agent Card**（`GET /a2a/.well-known/agent.json`）-- 返回框架标签为 `langgraph` 的元数据、能力（流式传输、任务控制）和一个 `chat` 技能。

### 入口

`main()` 协程创建 Uvicorn 服务器配置并启动 FastAPI 应用。运行脚本时调用 `asyncio.run(main())`。

## 核心概念

- **LangGraph StateGraph**：一种有向图，节点对共享的类型化状态进行变换。本示例使用最简单的图（一个节点到 END），但该模式可扩展到具有循环和条件的多步推理。
- **A2A 协议兼容**：服务端遵循 A2A JSON-RPC 2.0 规范，使其可被任何框架的 A2A 客户端调用。
- **SSE 流式传输**：`message/stream` 方法通过 Server-Sent Events 模拟逐 token 的流式输出。
- **Agent Card**：`.well-known/agent.json` 端点允许 A2A 客户端自动发现服务。

## 预期行为

启动后，Uvicorn 日志确认正在监听 `127.0.0.1:8102`。可通过以下命令验证 Agent Card：

```bash
curl http://127.0.0.1:8102/a2a/.well-known/agent.json
```

`message/send` 请求返回一个已完成的任务，答案形如 `[LangGraph Server] <你的输入>`。该服务端设计为供本目录中的 OxyGent 客户端和 OxyGent 流式客户端示例调用。
