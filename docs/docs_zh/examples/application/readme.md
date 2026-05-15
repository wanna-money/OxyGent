# 应用示例

展示将 OxyGent 多种功能组合在单个多智能体系统中的完整应用示例。

---

## 示例

### 综合多智能体示例

**文件:** `examples/application/demo.py`

本示例是一个将 OxyGent 核心功能整合到一个多智能体应用中的综合演示。它结合了多种工具类型和智能体模式：三个 `StdioMCPClient` 实例分别提供时间查询（通过 `mcp-server-time`）、文件操作（通过 `@modelcontextprotocol/server-filesystem`）和数学运算（通过自定义 `mcp_servers/math_tools.py`）。一个内联 `FunctionHub` 定义了返回随机笑话的 `joke_tool`。一个 `ChatAgent`（"intent_agent"）使用内置的意图识别提示词。系统包含三个由主控 `ReActAgent` 协调的专业智能体：具有自定义输入预处理（`func_process_input`）和 `trust_mode=False` 的 `time_agent`，用于文件系统操作的 `file_agent`，以及运行自定义 `func_workflow` 函数的 `WorkflowAgent`（"math_agent"）。该工作流函数展示了 OxyGent 的高级 API，包括在智能体层和主控层访问短期记忆、通过 `send_message` 发送 SSE 消息、通过 `oxy_request.call()` 进行跨智能体调用、使用自定义参数直接调用 LLM，以及动态查询解析。主控智能体应用了自定义输出格式化函数（`func_format_output`），为响应添加 "Answer: " 前缀。

**核心组件:**
- `HttpLLM` -- 低温度参数的 LLM 后端，确保确定性行为
- `ChatAgent`（"intent_agent"）-- 使用内置 `INTENTION_PROMPT` 进行意图分类的智能体
- `FunctionHub` -- 内联工具集，包含演示 `@fh.tool` 装饰器模式的 `joke_tool`
- `StdioMCPClient`（"time_tools"）-- 用于时区感知时间查询的 MCP 客户端
- `StdioMCPClient`（"file_tools"）-- 用于本地文件系统操作的 MCP 客户端
- `StdioMCPClient`（"math_tools"）-- 用于数学计算（如计算圆周率）的 MCP 客户端
- `ReActAgent`（"master_agent"）-- 具有自定义 `func_format_output` 和子智能体委派能力的编排器
- `ReActAgent`（"time_agent"）-- 具有自定义 `func_process_input` 和非信任模式的时间查询智能体
- `ReActAgent`（"file_agent"）-- 文件操作智能体
- `WorkflowAgent`（"math_agent"）-- 具有自定义 `func_workflow` 的智能体，展示记忆访问、SSE 消息推送、跨智能体调用和直接 LLM 调用
- `MAS` -- 启动 Web 服务并附带圆周率计算查询的运行时容器

**[详细文档 →](./demo.md)**
