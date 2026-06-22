# 后端与基础设施示例

> 本目录包含展示 OxyGent 后端能力的示例，涵盖 MAS 启动模式、配置管理、并发控制、数据作用域、钩子、消息处理以及 Oxy 组件自定义等内容。

---

### 从 JSON 文件加载配置

**文件:** `examples/backend/demo_config.py`

本示例展示如何使用 `Config.load_from_json()` 从 JSON 文件加载配置。配置系统支持 `default` 基础配置与环境特定覆盖层（如 `dev`、`prod`）的合并，通过 `env` 参数进行选择。部署时，只需设置 `APP_ENV` 环境变量即可自动切换配置，无需修改代码。

**核心组件:** `Config`, `HttpLLM`, `ReActAgent`

**[详细文档 →](./demo_config.md)**

---

### MAS 启动模式

**文件:** `examples/backend/demo_launch_mas.py`

全面展示 MAS 实例的各种启动和交互方式。包括通过 `mas.call()` 直接调用 Oxy（按名称调用 Agent、工具和 LLM）、通过 `mas.chat_with_agent()` 使用高级入口、通过 `start_cli_mode()` 启动交互式 REPL、通过 `start_batch_processing()` 进行并发批量执行、通过 `start_web_service()` 启动 Web 服务，以及使用工厂方法 `MAS.create()` 在非上下文管理器场景下创建实例。

**核心组件:** `MAS`, `HttpLLM`, `StdioMCPClient`, `ReActAgent`

**[详细文档 →](./demo_launch_mas.md)**

---

### 带信号量的批量处理

**文件:** `examples/backend/demo_batch_and_semaphore.py`

演示如何通过并发控制进行批量处理。`HttpLLM` 和 `ChatAgent` 上的 `semaphore` 参数限制了并发执行数量，防止并行处理大量请求时资源耗尽。本示例中 LLM 并发限制为 4、Agent 并发限制为 6，同时通过 `start_batch_processing()` 分发 10 个查询。

**核心组件:** `HttpLLM(semaphore=4)`, `ChatAgent(semaphore=6)`

**[详细文档 →](./demo_batch_and_semaphore.md)**

---

### 添加自定义 FastAPI 路由

**文件:** `examples/backend/demo_add_router.py`

展示如何通过 `MAS(routers=[router])` 参数传入 `APIRouter` 实例，为 MAS Web 服务扩展自定义 FastAPI 端点。示例注册了一个返回 `WebResponse` 的 GET 端点（`/api_name`），并创建了一个 `WorkflowAgent`，该 Agent 在内部通过 `httpx` 调用此自定义端点，展示了 Agent 如何与同一服务器中的用户自定义 API 交互。

**核心组件:** `APIRouter`, `WorkflowAgent`, `WebResponse`

**[详细文档 →](./demo_add_router.md)**

---

### 发送附件

**文件:** `examples/backend/demo_attachment.py`

演示如何在用户查询中附带文件进行多模态处理。在 LLM 上设置 `is_multimodal_supported=True` 并在 payload 中包含 `attachments` 列表，文件（如 `README.md`）将与查询一起传递给模型。当底层 LLM 支持多模态内容时，此模式支持图片、文档及其他基于文件的输入。

**核心组件:** `HttpLLM(is_multimodal_supported)`, `ChatAgent`

**[详细文档 →](./demo_attachment.md)**

---

### 自定义共享数据 Schema

**文件:** `examples/backend/demo_custom_shared_data_schema.py`

说明如何通过 `Config.set_es_schema_shared_data()` 为 `shared_data` 定义自定义 Elasticsearch Schema，以及如何在 `func_process_input` 回调中填充共享数据字段。示例注册了包含 `user_pin` 和 `user_name` 关键字字段的 Schema，然后在 Agent 执行前通过 `oxy_request.set_shared_data()` 设置其值，使结构化元数据在整个请求生命周期中可用。

**核心组件:** `Config`, `HttpLLM`, `ReActAgent`

**[详细文档 →](./demo_custom_shared_data_schema.md)**

---

### 数据作用域

**文件:** `examples/backend/demo_data_scope.py`

解释 OxyGent 中三个数据作用域层级及其在 Agent 调用间的可见性。`shared_data` 作用于单个 trace，对被调用 Agent 及其子 Agent 可见；`group_data` 作用于会话组，在共享同一 `from_trace_id` 的 trace 间持久化；`global_data` 在整个 MAS 实例间共享。示例使用两个 ReActAgent（主 Agent 和子 Agent），通过 `func_process_input` 回调在每一步打印所有数据作用域以供检查。

**核心组件:** `HttpLLM`, `StdioMCPClient`, `ReActAgent` (x2)

**[详细文档 →](./demo_data_scope.md)**

---

### 全局数据

**文件:** `examples/backend/demo_global_data.py`

展示如何在自定义 `BaseAgent` 子类中读写 `global_data`。示例实现了一个 `CounterAgent`，在每次请求时递增存储在 `global_data` 中的调用计数器，演示了状态如何在同一 MAS 实例的多次调用间持久化。计数器通过 `oxy_request.get_global_data()` 访问，通过 `oxy_request.set_global_data()` 更新。

**核心组件:** `BaseAgent`（自定义子类）, `HttpLLM`

**[详细文档 →](./demo_global_data.md)**

---

### 日志配置

**文件:** `examples/backend/demo_logger_setup.py`

演示如何使用 `oxygent.log_setup` 中的 `setup_logging()` 工具函数在 OxyGent 应用中配置自定义日志。日志记录器在模块级别初始化，然后在 `func_process_input` 回调中用于记录到达 Agent 前的查询信息。此模式适用于添加结构化日志、调试请求流程或集成外部日志系统。

**核心组件:** `setup_logging`, `HttpLLM`, `ChatAgent`

**[详细文档 →](./demo_logger_setup.md)**

---

### MAS 级别钩子

**文件:** `examples/backend/demo_mas_hook.py`

演示两种 MAS 级别的请求拦截钩子机制。`func_filter` 接收传入的 payload 并可在处理前进行修改（例如注入带有用户标识的 `group_data`）。`func_interceptor` 同样接收 payload，但可以通过返回响应字典（例如 403 权限拒绝错误）来直接短路请求。两个钩子均作为参数传递给 `MAS` 构造函数。

**核心组件:** `HttpLLM`, `ChatAgent`

**[详细文档 →](./demo_mas_hook.md)**

---

### 控制消息存储与发送

**文件:** `examples/backend/demo_save_message.py`

展示如何使用 `_is_stored` 和 `_is_send` 标志精细控制出站消息的行为。通过 `oxy_request.send_message()` 发送消息时，`_is_stored` 控制消息是否持久化到数据库，`_is_send` 控制消息是否通过 SSE 推送到前端。示例演示了这两个标志的全部四种组合，以及通过 `Config.set_message_is_stored()` 和 `Config.set_message_is_show_in_terminal()` 设置的全局默认值。

**核心组件:** `HttpLLM(stream)`, `ChatAgent(func_process_input)`

**[详细文档 →](./demo_save_message.md)**

---

### 出站消息后处理

**文件:** `examples/backend/demo_process_message.py`

演示如何使用 MAS 上的 `func_process_message` 回调对所有出站消息进行后处理。该回调接收每条消息的字典和当前 `OxyRequest`，可在消息到达前端之前修改其内容。本示例中，每个流式 token 都被追加了一个短横线字符，展示了如何全局地转换、过滤或丰富消息内容。

**核心组件:** `HttpLLM(stream)`, `ChatAgent`

**[详细文档 →](./demo_process_message.md)**

---

### 人机协同

**文件:** `examples/backend/demo_human_in_the_loop.py`

使用 `WorkflowAgent` 实现人机协同模式。工作流函数向前端发送消息，然后通过 `oxy_request.get_feedback_stream()` 阻塞等待，异步接收用户通过 SSE 通道发来的反馈。前端可以向 `/feedback` 端点 POST 请求，携带匹配的 `channel_id`（默认为 `trace_id`）来回传数据。收集到的反馈将被汇总并作为工作流结果返回。

**核心组件:** `HttpLLM`, `WorkflowAgent(func_workflow)`

**[详细文档 →](./demo_human_in_the_loop.md)**

---

### 子类化 Oxy 组件

**文件:** `examples/backend/demo_rewrite_oxy.py`

展示如何继承 `oxy.HttpLLM` 并重写 `_execute` 方法以实现完全自定义的 HTTP 调用逻辑。`MyHttpLLM` 类自行构建请求 payload，通过 `httpx` 直接发送 POST 请求，解析响应 JSON 并返回 `OxyResponse`。当需要集成非标准 LLM API、添加自定义认证或实现专有的请求/响应转换时，此模式非常有用。

**核心组件:** `HttpLLM`（子类化）, `OxyResponse`

**[详细文档 →](./demo_rewrite_oxy.md)**
