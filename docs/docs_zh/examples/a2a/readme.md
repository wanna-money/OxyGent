# A2A 协议示例

本目录包含 OxyGent 的 Agent-to-Agent (A2A) 协议示例，涵盖 OxyGent 原生通信以及与 Google A2A SDK、LangChain、LangGraph、AgentScope 等框架的跨框架互操作。

---

## OxyGent 原生 A2A

### A2A 服务端

**文件:** `examples/a2a/demo_a2a_oxygent_server.py`

启动一个内置 A2A 服务的 OxyGent MAS 实例。服务端注册一个由 `HttpLLM` 驱动的 `ChatAgent` 作为主代理，并在可配置的路径（`/a2a`）上暴露 A2A 端点。关键配置是在 `MAS` 构造函数中传入 `enable_a2a_server=True` 和 `a2a_base_path` 参数，系统会自动将 A2A 协议路由（包括 `.well-known/agent.json` 代理卡片端点）挂载到 FastAPI 服务上。该服务端是本目录下大多数客户端示例的前置依赖。

**核心组件:**
- `HttpLLM` -- 代理使用的 LLM 后端
- `ChatAgent` -- 处理传入 A2A 请求的主代理
- `MAS` -- 启用 `enable_a2a_server=True` 的运行时容器

**[详细文档 →](./demo_a2a_oxygent_server.md)**

---

### A2A 客户端（非流式）

**文件:** `examples/a2a/demo_a2a_oxygent_client.py`

演示使用 `A2AClientAgent` 以非流式模式调用 OxyGent A2A 服务端。客户端通过 `A2AClientAgent.minimal()` 工厂方法创建，设置 `streaming=False`。发送查询后，从响应中提取 `task_id`，并使用 `client.get_task()` 获取完整的任务对象，演示了 A2A 协议的 `message/send` 和 `tasks/get` 两种方法。示例还展示了如何从响应的 `extra` 字典中获取 `context_id` 和 `task_id`。

**核心组件:**
- `A2AClientAgent.minimal()` -- 轻量级 A2A 客户端代理工厂
- `MAS` -- 客户端代理的运行时容器
- `OxyRequest` -- 携带查询参数的请求对象

**[详细文档 →](./demo_a2a_oxygent_client.md)**

---

### A2A 客户端（流式）

**文件:** `examples/a2a/demo_a2a_oxygent_stream_client.py`

展示如何在 `minimal()` 工厂中设置 `streaming=True` 来使用 `A2AClientAgent` 的流式模式。客户端发送查询后，通过 A2A 协议的 `message/stream` 方法接收响应，实现增量 token 传输。流结束后，使用 `get_task()` 获取完整任务并打印最终输出及会话元数据（`context_id`、`task_id`）。

**核心组件:**
- `A2AClientAgent.minimal()` -- 设置 `streaming=True`
- `MAS` -- 运行时容器
- `OxyRequest` -- 携带查询参数的请求对象

**[详细文档 →](./demo_a2a_oxygent_stream_client.md)**

---

### A2A 任务跟进客户端

**文件:** `examples/a2a/demo_a2a_oxygent_task_followup_client.py`

通过 `context_id` 和 `reference_task_ids` 验证 A2A 协议的多轮对话连续性。客户端发送初始查询后，捕获返回的 `context_id` 和 `task_id`，然后发送后续查询，通过 `reference_task_ids` 引用首轮任务。这演示了 A2A 协议对有状态多轮对话的支持，服务端可以利用先前的任务上下文。客户端同时启用了 `enable_task_polling=True` 以支持异步任务完成模式。

**核心组件:**
- `A2AClientAgent.minimal()` -- 设置 `enable_task_polling=True`
- `context_id` / `reference_task_ids` -- A2A 会话连续性字段
- `MAS`、`OxyRequest` -- 标准 OxyGent 运行时和请求类型

**[详细文档 →](./demo_a2a_oxygent_task_followup_client.md)**

---

## Google A2A SDK 互操作

### Google SDK A2A 服务端

**文件:** `examples/a2a/google_sdk_interop/demo_google_sdk_a2a_server.py`

使用官方 Google A2A SDK（`a2a` 包）实现一个独立的 A2A 服务端。服务端定义了具有流式能力的 `AgentCard`，以及一个 `SimpleA2AHandler` 类，该类同时处理 `on_message_send`（同步）和 `on_message_send_stream`（通过逐字符 `TaskStatusUpdateEvent` 发送的流式响应）。应用使用 `A2AStarletteApplication` 构建并通过 uvicorn 启动。该服务端用于测试 OxyGent 客户端与 Google SDK 服务端的互操作。

**核心组件:**
- `A2AStarletteApplication` -- Google SDK 基于 Starlette 的 A2A 应用构建器
- `AgentCard` / `AgentSkill` -- A2A 代理元数据定义
- `SimpleA2AHandler` -- 实现 `on_message_send` 和 `on_message_send_stream`
- `TaskStatusUpdateEvent` -- 流式状态更新与部分消息

**[详细文档 →](./google_sdk_interop/demo_google_sdk_a2a_server.md)**

---

### Google SDK 客户端调用 OxyGent 服务端（非流式）

**文件:** `examples/a2a/google_sdk_interop/demo_a2a_sdk_call_oxygent.py`

使用 Google A2A SDK 的 `A2AClient` 和 `A2ACardResolver` 调用 OxyGent A2A 服务端。客户端从服务端的 `.well-known/agent.json` 端点解析代理卡片，然后使用 SDK 的类型化请求/响应模型发送 `SendMessageRequest`。示例还包含一个 `poll_task()` 工具函数，可重复调用 `tasks/get` 直到任务达到终态（completed、failed、canceled 或 rejected）。这证明了 OxyGent 的 A2A 服务端完全兼容标准 Google A2A SDK 客户端。

**核心组件:**
- `A2ACardResolver` -- 从服务端 URL 解析代理卡片
- `A2AClient` -- Google SDK 的 A2A 客户端
- `SendMessageRequest` / `MessageSendParams` -- 类型化 A2A 请求模型
- `poll_task()` -- 带超时的任务轮询工具

**[详细文档 →](./google_sdk_interop/demo_a2a_sdk_call_oxygent.md)**

---

### Google SDK 客户端调用 OxyGent 服务端（流式）

**文件:** `examples/a2a/google_sdk_interop/demo_a2a_sdk_stream_call_oxygent.py`

通过 Google A2A SDK 的 `send_message_streaming()` 方法对 OxyGent A2A 服务端进行流式互操作演示。客户端解析代理卡片，发送 `SendStreamingMessageRequest`，并迭代处理流式数据块。`extract_text()` 辅助函数处理多种结果类型（`Message`、`Task`、`TaskStatusUpdateEvent`、`TaskArtifactUpdateEvent`）以提取文本内容，并计算增量用于逐步显示。这验证了 OxyGent 的流式 A2A 响应能被标准 SDK 客户端正确消费。

**核心组件:**
- `A2AClient.send_message_streaming()` -- SDK 流式方法
- `SendStreamingMessageRequest` -- 类型化流式请求
- `extract_text()` -- 多类型文本提取辅助函数

**[详细文档 →](./google_sdk_interop/demo_a2a_sdk_stream_call_oxygent.md)**

---

### OxyGent 客户端调用 Google SDK 服务端（非流式）

**文件:** `examples/a2a/google_sdk_interop/demo_oxygent_client_call_google_sdk_server.py`

使用 OxyGent 的 `A2AClientAgent` 以非流式模式调用 Google A2A SDK 服务端。示例还演示了如何通过 `A2AClientAgent.minimal()` 的 `headers` 参数和 `OxyRequest` 的 `shared_data["_headers"]` 字段向 A2A 客户端传递自定义 HTTP 头（如认证令牌）。这适用于远程 A2A 服务端需要身份验证或自定义请求元数据的场景。

**核心组件:**
- `A2AClientAgent.minimal()` -- 带自定义 `headers` 参数
- `OxyRequest.shared_data["_headers"]` -- 按请求注入头信息
- `MAS` -- 运行时容器

**[详细文档 →](./google_sdk_interop/demo_oxygent_client_call_google_sdk_server.md)**

---

### OxyGent 客户端调用 Google SDK 服务端（流式）

**文件:** `examples/a2a/google_sdk_interop/demo_oxygent_stream_client_call_google_sdk_server.py`

使用 OxyGent 的 `A2AClientAgent` 流式模式（`streaming=True`）调用 Google A2A SDK 服务端。客户端接收流式响应并打印最终聚合输出及会话标识符。这是上述非流式 Google SDK 互操作示例的流式对应版本，验证了 OxyGent 客户端与 Google SDK 服务端之间的双向流式兼容性。

**核心组件:**
- `A2AClientAgent.minimal()` -- 设置 `streaming=True`
- `MAS`、`OxyRequest` -- 标准 OxyGent 运行时类型

**[详细文档 →](./google_sdk_interop/demo_oxygent_stream_client_call_google_sdk_server.md)**

---

## LangChain 互操作

### LangChain A2A 服务端

**文件:** `examples/a2a/langchain_interop/demo_langchain_a2a_server.py`

实现一个由 LangChain 驱动的 A2A 兼容服务端。服务端使用 `RunnableLambda` 链作为处理后端，通过 FastAPI 暴露一个 JSON-RPC 风格的统一端点，处理 `message/send`、`message/stream`、`tasks/get` 和 `tasks/cancel` 方法。`message/stream` 路径返回 `EventSourceResponse`（SSE），逐字符发送增量更新。内存中的 `TASKS` 字典存储已完成的任务供检索。代理卡片通过 `/.well-known/agent.json` 端点提供。

**核心组件:**
- `RunnableLambda` -- LangChain 的最小可运行单元，用于文本处理
- `FastAPI` + `EventSourceResponse` -- 基于 SSE 的流式端点
- JSON-RPC 调度 -- `message/send`、`message/stream`、`tasks/get`、`tasks/cancel`

**[详细文档 →](./langchain_interop/demo_langchain_a2a_server.md)**

---

### LangChain 客户端调用 OxyGent 服务端

**文件:** `examples/a2a/langchain_interop/demo_langchain_client_call_oxygent_server.py`

演示从 LangChain 风格代码调用 OxyGent A2A 服务端。一个 `RunnableLambda` 预处理用户查询（添加框架标签前缀），客户端通过 `httpx.AsyncClient` 向 OxyGent 服务端发送 JSON-RPC `message/send` 请求。后处理 `RunnableLambda` 清理响应文本。这展示了如何使用标准 HTTP 调用将 OxyGent A2A 端点集成到现有 LangChain 管道中。

**核心组件:**
- `RunnableLambda` -- 预处理/后处理包装器
- `httpx.AsyncClient` -- 直接向 OxyGent 服务端发送 HTTP JSON-RPC 调用
- A2A JSON-RPC 协议 -- `message/send` 方法

**[详细文档 →](./langchain_interop/demo_langchain_client_call_oxygent_server.md)**

---

### OxyGent 客户端调用 LangChain 服务端（非流式）

**文件:** `examples/a2a/langchain_interop/demo_oxygent_client_call_langchain_server.py`

使用 OxyGent 的 `A2AClientAgent`（设置 `enable_task_polling=True`）以非流式模式调用 LangChain A2A 服务端。发送查询后打印代理响应和会话标识符。这证明了 OxyGent 的 A2A 客户端可以无缝地与任何实现了 A2A 协议的第三方服务端通信，无论其底层框架如何。

**核心组件:**
- `A2AClientAgent.minimal()` -- 设置 `enable_task_polling=True`
- `MAS`、`OxyRequest` -- 标准 OxyGent 运行时类型

**[详细文档 →](./langchain_interop/demo_oxygent_client_call_langchain_server.md)**

---

### OxyGent 客户端调用 LangChain 服务端（流式）

**文件:** `examples/a2a/langchain_interop/demo_oxygent_stream_client_call_langchain_server.py`

使用 OxyGent 的 `A2AClientAgent` 流式模式调用 LangChain A2A 服务端。客户端通过 `message/stream` 协议方法接收增量流式响应，并打印最终聚合输出。这是上述非流式 LangChain 互操作客户端示例的流式对应版本。

**核心组件:**
- `A2AClientAgent.minimal()` -- 设置 `streaming=True`
- `MAS`、`OxyRequest` -- 标准 OxyGent 运行时类型

**[详细文档 →](./langchain_interop/demo_oxygent_stream_client_call_langchain_server.md)**

---

## LangGraph 互操作

### LangGraph A2A 服务端

**文件:** `examples/a2a/langgraph_interop/demo_langgraph_a2a_server.py`

实现一个由 LangGraph 驱动的 A2A 兼容服务端。服务端定义了一个包含单个 `answer_node` 的 `StateGraph`，用于处理查询并生成响应。与 LangChain 服务端类似，它通过 FastAPI 统一端点处理 `message/send`、`message/stream`、`tasks/get` 和 `tasks/cancel` 的 JSON-RPC 调度。`message/stream` 路径提供基于 SSE 的逐字符流式传输。图状态使用 `TypedDict`（`GraphState`）定义，包含 `query` 和 `answer` 字段。

**核心组件:**
- `StateGraph` / `GraphState` -- LangGraph 基于状态的计算图
- `FastAPI` + `EventSourceResponse` -- SSE 流式端点
- JSON-RPC 调度 -- `message/send`、`message/stream`、`tasks/get`、`tasks/cancel`

**[详细文档 →](./langgraph_interop/demo_langgraph_a2a_server.md)**

---

### LangGraph 客户端调用 OxyGent 服务端

**文件:** `examples/a2a/langgraph_interop/demo_langgraph_client_call_oxygent_server.py`

演示在 LangGraph 图内调用 OxyGent A2A 服务端。一个 `StateGraph` 将 A2A 调用封装在 `call_node` 中，该节点通过 `httpx.AsyncClient` 向 OxyGent 服务端发送 JSON-RPC `message/send` 请求，并将响应解析到图状态中（提取 `context_id`、`task_id` 和回答文本）。图通过 `graph.ainvoke()` 异步调用。这展示了如何将 OxyGent A2A 端点作为节点集成到 LangGraph 工作流中。

**核心组件:**
- `StateGraph` / `GraphState` -- 带类型化状态的 LangGraph 计算图
- `call_node` -- 封装 A2A HTTP 调用的异步图节点
- `httpx.AsyncClient` -- 直接向 OxyGent 服务端发送 JSON-RPC 调用

**[详细文档 →](./langgraph_interop/demo_langgraph_client_call_oxygent_server.md)**

---

### OxyGent 客户端调用 LangGraph 服务端（非流式）

**文件:** `examples/a2a/langgraph_interop/demo_oxygent_client_call_langgraph_server.py`

使用 OxyGent 的 `A2AClientAgent`（设置 `enable_task_polling=True`）调用 LangGraph A2A 服务端。此示例执行两轮对话：第一次调用发送查询，第二次调用引用第一轮的 `context_id` 和 `task_id` 来继续对话。这演示了 OxyGent 与 LangGraph 服务端通信时的多轮会话连续性。

**核心组件:**
- `A2AClientAgent.minimal()` -- 设置 `enable_task_polling=True`
- `context_id` / `task_id` -- 多轮会话跟踪
- `MAS`、`OxyRequest` -- 标准 OxyGent 运行时类型

**[详细文档 →](./langgraph_interop/demo_oxygent_client_call_langgraph_server.md)**

---

### OxyGent 客户端调用 LangGraph 服务端（流式）

**文件:** `examples/a2a/langgraph_interop/demo_oxygent_stream_client_call_langgraph_server.py`

使用 OxyGent 的 `A2AClientAgent` 流式模式调用 LangGraph A2A 服务端。客户端接收增量流式响应并打印最终聚合输出及会话元数据。这是上述非流式 LangGraph 互操作客户端示例的流式对应版本。

**核心组件:**
- `A2AClientAgent.minimal()` -- 设置 `streaming=True`
- `MAS`、`OxyRequest` -- 标准 OxyGent 运行时类型

**[详细文档 →](./langgraph_interop/demo_oxygent_stream_client_call_langgraph_server.md)**

---

## AgentScope 互操作

### AgentScope A2A 服务端

**文件:** `examples/a2a/agentscope_interop/demo_agentscope_a2a_server.py`

使用 Google A2A SDK 实现一个 AgentScope 风格的 A2A 服务端。`AgentScopeStreamHandler` 类实现了 `on_message_send_stream`，通过 `TaskStatusUpdateEvent` 逐字符发送流式响应来回显接收到的消息。服务端使用 `A2AStarletteApplication` 构建，其 `AgentCard` 声明了流式传输和状态转换历史功能。该处理器故意不依赖外部模型，使其成为一个自包含的互操作测试目标。

**核心组件:**
- `A2AStarletteApplication` -- Google SDK 基于 Starlette 的 A2A 应用构建器
- `AgentScopeStreamHandler` -- 实现 `on_message_send_stream` 的流式处理器
- `AgentCard` / `AgentSkill` -- A2A 代理元数据
- `TaskStatusUpdateEvent` -- 增量流式状态更新

**[详细文档 →](./agentscope_interop/demo_agentscope_a2a_server.md)**

---

### AgentScope 客户端调用 OxyGent 服务端

**文件:** `examples/a2a/agentscope_interop/demo_agentscope_client_call_oxygent_server.py`

使用 AgentScope 原生的 `A2AAgent` 类调用 OxyGent A2A 服务端。客户端构造一个指向 OxyGent 服务端 URL 的 `AgentCard`，创建 `A2AAgent` 实例，并使用 AgentScope 的 `Msg` 类发送消息。代理卡片的能力声明中显式禁用了流式传输（`streaming=False`），以避免 AgentScope 演示运行时中的异步流关闭竞态条件。这证明了 OxyGent 的 A2A 服务端兼容 AgentScope 的原生 A2A 客户端。

**核心组件:**
- `A2AAgent` -- AgentScope 内置的 A2A 客户端代理
- `AgentCard` -- 指向 OxyGent 服务端，设置 `streaming=False`
- `Msg` -- AgentScope 的消息类型

**[详细文档 →](./agentscope_interop/demo_agentscope_client_call_oxygent_server.md)**

---

### OxyGent 客户端调用 AgentScope 服务端

**文件:** `examples/a2a/agentscope_interop/demo_oxygent_client_call_agentscope_server.py`

使用 OxyGent 的 `A2AClientAgent` 流式模式调用 AgentScope A2A 服务端。客户端配置为 `streaming=True`，并包含任务轮询参数（`task_poll_interval_seconds`、`task_poll_max_wait_seconds`）以提供灵活性。发送查询后打印响应和会话元数据。这演示了 OxyGent 消费来自 AgentScope 服务端的流式 A2A 响应的能力。

**核心组件:**
- `A2AClientAgent.minimal()` -- 设置 `streaming=True` 及轮询参数
- `MAS`、`OxyRequest` -- 标准 OxyGent 运行时类型

**[详细文档 →](./agentscope_interop/demo_oxygent_client_call_agentscope_server.md)**
