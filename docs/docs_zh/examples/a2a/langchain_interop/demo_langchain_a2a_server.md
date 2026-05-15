# LangChain A2A 服务端

**源文件:** `examples/a2a/langchain_interop/demo_langchain_a2a_server.py`

## 概述

本示例启动一个基于 LangChain 的最小化 A2A 协议兼容服务端。它在端口 8101 上运行 FastAPI 应用，实现了核心 A2A JSON-RPC 方法（`message/send`、`message/stream`、`tasks/get`、`tasks/cancel`），并在 `.well-known/agent.json` 端点提供 Agent Card 发现服务。底层逻辑是一个简单的 `RunnableLambda` 链，会在输入前添加 `[LangChain Server]` 前缀后回显。

## 前置条件

- Python 3.10+
- 额外依赖包：`pip install langchain-core fastapi uvicorn sse-starlette`
- 无需 LLM API 密钥 -- 服务端使用确定性的回显链。

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/langchain_interop/demo_langchain_a2a_server.py
```

服务启动后监听地址为 `http://127.0.0.1:8101/a2a`。

## 代码详解

### 配置

| 常量 | 值 | 用途 |
|---|---|---|
| `APP_HOST` | `127.0.0.1` | 监听地址 |
| `APP_PORT` | `8101` | 监听端口 |
| `BASE_PATH` | `/a2a` | 所有 A2A 端点的根路径 |

内存中的 `TASKS` 字典用于存储已完成的任务，以便后续通过 `tasks/get` 检索。

### 组件

**`chain`** -- 一个 LangChain `RunnableLambda`，在任何输入字符串前添加 `[LangChain Server]`。它代表了 agent 逻辑，可替换为任意 LangChain 链或 agent。

**`extract_text(payload)`** -- 从 A2A `params` 字典中解析用户文本，优先从嵌套的 `message.parts` 结构中提取，回退到顶层的 `query` 或 `text` 字段。

**`build_message(text, task_id, context_id)`** -- 构造角色为 `agent` 的 A2A `message` 事件。

**`build_task(text, task_id, context_id)`** -- 将消息包装为完整的 A2A `task` 对象，状态设为 `completed`，并包含一个含答案的 artifact。

**A2A 端点：**

| 方法 | 行为 |
|---|---|
| `message/send` | 同步调用链并返回已完成的任务。 |
| `message/stream` | 调用链后逐字符通过 SSE 事件发送答案（模拟流式输出）。 |
| `tasks/get` | 通过 ID 检索先前完成的任务。 |
| `tasks/cancel` | 将任务标记为 `canceled`。 |

**Agent Card**（`GET /a2a/.well-known/agent.json`）-- 返回服务端的元数据，包括名称、能力（流式传输、任务控制）及一个 `chat` 技能。

### 入口

`main()` 协程创建 Uvicorn 服务器配置并启动 FastAPI 应用。直接运行脚本时调用 `asyncio.run(main())`。

## 核心概念

- **A2A 协议**：服务端实现了 Google 的 Agent-to-Agent 协议（基于 JSON-RPC 2.0），实现跨框架的 agent 互操作。
- **Agent Card 发现**：客户端通过获取 `/.well-known/agent.json` 来发现服务端的能力。
- **RunnableLambda**：LangChain 最简单的原语 -- 将普通 Python 函数包装为可运行对象。替换为真正的 LangChain 链即可构建生产级 agent。
- **SSE 流式传输**：`message/stream` 方法返回 `EventSourceResponse`，以 Server-Sent Events 形式发送部分结果。

## 预期行为

启动服务后，你应该看到 Uvicorn 日志确认正在监听 `127.0.0.1:8101`。可通过以下命令验证 Agent Card：

```bash
curl http://127.0.0.1:8101/a2a/.well-known/agent.json
```

发送 `message/send` 请求将返回包含已完成任务的 JSON-RPC 响应，答案形如 `[LangChain Server] <你的输入>`。该服务端设计为供本目录中的 OxyGent 客户端或 OxyGent 流式客户端示例调用。
