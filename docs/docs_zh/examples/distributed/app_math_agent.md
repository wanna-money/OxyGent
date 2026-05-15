# 分布式数学代理服务

**源文件:** `examples/distributed/app_math_agent.py`

## 概述

本文件定义了三服务分布式系统中的**数学代理服务**，作为中间层运行在 8081 端口。它暴露一个 `WorkflowAgent`，通过自定义 Python 工作流函数处理 pi 计算请求。同时，它还演示了跨服务代理通信——在执行计算之前，通过 SSE 调用运行在 8082 端口的远程时间代理。本服务由运行在 8080 端口的主控代理调用。

## 前置条件

- 环境变量（在 `.env` 文件中配置或直接导出）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥。
  - `DEFAULT_LLM_BASE_URL` -- LLM 端点的基础 URL。
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符。
- 必须安装 **uv**（用于运行 MCP 数学工具服务器）。
- **时间代理服务**（`app_time_agent.py`）必须已经在 `http://127.0.0.1:8082` 上运行。

### 启动顺序

1. **端口 8082** -- 首先启动 `app_time_agent.py`。
2. **端口 8081** -- 然后启动本数学代理。
3. **端口 8080** -- 最后启动 `app_master_agent.py`（如果需要完整的分布式演示）。

## 运行方式

```bash
# 终端 1（首先启动时间代理）
python -m examples.distributed.app_time_agent

# 终端 2
python -m examples.distributed.app_math_agent
```

服务启动后可通过 `http://127.0.0.1:8081` 访问，同时也提供 Web UI 用于独立测试。

## 代码详解

### 配置

```python
Config.set_app_name("app-math")
Config.set_server_port(8081)
```

为服务指定独立的应用名称（`app-math`），并绑定到 **8081** 端口，以便与 8080 端口的主控代理和 8082 端口的时间代理共存。

### 组件（`oxy_space`）

| 组件 | 类型 | 用途 |
|---|---|---|
| `default_name` | `HttpLLM` | 共享的 LLM 后端。 |
| `math_tools` | `StdioMCPClient` | 通过 `uv` 运行 `mcp_servers/math_tools.py`。暴露两个工具：`power`（幂运算）和 `calc_pi`（计算 pi 到 N 位小数）。 |
| `time_agent` | `SSEOxyGent` | 远程代理，代理 8082 端口上的时间代理服务。 |
| `math_agent` | `WorkflowAgent` | 本服务的主代理（`is_master=True`）。使用自定义的 `func_workflow` 而非 LLM 驱动的推理循环。可访问 `math_tools` 和 `time_agent` 作为子代理。 |

### 工作流函数

`workflow` 函数是核心逻辑：

```python
async def workflow(oxy_request: OxyRequest):
```

执行步骤如下：

1. **读取对话历史** -- 调用 `oxy_request.get_short_memory()` 获取本地代理的历史记录，调用 `oxy_request.get_short_memory(master_level=True)` 获取顶层用户对话记录。
2. **调用时间代理** -- 通过 `oxy_request.call()` 向 8082 端口的远程 `time_agent` 发送 "What time is it now?" 请求，演示跨服务通信。
3. **提取精度参数** -- 使用正则表达式从用户查询中提取数字（如从 "The 30 positions of pi" 中提取 "30"）。
4. **调用 `calc_pi`** -- 如果找到数字，则以该精度调用 `calc_pi` MCP 工具。
5. **返回默认值** -- 如果未找到数字，则返回默认的 2 位近似值（3.14）。

### 入口点

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="The 30 positions of pi")
```

在 8081 端口启动 Web 服务，并提供演示查询用于独立测试。

## 核心概念

- **WorkflowAgent** -- 与 `ReActAgent`（使用 LLM 推理循环）不同，`WorkflowAgent` 执行一个确定性的 Python 函数（`func_workflow`）。这使开发者可以完全控制执行流程，同时仍然能利用子代理和工具。
- **oxy_request.call()** -- 一个代理调用另一个代理（本地或远程）的机制。`callee` 参数指定目标名称，`arguments` 传递负载。当被调用者是 `SSEOxyGent` 时，这在跨进程边界时透明工作。
- **master_level=True** -- 访问对话历史或用户查询时，`master_level=True` 从顶层主控代理获取上下文，而非当前代理。这在分布式场景中至关重要，因为数学代理需要看到终端用户最初提出的问题。
- **跨服务追踪** -- 每个请求携带一个 `trace_id`，将整个分布式调用链串联起来，便于调试和可观测性。

## 预期行为

1. 当 8080 端口的主控代理发送 pi 计算请求时，通过 SSE 到达本服务。
2. `workflow` 函数首先查询 8082 端口的时间代理，并在控制台打印当前时间。
3. 然后从查询中提取小数位数，并调用 `calc_pi` MCP 工具。
4. 计算出的 pi 值返回给调用方的主控代理，由其展示给用户。
5. 控制台输出将显示对话历史、用户的原始查询以及从远程时间代理获取的当前时间。
