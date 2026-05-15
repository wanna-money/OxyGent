# 多代理应用：自定义工作流、MCP 工具与钩子函数

**源文件:** `examples/application/demo.py`

## 概述

这是一个综合示例，在单个应用中展示了 OxyGent 的多项核心功能：MCP 工具客户端（时间、文件系统、数学）、自定义 `FunctionHub` 工具、带有编程式工作流函数的 `WorkflowAgent`、输入/输出钩子函数，以及主 `ReActAgent` 协调多个子代理。本示例展示了如何构建包含工具调用、代理间通信和消息格式化的实际多代理系统。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包
- Node.js 和 `npx`（用于文件系统 MCP 服务器）
- `uvx`（用于时间 MCP 服务器：`mcp-server-time`）
- `uv`（用于数学 MCP 服务器 `./mcp_servers/math_tools.py`）
- `./local_file` 目录，供文件系统 MCP 工具操作

## 运行方式

```bash
python -m examples.application.demo
```

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
```

设置全局默认 LLM 模型名称。

### 自定义 FunctionHub 工具

```python
fh = oxy.FunctionHub(name="joke_tools")

@fh.tool(description="a tool for telling jokes")
async def joke_tool(joke_type: str = Field(description="The type of the jokes")):
    ...
```

定义了一个简单的笑话工具，从硬编码列表中随机返回一个笑话。展示了如何使用 `pydantic.Field` 注册带类型标注和参数描述的异步函数。

### 钩子函数

#### `update_query(oxy_request: OxyRequest) -> OxyRequest`

附加到 `time_agent` 的**输入预处理钩子**（`func_process_input`）。在代理执行前，该函数：

1. 记录共享数据和用户查询（主代理级和当前级）。
2. 将被调用者名称注入到请求参数中（`oxy_request.arguments["who"]`）。
3. 返回修改后的请求。

#### `format_output(oxy_response: OxyResponse) -> OxyResponse`

附加到 `master_agent` 的**输出后处理钩子**（`func_format_output`）。在主代理生成响应后，该函数为输出添加 `"Answer: "` 前缀。

### 工作流函数

```python
async def workflow(oxy_request: OxyRequest):
```

通过 `func_workflow` 附加到 `math_agent` 的自定义工作流函数。这是 `WorkflowAgent` 的核心 -- 代理不使用 ReAct 循环，而是直接执行此函数。工作流内容：

1. **获取对话历史** -- `get_short_memory()` 获取代理级历史，`get_short_memory(master_level=True)` 获取用户级历史。
2. **发送自定义 SSE 消息** -- `send_message()` 向前端推送消息。
3. **调用其他代理** -- `oxy_request.call(callee="time_agent", ...)` 展示代理间通信。
4. **直接调用 LLM** -- `oxy_request.call(callee="default_llm", ...)` 使用自定义参数向 LLM 发送原始消息。
5. **条件工具调用** -- 从用户查询中提取数字。如果找到数字，调用 `calc_pi` 工具（来自 `math_tools`）计算圆周率到指定小数位；否则返回默认响应。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `temperature=0.01`，`semaphore=4` |
| `intent_agent` | `ChatAgent` | 使用 `INTENTION_PROMPT` 进行意图分类 |
| `joke_tools` | `FunctionHub` | 自定义笑话工具 |
| `time_tools` | `StdioMCPClient` | `mcp-server-time`，时区为 `Asia/Shanghai` |
| `file_tools` | `StdioMCPClient` | `@modelcontextprotocol/server-filesystem`，操作 `./local_file` 目录 |
| `math_tools` | `StdioMCPClient` | 本地 `./mcp_servers/math_tools.py`，通过 `uv run` 运行 |
| `master_agent` | `ReActAgent` | `is_master=True`，`sub_agents=[time, file, math]`，`func_format_output`，`timeout=100` |
| `time_agent` | `ReActAgent` | `tools=["time_tools"]`，`func_process_input=update_query`，`trust_mode=False`，`timeout=10` |
| `file_agent` | `ReActAgent` | `tools=["file_tools"]` |
| `math_agent` | `WorkflowAgent` | `func_workflow=workflow`，`sub_agents=["time_agent"]`，`tools=["math_tools"]`，`is_retain_master_short_memory=True` |

### 入口函数

```python
await mas.start_web_service(
    first_query="Please calculate the 20 positions of Pi",
    welcome_message="Hi, I'm OxyGent. How can I assist you?",
)
```

使用自定义欢迎消息和触发数学代理工作流的初始查询启动 Web 服务。

## 核心概念

- **WorkflowAgent** -- 执行用户定义的 `func_workflow` 函数而非标准 ReAct 推理循环的代理类型。提供对代理行为的完全编程控制。
- **`oxy_request.call()`** -- 核心代理间通信原语。代理和工具可以通过名称相互调用，传递参数并接收 `OxyResponse` 对象。
- **`oxy_request.send_message()`** -- 在代理执行期间通过 SSE（服务器发送事件）向前端推送自定义消息。
- **`func_process_input` / `func_format_output`** -- 分别在执行前转换请求和执行后转换响应的钩子函数。
- **`trust_mode=False`** -- 在 `time_agent` 上禁用信任模式时，代理在执行工具调用前会请求用户确认。
- **`is_retain_master_short_memory=True`** -- `math_agent` 保留来自主代理（用户）级别的对话历史，使工作流可以访问完整的对话上下文。
- **StdioMCPClient** -- 通过标准 I/O（stdin/stdout）连接到 MCP 服务器。每个 MCP 客户端将外部工具服务器封装为 OxyGent 工具。
- **`semaphore`** -- LLM 设置 `semaphore=4`，允许最多 4 个并发 LLM 请求。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动，欢迎消息为 "Hi, I'm OxyGent. How can I assist you?"。
2. 首个查询 "Please calculate the 20 positions of Pi" 被自动发送。
3. 主代理将其路由到 `math_agent`。
4. `math_agent` 工作流执行：
   - 记录对话历史。
   - 向前端发送自定义 SSE 消息。
   - 调用 `time_agent` 获取 Asia/Shanghai 时区的当前时间。
   - 直接调用 `default_llm` 发送简单问候。
   - 从查询中提取数字 "20"，调用 `calc_pi` 计算圆周率到 20 位小数。
5. 结果经 `format_output` 格式化（添加 "Answer: " 前缀）后显示在 Web UI 中。
