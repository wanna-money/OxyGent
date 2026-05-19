# 电商支付服务

**源文件:** `examples/ecommerce/app_payment_service.py`

## 概述

本文件定义了电商多智能体系统中四个后端微服务中最简单的**支付服务**。它运行在 8082 端口，提供一个配备支付相关 MCP 工具的 `ReActAgent`，可以通过支付 ID 或订单 ID 查询支付状态，以及列出支持的支付方式。该服务由运行在 8081 端口的订单服务调用。

## 前置条件

- 环境变量（在 `.env` 文件中配置或直接导出）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥。
  - `DEFAULT_LLM_BASE_URL` -- LLM 端点的基础 URL。
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符。
- 必须安装 **uv**（用于运行 MCP 工具服务器）。
- 无需先启动其他服务——这是叶节点服务。

### 启动顺序（在完整电商系统中）

本服务没有下游依赖。应在订单服务之前启动：

1. **端口 8082** -- 首先启动本支付服务。
2. **端口 8081** -- 然后启动 `app_order_service.py`（依赖本服务）。

## 运行方式

```bash
python -m examples.ecommerce.app_payment_service
```

服务启动后可通过 `http://127.0.0.1:8082` 访问。

## 代码详解

### 配置

```python
Config.set_app_name("payment-service")
Config.set_server_port(8082)
```

将应用名称设为 `payment-service`，并绑定到 **8082** 端口。

### 组件（`oxy_space`）

| 组件 | 类型 | 用途 |
|---|---|---|
| `default_llm` | `HttpLLM` | 共享的 LLM 后端，`temperature=0.01`，`semaphore=4`。 |
| `payment_tools` | `StdioMCPClient` | 通过 `uv` 运行 `mcp_servers/payment_tools.py`。提供两个工具：`query_payment_status`（通过支付 ID 或订单 ID 查询支付详情）和 `get_payment_methods`（列出支持的支付方式及其费率和限额）。 |
| `payment_service` | `ReActAgent` | 本服务的主代理（`is_master=True`）。使用 `payment_tools` 通过 LLM 驱动的推理来回答支付相关查询。 |

### 入口点

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service()
```

在 8082 端口启动 Web 服务，无预填查询。

## 核心概念

- **叶节点服务模式** -- 与分布式示例中的时间代理类似，支付服务是一个没有下游依赖的叶节点。它展示了微服务架构中最小的可部署单元。
- **双键查询** -- `query_payment_status` 工具同时接受支付 ID（如 `PAY001`）或订单 ID（如 `ORDER001`），并通过 `ORDER_TO_PAYMENT` 映射在内部解析。这简化了调用代理的逻辑，因为它不需要知道支付 ID。
- **模拟支付数据** -- 可用两条支付记录：PAY001（对应 ORDER001，金额 5999.00，通过方式 A 支付）和 PAY002（对应 ORDER002，金额 12999.00，通过方式 B 支付）。ORDER003 没有关联的支付记录（它处于"待支付"状态）。

## 预期行为

1. 当被订单服务调用或直接访问时，支付代理可以回答以下查询：
   - "ORDER001 的支付状态是什么？" -- 返回支付详情：PAY001，金额 5999.00，通过支付方式 A 支付。
   - "查看支付 PAY002" -- 返回指定支付 ID 的支付详情。
   - "支持哪些支付方式？" -- 返回三种支付方式（A、B、C），包含费率、最大金额和说明。
2. 查询 ORDER003 的支付将返回错误，因为该订单不存在支付记录（仍处于待支付状态）。
