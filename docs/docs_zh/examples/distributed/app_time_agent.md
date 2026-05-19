# 分布式时间代理服务

**源文件:** `examples/distributed/app_time_agent.py`

## 概述

本文件定义了三服务分布式系统中的**时间代理服务**，作为叶节点运行在 8082 端口。它提供一个简单的 `ReActAgent`，使用 `mcp-server-time` MCP 工具来回答时间相关的查询。该服务由运行在 8081 端口的数学代理调用，也可以通过其自身的 Web UI 独立使用。

## 前置条件

- 环境变量（在 `.env` 文件中配置或直接导出）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥。
  - `DEFAULT_LLM_BASE_URL` -- LLM 端点的基础 URL。
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符。
- 必须安装 **uvx**（用于运行 `mcp-server-time` 包）。
- 无需先启动其他服务——这是叶节点服务。

### 启动顺序

本服务没有下游依赖。在完整的分布式演示中，应**最先**启动：

1. **端口 8082** -- 首先启动本时间代理。
2. **端口 8081** -- 然后启动 `app_math_agent.py`。
3. **端口 8080** -- 最后启动 `app_master_agent.py`。

## 运行方式

```bash
python -m examples.distributed.app_time_agent
```

服务启动后可通过 `http://127.0.0.1:8082` 访问。

## 代码详解

### 配置

```python
Config.set_app_name("app-time")
Config.set_server_port(8082)
```

将应用名称设为 `app-time`，并绑定到 **8082** 端口。

### 组件（`oxy_space`）

| 组件 | 类型 | 用途 |
|---|---|---|
| `default_llm` | `HttpLLM` | 共享的 LLM 后端，`temperature=0.01`，`semaphore=4`。 |
| `time_tools` | `StdioMCPClient` | 通过 `uvx` 启动 `mcp-server-time` MCP 服务器，时区设置为 `Asia/Shanghai`。提供时间相关的工具（获取当前时间、时区转换等）。 |
| `time_agent` | `ReActAgent` | 本服务的主代理。使用 `time_tools` 通过 LLM 驱动的 Reason-Act 循环来回答时间查询。 |

### 入口点

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="What time is it now?")
```

在 8082 端口启动 Web 服务，并提供演示查询用于独立测试。

## 核心概念

- **叶节点服务模式** -- 这是最简单的分布式 OxyGent 服务：一个代理搭配一个工具。它表明即使是最小的功能单元也可以作为独立服务部署，并由其他代理通过 SSE 访问。
- **StdioMCPClient 配合 uvx** -- `uvx` 命令可以直接运行 Python 包而无需事先安装。此处它启动 `mcp-server-time`，一个提供时间相关工具的社区 MCP 服务器。
- **时区配置** -- `--local-timezone=Asia/Shanghai` 参数配置时间服务器以中国标准时间（CST）报告时间。

## 预期行为

1. 独立访问时，`http://127.0.0.1:8082` 的 Web UI 会以查询 *"What time is it now?"* 打开。
2. `time_agent` 使用 MCP 时间工具确定 Asia/Shanghai 时区的当前时间。
3. 响应中显示当前的日期和时间。
4. 当被数学代理（8081 端口）远程调用时，执行相同的流程，但结果通过 SSE 返回，而不是显示在本地 Web UI 中。
