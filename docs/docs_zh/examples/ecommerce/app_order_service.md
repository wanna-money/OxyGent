# 电商订单服务

**源文件:** `examples/ecommerce/app_order_service.py`

## 概述

本文件定义了电商多智能体系统中四个后端微服务之一的**订单服务**。它运行在 8081 端口，提供一个使用 MCP 订单工具管理订单查询和订单取消的 `ReActAgent`。同时，它还通过 SSE 连接 8082 端口的支付服务作为子代理，使订单代理能够回答任意订单的支付相关问题。

## 前置条件

- 环境变量（在 `.env` 文件中配置或直接导出）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥。
  - `DEFAULT_LLM_BASE_URL` -- LLM 端点的基础 URL。
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符。
- 必须安装 **uv**（用于运行 MCP 工具服务器）。
- **支付服务**（`app_payment_service.py`）必须已经在 `http://127.0.0.1:8082` 上运行。

### 启动顺序（在完整电商系统中）

1. **端口 8082** -- 首先启动支付服务：`python -m examples.ecommerce.app_payment_service`
2. **端口 8081** -- 然后启动本订单服务：`python -m examples.ecommerce.app_order_service`
3. **端口 8085** -- 最后启动网关（如果运行完整系统）。

## 运行方式

```bash
# 终端 1 -- 支付服务（必须先运行）
python -m examples.ecommerce.app_payment_service

# 终端 2 -- 订单服务
python -m examples.ecommerce.app_order_service
```

服务启动后可通过 `http://127.0.0.1:8081` 访问。

## 代码详解

### 配置

```python
Config.set_app_name("order-service")
Config.set_server_port(8081)
```

将应用名称设为 `order-service`，并绑定到 **8081** 端口。

### 组件（`oxy_space`）

| 组件 | 类型 | 用途 |
|---|---|---|
| `default_llm` | `HttpLLM` | 共享的 LLM 后端，`temperature=0.01`，`semaphore=4`。 |
| `order_tools` | `StdioMCPClient` | 通过 `uv` 运行 `mcp_servers/order_tools.py`。提供三个工具：`query_order`（按订单 ID 查询订单详情）、`query_user_orders`（查询某用户的所有订单）和 `cancel_order`（取消订单并记录原因和时间戳）。 |
| `payment_service` | `SSEOxyGent` | 8082 端口支付服务的远程代理。允许订单代理将支付相关查询（支付状态、支付方式）委派给支付微服务。 |
| `order_agent` | `ReActAgent` | 本服务的主代理（`is_master=True`）。使用 `order_tools` 进行订单管理，并可以委派 `payment_service` 处理支付查询。 |

### 入口点

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service()
```

在 8081 端口启动 Web 服务，无预填查询。

## 核心概念

- **服务组合** -- 订单服务展示了一个微服务如何依赖另一个微服务。通过将 `payment_service` 作为子代理，订单代理可以透明地处理诸如"ORDER001 的支付状态是什么？"这样的查询，将其委派给支付服务。
- **订单生命周期** -- MCP 订单工具模拟了一个完整的订单管理系统，包含三个处于不同状态的示例订单：ORDER001（已发货）、ORDER002（已送达）、ORDER003（待支付）。`cancel_order` 工具仅允许取消"处理中"或"待支付"状态的订单。
- **跨服务代理层级** -- 在本服务内部，`order_agent` 是主代理。但当被网关调用时，它扮演子代理的角色。OxyGent 的 `is_master=True` 标志仅在单个 MAS 实例中指定入口点。

## 预期行为

1. 当被网关调用或直接访问时，订单代理可以回答以下查询：
   - "查看 ORDER001" -- 返回订单详情，包括商品、总价、状态和收货地址。
   - "列出 USER003 的所有订单" -- 返回该用户的所有订单。
   - "取消 ORDER003，因为用户不想要了" -- 取消订单（状态从"待支付"变为"已取消"），记录取消原因和时间戳，并返回商品详情。
   - "ORDER001 的支付状态是什么？" -- 委派给支付服务，返回支付详情（PAY001，通过支付方式 A 支付）。
2. 尝试取消 ORDER001（状态"已发货"）将失败，并返回消息说明已发货的订单无法取消。
