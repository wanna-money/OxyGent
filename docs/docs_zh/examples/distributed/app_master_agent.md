# 分布式主控代理（网关）

**源文件:** `examples/distributed/app_master_agent.py`

## 概述

本文件定义了三服务分布式多智能体系统中的**主控代理**。它作为用户交互的网关，在默认端口（8080）上运行 Web UI，托管一个本地文件代理，并通过 SSE（Server-Sent Events）将数学相关的查询转发到运行在 8081 端口的远程数学代理。本文件与 `app_math_agent.py` 和 `app_time_agent.py` 一起，展示了 OxyGent 如何将多个代理分布到独立进程中，并通过 HTTP/SSE 协议进行通信。

## 前置条件

- 环境变量（在 `.env` 文件中配置或直接导出）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥。
  - `DEFAULT_LLM_BASE_URL` -- LLM 端点的基础 URL。
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符（如 `gpt-4`）。
- 必须安装 **Node.js**（使用 `npx` 启动 MCP 文件系统服务器）。
- **数学代理服务**（`app_math_agent.py`）必须已经在 `http://127.0.0.1:8081` 上运行。数学代理又依赖于运行在 8082 端口的时间代理。请参阅下方[启动顺序](#启动顺序)。

### 启动顺序

由于主控代理通过 SSE 连接数学代理，而数学代理又通过 SSE 连接时间代理，因此必须从下往上启动各服务：

1. **端口 8082** -- 首先启动时间代理：`python -m examples.distributed.app_time_agent`
2. **端口 8081** -- 然后启动数学代理：`python -m examples.distributed.app_math_agent`
3. **端口 8080** -- 最后启动主控代理：`python -m examples.distributed.app_master_agent`

## 运行方式

```bash
# 终端 1
python -m examples.distributed.app_time_agent

# 终端 2
python -m examples.distributed.app_math_agent

# 终端 3
python -m examples.distributed.app_master_agent
```

三个服务全部启动后，在浏览器中打开 `http://127.0.0.1:8080` 即可访问 Web UI。

## 代码详解

### 配置

本文件没有显式调用 `Config.set_server_port()` 或 `Config.set_app_name()`，因此使用框架默认值——端口 **8080** 和默认应用名称。

### 组件（`oxy_space`）

`oxy_space` 列表注册了四个组件：

| 组件 | 类型 | 用途 |
|---|---|---|
| `default_llm` | `HttpLLM` | 所有本地代理共享的 LLM 后端。`temperature` 设为 0.01 以获得近乎确定性的输出。`semaphore=4` 限制并发 LLM 调用数。 |
| `file_tools` | `StdioMCPClient` | 通过 `npx` 启动 `@modelcontextprotocol/server-filesystem` MCP 服务器，作用域限定在 `./local_file` 目录。提供文件系统读写工具。 |
| `master_agent` | `ReActAgent` | 顶层代理（`is_master=True`）。根据用户意图将查询路由到 `file_agent` 或 `math_agent`。 |
| `file_agent` | `ReActAgent` | 使用 `file_tools` 处理本地文件查询的子代理。 |
| `math_agent` | `SSEOxyGent` | **远程**代理代理。通过 SSE 将请求转发到 `http://127.0.0.1:8081` 上运行的实际数学代理。`is_share_call_stack=False` 使各服务之间的调用栈保持隔离。 |

### 入口点

`main()` 协程创建一个 `MAS` 实例，然后以初始查询 *"The first 30 positions of pi"* 启动 Web 服务。该预填查询在 Web UI 首次加载时显示，会立即触发分布式工作流的演示。

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="The first 30 positions of pi")
```

## 核心概念

- **SSEOxyGent** -- 分布式服务之间的桥梁。它将远程 MAS 端点包装为本地代理的形式，使用 SSE 进行流式通信。这是实现多进程代理部署的核心机制。
- **is_share_call_stack=False** -- 阻止主控代理的调用栈上下文被转发给远程数学代理，使每个服务的推理历史保持独立。
- **ReActAgent** -- 遵循 Reason-Act（推理-行动）循环的代理：先对用户查询进行推理，选择一个工具或子代理，观察结果，然后重复直到产生最终答案。
- **MCP（Model Context Protocol）** -- `StdioMCPClient` 将外部 MCP 服务器作为子进程启动，并通过标准输入/输出通信，将服务器的工具暴露给代理使用。

## 预期行为

1. Web UI 在 `http://127.0.0.1:8080` 打开，预填查询 *"The first 30 positions of pi"*。
2. `master_agent` 识别这是一个数学任务，将其委派给 `math_agent`。
3. `math_agent` 代理通过 SSE 将请求转发到 8081 端口，那里的实际数学代理会计算 pi 的前 30 位小数（在此之前可能会先查询 8082 端口的时间代理）。
4. 结果通过 SSE 连接返回主控代理，并在 Web UI 中展示。
5. 用户也可以提问文件相关的问题（如"列出 local_file 中的文件"），主控代理会将其路由到 `file_agent` 处理。
