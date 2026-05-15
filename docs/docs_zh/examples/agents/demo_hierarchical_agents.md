# 层级式多代理系统

**源文件:** `examples/agents/demo_hierarchical_agents.py`

## 概述

本示例展示了层级式多代理架构，其中一个主 `ReActAgent` 将任务委派给拥有各自 MCP 工具的专业子代理。主代理协调 `time_agent` 和 `file_agent`，实现跨多个工具领域的复杂工作流（例如获取当前时间并保存到文件）。这种模式对于构建需要链接多种专业能力的任务系统至关重要。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包
- 已安装 `uvx`（用于 `mcp-server-time`）
- 已安装 `npx` / Node.js（用于 `@modelcontextprotocol/server-filesystem`）
- `./local_file` 目录应已存在（作为文件 MCP 服务器的文件系统沙盒）

## 运行方式

```bash
python -m examples.agents.demo_hierarchical_agents
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量 |
| `time_tools` | `StdioMCPClient` | `params.command="uvx"`，`params.args=["mcp-server-time", "--local-timezone=Asia/Shanghai"]` |
| `file_tools` | `StdioMCPClient` | `params.command="npx"`，`params.args=["-y", "@modelcontextprotocol/server-filesystem", "./local_file"]` |
| `master_agent` | `ReActAgent` | `is_master=True`；`sub_agents=["time_agent", "file_agent"]`；`llm_model="default_llm"` |
| `time_agent` | `ReActAgent` | `desc="A tool for time query"`；`tools=["time_tools"]`；`llm_model="default_llm"` |
| `file_agent` | `ReActAgent` | `desc="A tool for file operation."`；`tools=["file_tools"]`；`llm_model="default_llm"` |

### 入口函数

```python
await mas.start_web_service(
    first_query="Get what time it is and save in `log.txt` under `/local_file`",
)
```

启动 Web 服务，初始查询为一个复合任务，同时需要时间查询和文件写入。

## 核心概念

- **层级委派** -- 主代理不直接使用任何工具，而是分解任务并委派给拥有各自工具集的专业子代理。
- **`is_master=True`** -- 显式标记主代理。`MAS` 运行时将所有传入查询路由到此代理。
- **同构子代理类型** -- 与异构示例不同，这里所有代理（主代理和子代理）都是 `ReActAgent` 实例，但它们在分配的工具和描述上有所不同。
- **MCP 工具隔离** -- 每个子代理只能访问其指定的 MCP 工具，确保关注点分离。
- **多步骤复合任务** -- 初始查询要求主代理先调用 `time_agent`，然后将结果传递给 `file_agent`，展示了顺序多代理协调。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 复合查询被发送："Get what time it is and save in `log.txt` under `/local_file`"。
3. 主代理分解任务：
   - 首先调用 `time_agent` 获取当前时间。
   - 然后调用 `file_agent` 将时间写入 `./local_file` 目录下的 `log.txt`。
4. `time_agent` 使用 `mcp-server-time` 工具获取当前时间（Asia/Shanghai 时区）。
5. `file_agent` 使用 `@modelcontextprotocol/server-filesystem` 工具创建/写入文件。
6. 最终结果确认两个操作均已完成，文件 `./local_file/log.txt` 包含当前时间。
