# Tool 示例

本目录包含了 OxyGent 中注册和使用不同工具类型的示例，涵盖 FunctionHub 工具、MCP 协议工具以及预置的文档处理工具。

---

## 示例列表

### FunctionHub 工具

**文件:** `examples/tools/demo_functionhub.py`

演示了如何使用 FunctionHub 创建自定义工具并将其注册到 Agent。示例中定义了一个名为 `joke_tools` 的 `FunctionHub`，并通过 `@fh.tool()` 装饰器注册了一个 `joke_tool` 函数。该工具接受一个 `joke_type` 参数（使用 Pydantic `Field` 添加描述信息），并从硬编码的笑话列表中随机返回一条。FunctionHub 被传入 ReActAgent 的 `tools` 列表，使 Agent 在推理过程中能够发现并调用该工具。系统以 Web 服务方式启动，并以"请讲一个笑话"作为初始查询。

**核心组件:**
- `FunctionHub` -- 声明一组命名的函数式工具
- `@fh.tool()` 装饰器 -- 将异步函数注册为带描述的可调用工具
- `ReActAgent` -- 推理型 Agent，能够选择并调用已注册的工具
- `HttpLLM` -- 底层语言模型

**[详细文档 →](./demo_functionhub.md)**

---

### MCP 工具 (Stdio, SSE, Streamable)

**文件:** `examples/tools/demo_mcp.py`

展示了如何通过不同传输方式将外部 MCP（Model Context Protocol）工具服务器连接到 Agent。示例配置了三个 `StdioMCPClient` 实例：`time_tools`（通过 `uvx mcp-server-time` 启动）、`map_tools`（通过 `npx @amap/amap-maps-mcp-server` 启动，并配置了高德地图 API 密钥环境变量）和 `math_tools`（通过 `uv run` 指向本地 `math_tools.py` MCP 服务器启动）。注释代码块中还展示了 `SSEMCPClient` 和 `StreamableMCPClient`，分别用于 SSE 和 Streamable HTTP 传输方式。一个 ReActAgent 接入了时间和数学工具，并以"现在几点了"作为查询启动。

**核心组件:**
- `StdioMCPClient` -- 通过标准输入输出连接 MCP 服务器（基于子进程）
- `SSEMCPClient` -- 通过 Server-Sent Events 连接 MCP 服务器（注释示例）
- `StreamableMCPClient` -- 通过 Streamable HTTP 连接 MCP 服务器（注释示例）
- `ReActAgent` -- 能够发现并调用 MCP 工具的 Agent
- `HttpLLM` -- 底层语言模型

**[详细文档 →](./demo_mcp.md)**

---

### 带自定义 Headers 的 MCP 工具

**文件:** `examples/tools/demo_mcp_with_headers.py`

演示了使用 `StreamableMCPClient` 向 MCP 工具服务器传递 HTTP Headers 的三种机制，这对于身份验证和请求定制非常重要。示例定义了三种 `oxy_space` 配置：（1）通过 `headers` 参数直接在 `StreamableMCPClient` 上设置静态 Headers；（2）启用 `is_dynamic_headers=True` 后，从请求的 `shared_data["headers"]` 中动态读取 Headers；（3）启用 `is_inherit_headers=True` 后，透传前端 HTTP 请求的 Headers 到 MCP 服务器。当多个 Headers 来源同时存在时，优先级为：前端请求 Headers > shared_data 中的 Headers > 客户端静态 Headers。

**核心组件:**
- `StreamableMCPClient` -- 支持 Headers 自定义的 MCP 客户端
- `headers` -- 静态 Headers 配置
- `is_dynamic_headers` -- 启用从 shared_data 中动态获取 Headers
- `is_inherit_headers` -- 启用前端请求 Headers 的透传
- `ReActAgent` -- 使用已配置 MCP 工具的 Agent

**[详细文档 →](./demo_mcp_with_headers.md)**

---

### 文档处理工具

**文件:** `examples/tools/demo_document_tools.py`

一个综合性的示例，通过五个子示例展示了 OxyGent 预置文档处理工具的使用方式。（1）基础文档处理：使用 `detect_document_format` 识别 PDF/Word/Excel 文件的类型、大小和支持的操作。（2）文档处理 Agent：创建了一个配备 `preset_tools.document_tools` 和详细系统提示词的 ReActAgent，使其能够智能选择合适的工具处理各类文档操作。（3）批量处理：遍历目录中的所有文档，检测格式，提取元数据（如通过 `get_pdf_info` 获取 PDF 的页数和图片数），并生成 JSON 报告。（4）文档分析 Agent：一个高级 ReActAgent，结合 `document_tools` 和 `file_tools` 进行深度内容分析和报告生成。（5）直接 API 调用：打印示例代码片段，展示如何在不使用 Agent 的情况下直接从 Python 调用文档工具，涵盖 PDF 文本提取、PDF 信息获取、合并、拆分、Word 读取和 Excel 读取。

**核心组件:**
- `preset_tools.document_tools` -- 内置文档处理 FunctionHub（PDF、Word、Excel）
- `preset_tools.file_tools` -- 内置文件系统工具
- `detect_document_format` -- 识别文档类型及支持的操作
- `get_pdf_info` -- 提取 PDF 元数据和内容统计信息
- `ReActAgent` -- 用于智能文档处理的 Agent
- `HttpLLM` -- 底层语言模型

**[详细文档 →](./demo_document_tools.md)**
