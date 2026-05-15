# MCP 工具集成示例

**源文件:** `examples/tools/demo_mcp.py`

## 概述

本示例展示如何通过 `StdioMCPClient` 使用 Model Context Protocol (MCP) 集成外部工具。示例配置了三个不同的 MCP 工具服务器——时间服务器、地图服务器和数学服务器——演示了 OxyGent 如何连接任何符合 MCP 协议的工具进程。示例中还包含了注释掉的 `SSEMCPClient` 和 `StreamableMCPClient` 配置，展示替代的传输模式。

## 前置条件

- 环境变量（在 `.env` 或终端中设置）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥
  - `DEFAULT_LLM_BASE_URL` -- LLM API 的基础 URL
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符
- 已安装 **Node.js**（用于基于 `npx` 的 MCP 服务器，如地图工具）
- 已安装 **uv** 或 **uvx**（用于基于 Python 的 MCP 服务器，如时间和数学工具）
- 地图工具需要有效的高德地图 API 密钥（需替换代码中的 `"API_KEY"`）
- `mcp_servers/` 目录中需包含 `math_tools.py`

## 运行方式

```bash
python -m examples.tools.demo_mcp
```

## 代码详解

### 配置

使用环境变量配置名为 `"default_llm"` 的 `HttpLLM`，为 ReAct 智能体提供推理能力。

### 组件（`oxy_space`）

`oxy_space` 包含五个组件（其中两个被注释）：

1. **`HttpLLM("default_llm")`** -- 语言模型。
2. **`StdioMCPClient("time_tools")`** -- 通过 `uvx` 启动 `mcp-server-time` 包，时区设置为 `Asia/Shanghai`，通过标准输入输出通信。
3. **`StdioMCPClient("map_tools")`** -- 通过 `npx` 启动 `@amap/amap-maps-mcp-server` 包，需要通过 `env` 参数传入高德地图 API 密钥。
4. **`StdioMCPClient("math_tools")`** -- 通过 `uv` 运行本地 Python MCP 服务器（`mcp_servers/math_tools.py`），提供数学计算工具。
5. **`ReActAgent("master_agent")`** -- ReAct 智能体，绑定了 `"time_tools"` 和 `"math_tools"`，通过 `llm_model` 显式指定使用 `"default_llm"` 进行推理。

注释部分展示了如何使用：
- **`SSEMCPClient`** -- 通过 Server-Sent Events 连接远程 MCP 服务器。
- **`StreamableMCPClient`** -- 通过可流式传输的 HTTP 端点连接远程 MCP 服务器。

### 入口点

`main()` 协程创建 `MAS` 上下文，初始化所有 MCP 客户端连接（启动 stdio 子进程），然后以初始查询 `"What time is it"` 启动 Web 服务。

## 核心概念

- **StdioMCPClient** -- 启动外部进程并通过 stdin/stdout 使用 MCP 协议通信。`params` 字典指定子进程的 `command`、`args` 和可选的 `env`。
- **SSEMCPClient** -- 通过 HTTP Server-Sent Events 连接到运行中的 MCP 服务器。适用于远程或共享的工具服务器。
- **StreamableMCPClient** -- 类似 SSE，但使用可流式传输的 HTTP 端点（`/mcp`），支持双向流式传输。
- **MCP（Model Context Protocol）** -- 一种标准化的 LLM 工具集成协议，允许智能体从任何符合 MCP 协议的服务器发现和调用工具。
- **工具名称引用** -- 智能体通过 MCP 客户端的 `name` 引用工具（如 `"time_tools"`），MAS 运行时将名称解析为实际的工具实例。

## 预期行为

1. MAS 初始化并启动 `time_tools` 和 `math_tools` MCP 服务器进程（以及可选的 `map_tools`）。
2. Web 服务器在 `http://127.0.0.1:8080` 启动。
3. 智能体收到查询"What time is it"。
4. 智能体判断需要使用时间工具，通过 MCP 调用并获取 `Asia/Shanghai` 时区的当前时间。
5. 智能体在 Web UI 中向用户展示当前时间。
