# 电商物流服务

**源文件:** `examples/ecommerce/app_logistics_service.py`

## 概述

本文件定义了电商多智能体系统中四个后端微服务之一的**物流服务**。它运行在 8083 端口，提供一个配备了物流跟踪和配送管理 MCP 工具的 `ReActAgent`。该服务处理通过运单号或订单号进行的包裹跟踪、配送信息查询，以及物流方式推荐与费用计算。

## 前置条件

- 环境变量（在 `.env` 文件中配置或直接导出）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥。
  - `DEFAULT_LLM_BASE_URL` -- LLM 端点的基础 URL。
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符。
- 必须安装 **uv**（用于运行 MCP 工具服务器）。
- 无需先启动其他服务——本服务没有下游依赖。

### 启动顺序（在完整电商系统中）

本服务可以独立启动。在完整系统中，应在网关之前启动：

1. **端口 8083** -- 启动本物流服务。
2. **端口 8085** -- 然后启动 `app_gateway.py`。

## 运行方式

```bash
python -m examples.ecommerce.app_logistics_service
```

服务启动后可通过 `http://127.0.0.1:8083` 访问。

## 代码详解

### 配置

```python
Config.set_app_name("logistics-service")
Config.set_server_port(8083)
```

将应用名称设为 `logistics-service`，并绑定到 **8083** 端口。

### 组件（`oxy_space`）

| 组件 | 类型 | 用途 |
|---|---|---|
| `default_name` | `HttpLLM` | 共享的 LLM 后端，`temperature=0.01`，`semaphore=4`。 |
| `logistics_tools` | `StdioMCPClient` | 通过 `uv` 运行 `mcp_servers/logistics_tools.py`。提供：`track_package`（按运单号跟踪）和 `track_by_order`（按订单号跟踪）。使用内存中的模拟数据。 |
| `delivery_tools` | `StdioMCPClient` | 通过 `uv` 运行 `mcp_servers/delivery_tools.py`。提供：`get_delivery_info`（按订单号查询配送详情）和 `get_delivery_methods`（根据城市和重量查询可用的物流方式及费用计算）。 |
| `logistics_agent` | `ReActAgent` | 本服务的主代理（`is_master=True`）。使用 `logistics_tools` 和 `delivery_tools` 通过 LLM 驱动的推理来回答物流和配送查询。 |

### 入口点

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service()
```

在 8083 端口启动 Web 服务，无预填查询。

## 核心概念

- **领域专属微服务** -- 本服务将所有物流相关功能（跟踪、配送信息、物流方式）封装在一个代理之后。网关将其作为不透明的 `SSEOxyGent` 访问，将物流领域与其他关注点解耦。
- **多 MCP 工具客户端** -- 单个代理可以使用来自多个 MCP 服务器的工具。此处 `logistics_tools` 处理包裹跟踪，而 `delivery_tools` 处理配送管理，但两者都暴露给同一个 `logistics_agent`。
- **模拟数据** -- MCP 服务器使用内存字典模拟真实数据库。可用的模拟数据包括 `JD1234567890`（ORDER001，运输中）和 `JD1234567891`（ORDER002，已签收）的物流跟踪信息，以及 ORDER001 和 ORDER002 的配送信息。

## 预期行为

1. 当被网关调用时，物流代理可以回答以下查询：
   - "跟踪包裹 JD1234567890" -- 返回完整的物流历史记录，显示包裹正在运输中。
   - "ORDER002 的配送状态是什么？" -- 返回配送信息，显示订单已送达。
   - "省 A 2 公斤的包裹有哪些配送方式？" -- 返回可用的配送方式，包括标准配送、快速配送、次日达和当日达，并计算相应费用。
2. 代理使用 ReAct 推理来根据用户查询确定调用哪个工具。
3. 物流跟踪历史包含每个运输事件的时间戳、位置和状态描述。
