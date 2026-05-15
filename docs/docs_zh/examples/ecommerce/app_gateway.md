# 电商网关代理

**源文件:** `examples/ecommerce/app_gateway.py`

## 概述

本文件定义了五服务电商多智能体系统中的**网关代理**，即中央编排器。它运行在 8085 端口，作为所有用户请求的唯一入口，将请求路由到相应的领域专属远程代理：商品服务（8080 端口）、订单服务（8081 端口）、支付服务（8082 端口，通过订单服务访问）和物流服务（8083 端口）。同时，它还包含一个自定义的 `WorkflowAgent`，用于处理跨域的订单取消流程。

## 前置条件

- 环境变量（在 `.env` 文件中配置或直接导出）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥。
  - `DEFAULT_LLM_BASE_URL` -- LLM 端点的基础 URL。
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符。
- 启动网关之前，**所有四个后端服务**必须已经运行。请参阅下方[启动顺序](#启动顺序)。

### 启动顺序

各服务之间形成依赖链，请按以下顺序启动：

1. **端口 8080** -- 商品服务：`python -m examples.ecommerce.app_product_service`
2. **端口 8082** -- 支付服务：`python -m examples.ecommerce.app_payment_service`
3. **端口 8081** -- 订单服务（依赖 8082 端口的支付服务）：`python -m examples.ecommerce.app_order_service`
4. **端口 8083** -- 物流服务：`python -m examples.ecommerce.app_logistics_service`
5. **端口 8085** -- 网关（依赖以上所有服务）：`python -m examples.ecommerce.app_gateway`

## 运行方式

```bash
# 终端 1 -- 商品服务
python -m examples.ecommerce.app_product_service

# 终端 2 -- 支付服务
python -m examples.ecommerce.app_payment_service

# 终端 3 -- 订单服务
python -m examples.ecommerce.app_order_service

# 终端 4 -- 物流服务
python -m examples.ecommerce.app_logistics_service

# 终端 5 -- 网关
python -m examples.ecommerce.app_gateway
```

所有服务启动后，在浏览器中打开 `http://127.0.0.1:8085` 访问 Web UI。

## 代码详解

### 配置

```python
Config.set_server_port(8085)
```

网关运行在 **8085** 端口，与所有后端服务分离。

### 组件（`oxy_space`）

| 组件 | 类型 | 用途 |
|---|---|---|
| `default_llm` | `HttpLLM` | 网关本地代理共享的 LLM 后端。 |
| `cancel_order_workflow` | `WorkflowAgent` | 编排跨订单服务和商品服务的订单取消工作流。使用 `trust_mode=True`（跳过 LLM 确认步骤），超时时间为 20 秒。 |
| `gateway_agent` | `ReActAgent` | 主代理（`is_master=True`）。根据用户意图将查询路由到相应的子代理或工作流。可访问 `order_agent`、`product_agent`、`logistics_agent` 和 `cancel_order_workflow`。 |
| `product_agent` | `SSEOxyGent` | 8080 端口商品服务的远程代理。处理商品查询、库存检查和库存管理。 |
| `order_agent` | `SSEOxyGent` | 8081 端口订单服务的远程代理。处理订单查询、订单历史和订单取消。 |
| `logistics_agent` | `SSEOxyGent` | 8083 端口物流服务的远程代理。处理包裹跟踪、配送信息和物流方式查询。 |

### 钩子函数/回调

#### `update_query(oxy_request: OxyRequest)`

附加到 `product_agent`、`order_agent` 和 `logistics_agent` SSE 代理上的预处理函数（`func_process_input`）。它通过将原始用户查询（来自 `master_level=True`）与当前子查询组合来丰富请求内容，确保远程服务拥有完整的上下文：

```python
oxy_request.set_query(f"user query is {user_query}\ncurrent query is {current_query}")
```

#### `cancel_order_workflow(oxy_request: OxyRequest)`

`cancel_order_workflow` 代理的工作流函数。它执行跨服务的多步操作：

1. **调用 `order_agent`** -- 将取消请求发送到订单服务，订单服务取消订单并返回订单详情（包括商品 ID 和数量）。
2. **调用 `product_agent`** -- 将订单代理的响应发送到商品服务，商品服务释放预留库存（调用 `release_reserved_stock`）。
3. **返回合并结果** -- 将订单取消和库存更新的结果合并为一个响应。

### 入口点

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(
        first_query="Because the user doesn't want it anymore, so to cancel ORDER003 order, please help me cancel this order",
    )
```

在 8085 端口启动 Web 服务，并以触发订单取消工作流的演示查询作为初始查询。

## 核心概念

- **多服务架构** -- 网关模式实现了关注点分离：每个领域（商品、订单、支付、物流）作为独立服务运行。网关提供统一接口并处理跨域编排。
- **WorkflowAgent 用于跨域操作** -- 订单取消等操作跨越多个领域（订单 + 库存）。带有自定义 `func_workflow` 的 `WorkflowAgent` 为这些横切关注点提供确定性编排。
- **func_process_input** -- 在将 `OxyRequest` 发送到远程代理之前对其进行转换的钩子。此处它附加了原始用户查询，以便远程服务拥有足够的上下文来执行操作。
- **trust_mode=True** -- 在 `cancel_order_workflow` 上启用此选项，绕过任何 LLM 确认步骤，允许工作流直接执行各步骤而无需在每个阶段询问用户确认。
- **SSEOxyGent** -- 每个远程服务在网关的 `oxy_space` 中都表示为一个 `SSEOxyGent`。这使得远程服务在路由层面与本地代理无法区分。

## 预期行为

1. Web UI 在 `http://127.0.0.1:8085` 打开，预填取消 ORDER003 的演示查询。
2. `gateway_agent` 识别这是一个订单取消任务，将其路由到 `cancel_order_workflow`。
3. 工作流调用 `order_agent`（8081 端口），取消 ORDER003（状态从"待支付"变为"已取消"），并返回商品详情（商品 C x2，商品 A x1）。
4. 工作流随后调用 `product_agent`（8080 端口），释放已取消商品的预留库存。
5. 合并结果返回给用户，显示取消确认和库存更新信息。
6. 用户还可以提出商品问题（"商品 A 是什么？"）、订单问题（"查看 ORDER001"）或物流问题（"跟踪 JD1234567890"），网关会路由到相应的服务。
