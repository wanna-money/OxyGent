# MCP Tools 示例

演示如何通过 `StdioMCPClient` 将 MCP（Model Context Protocol）工具服务器集成到 OxyGent 智能体中。

---

## 示例

### 浏览器自动化示例

**文件:** `examples/mcp_tools/browser_demo.py`

本示例构建了一个将浏览器自动化与文件系统操作相结合的多智能体系统。一个主控 `ReActAgent` 协调两个专业子智能体：浏览器智能体配备了自定义浏览器 MCP 服务器（通过 `StdioMCPClient` 启动 `mcp_servers/browser/server.py`），用于网页导航、页面内容提取和自动登录处理；文件智能体配备了官方 `@modelcontextprotocol/server-filesystem` MCP 服务器，用于读写本地文件。该示例的默认任务是在线搜索天气信息并将提取结果保存到本地文本文件，展示了跨智能体任务委派机制，系统提示词中详细定义了上下文传递、错误处理和结果整合的规范。

**核心组件:**
- `HttpLLM` -- 通过环境变量配置的 LLM 后端
- `StdioMCPClient`（"browser_tools"）-- 启动自定义浏览器 MCP 服务器，用于网页抓取和自动化操作
- `StdioMCPClient`（"file_tools"）-- 启动官方文件系统 MCP 服务器，用于本地文件操作
- `ReActAgent`（"browser_agent"）-- 专门处理浏览器任务的智能体，包含登录检测逻辑
- `ReActAgent`（"file_agent"）-- 专门处理文件系统任务的智能体，包含输入验证
- `ReActAgent`（"master_agent"）-- 编排器，将任务委派给浏览器和文件子智能体
- `MAS` -- 启动 Web 服务 UI 的运行时容器

**[详细文档 →](./browser_demo.md)**

---

### 文本转语音（TTS）示例

**文件:** `examples/mcp_tools/tts_demo.py`

本示例演示了如何在 OxyGent 中使用自定义 TTS（文本转语音）MCP 服务器。它创建一个 `StdioMCPClient`，使用当前 Python 解释器启动 `mcp_servers/tts_tools.py` 服务器。TTS 智能体是一个 `ReActAgent`，能够通过 Microsoft Edge TTS 将文本转换为语音、停止音频播放以及列出可用语音。主要特性包括在 `tts_audio_cache/` 目录中自动缓存音频、对长文本进行智能分块处理，以及支持多种中英文语音选项。主控智能体负责将用户请求路由到 TTS 智能体。

**核心组件:**
- `HttpLLM` -- 用于智能体推理的 LLM 后端
- `StdioMCPClient`（"tts_tools"）-- 启动 TTS MCP 服务器，用于语音合成和播放
- `ReActAgent`（"tts_agent"）-- 使用 Edge TTS 语音处理文本转语音请求
- `ReActAgent`（"master_agent"）-- 将用户请求路由到 TTS 子智能体
- `MAS` -- 带有 Web 服务和欢迎消息的运行时容器

**[详细文档 →](./tts_demo.md)**

---

### 火车票查询示例

**文件:** `examples/mcp_tools/demo_train_ticket.py`

本示例展示了如何使用 `FunctionHub` 工具（从 `function_hubs/train_ticket_tools.py` 导入）配合 `ReActAgent` 构建中国铁路（12306）车票查询助手。FunctionHub 提供三个工具：`get_stations_of_city` 根据城市名查询车站代码，`get_tickets` 查询指定日期两站之间的可用车票，`get_current_date` 解析"明天"等相对日期。该智能体以 `trust_mode=False` 运行，即在执行前会验证工具调用。示例启动 Web 服务时附带中英双语欢迎消息，说明用户可以尝试的查询示例。

**核心组件:**
- `HttpLLM` -- 低温度参数的 LLM 后端，确保精确的工具调用
- `FunctionHub`（"train_ticket_tools"）-- Python 函数工具，提供 12306 车站查询、车票查询和日期解析功能
- `ReActAgent`（"train_ticket_agent"）-- 单一智能体，对火车票工具进行推理和调用
- `MAS` -- 启动 Web 服务并附带示例查询的运行时容器

**[详细文档 →](./demo_train_ticket.md)**
