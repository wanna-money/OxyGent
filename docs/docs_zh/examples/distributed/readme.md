# 分布式示例

这些示例展示了如何使用 OxyGent 构建分布式多智能体系统，其中多个独立部署的智能体服务通过 SSE（Server-Sent Events）连接进行相互通信。

---

## 示例

### 主控智能体（网关）

**文件:** `examples/distributed/app_master_agent.py`

本示例搭建了一个用于编排分布式多智能体系统的主控网关智能体。它定义了一个名为 `master_agent` 的 `ReActAgent`（标记为 `is_master=True`），将任务委派给两个子智能体：一个是通过 `@modelcontextprotocol/server-filesystem` MCP 工具查询本地文件的本地 `file_agent`，另一个是通过 `SSEOxyGent` 连接到端口 8081 上独立服务的远程 `math_agent`。主控智能体使用 `HttpLLM` 进行推理，并以"圆周率前 30 位"作为初始查询启动 Web 服务。

**核心组件:**
- `HttpLLM` — 通过环境变量配置的 LLM 推理后端
- `StdioMCPClient` ("file_tools") — 封装文件系统服务器的 MCP 客户端，用于本地文件操作
- `ReActAgent` ("master_agent") — 主控编排智能体，负责将任务路由到子智能体
- `ReActAgent` ("file_agent") — 使用文件系统 MCP 工具的本地文件查询智能体
- `SSEOxyGent` ("math_agent") — 连接到端口 8081 数学服务的远程智能体代理

**[详细文档 →](./app_master_agent.md)**

---

### 数学智能体服务

**文件:** `examples/distributed/app_math_agent.py`

本示例将一个专注于数学计算的智能体作为独立服务部署在端口 8081 上。它使用带有自定义 `workflow` 函数的 `WorkflowAgent` 来编排多步骤逻辑：首先通过 `SSEOxyGent` 调用端口 8082 上的远程 `time_agent` 获取当前时间，然后从用户查询中解析数字，并调用 `calc_pi` MCP 工具计算对应位数的圆周率。该工作流演示了如何通过 `get_short_memory()` 在智能体层级和主控层级访问对话历史，并展示了如何在单个工作流函数中链式调用远程智能体和本地工具。

**核心组件:**
- `HttpLLM` — 数学智能体的 LLM 后端
- `StdioMCPClient` ("math_tools") — 运行数学工具服务器的 MCP 客户端，用于圆周率计算
- `SSEOxyGent` ("time_agent") — 连接到端口 8082 时间服务的远程智能体代理
- `WorkflowAgent` ("math_agent") — 带有自定义 `func_workflow` 的主控智能体，链式调用远程智能体和工具
- `Config.set_app_name` / `Config.set_server_port` — 将此服务配置为 "app-math"，运行在端口 8081

**[详细文档 →](./app_math_agent.md)**

---

### 时间智能体服务

**文件:** `examples/distributed/app_time_agent.py`

本示例将一个简单的时间查询智能体作为独立服务部署在端口 8082 上。它配置了一个名为 `time_agent` 的 `ReActAgent`，使用通过 `uvx` 运行的 `mcp-server-time` MCP 工具（设置为 `Asia/Shanghai` 时区）来回答时间相关的查询。这是三个分布式服务中最简单的一个，展示了如何将单一用途的智能体部署为独立微服务，供系统中的其他智能体通过 SSE 远程调用。

**核心组件:**
- `HttpLLM` — 用于推理的 LLM 后端
- `StdioMCPClient` ("time_tools") — 运行 `mcp-server-time` 服务器的 MCP 客户端，配置为上海时区
- `ReActAgent` ("time_agent") — 回答时间查询的单一用途智能体
- `Config.set_app_name` / `Config.set_server_port` — 将此服务配置为 "app-time"，运行在端口 8082

**[详细文档 →](./app_time_agent.md)**
