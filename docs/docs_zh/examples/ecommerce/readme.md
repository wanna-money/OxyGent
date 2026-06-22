# 电商示例

这些示例展示了一个使用 OxyGent 构建的完整分布式电商多智能体系统，其中商品、订单、支付和物流等专业微服务通过中央网关智能体进行统一编排。

---

## 示例

### 网关智能体

**文件:** `examples/ecommerce/app_gateway.py`

本示例实现了编排整个电商系统的中央网关。它定义了一个名为 `gateway_agent` 的 `ReActAgent`（标记为 `is_master=True`），将用户请求路由到四个子智能体：`order_agent`、`product_agent`、`logistics_agent` 和 `cancel_order_workflow`。前三个是通过 `SSEOxyGent` 分别连接到端口 8081、8080 和 8083 上服务的远程智能体，每个都使用 `func_process_input` 钩子在转发前将用户级查询与当前查询合并。`cancel_order_workflow` 是一个本地 `WorkflowAgent`，实现了多步骤的订单取消流程：首先调用 `order_agent` 取消订单，然后调用 `product_agent` 释放预留库存。网关运行在端口 8085 上，展示了启用信任模式的复杂跨服务工作流编排。

**核心组件:**
- `HttpLLM` ("default_llm") — 网关智能体推理所用的 LLM 后端
- `ReActAgent` ("gateway_agent") — 在所有子智能体之间路由请求的主控智能体
- `WorkflowAgent` ("cancel_order_workflow") — 带有自定义 `cancel_order_workflow` 函数的本地工作流智能体，链式调用远程服务完成订单取消和库存释放
- `SSEOxyGent` ("product_agent") — 连接到端口 8080 商品服务的远程代理
- `SSEOxyGent` ("order_agent") — 连接到端口 8081 订单服务的远程代理
- `SSEOxyGent` ("logistics_agent") — 连接到端口 8083 物流服务的远程代理
- `func_process_input` (update_query) — 输入预处理钩子，合并主控级查询与当前查询

**[详细文档 →](./app_gateway.md)**

---

### 商品服务

**文件:** `examples/ecommerce/app_product_service.py`

本示例将商品和库存管理微服务部署在端口 8080 上。它配置了一个名为 `product_agent` 的 `ReActAgent`，配备两个 MCP 工具客户端：`product_db` 用于商品数据库查询（商品信息、关键词搜索、分类浏览），`inventory_tools` 用于库存管理操作（库存检查、可用性验证、仓库分布）。该智能体被标记为此服务的主控，使用 `HttpLLM` 进行推理以决定调用哪些工具。

**核心组件:**
- `HttpLLM` — 用于商品相关推理的 LLM 后端
- `StdioMCPClient` ("product_db") — 商品数据库工具的 MCP 客户端
- `StdioMCPClient` ("inventory_tools") — 库存管理工具的 MCP 客户端
- `ReActAgent` ("product_agent") — 处理商品查询和库存操作的主控智能体

**[详细文档 →](./app_product_service.md)**

---

### 订单服务

**文件:** `examples/ecommerce/app_order_service.py`

本示例将订单管理微服务部署在端口 8081 上。它配置了一个名为 `order_agent` 的 `ReActAgent`，配备 `order_tools` MCP 客户端用于订单管理操作（查询订单详情、用户订单历史、取消订单）。该智能体还拥有一个通过 `SSEOxyGent` 连接到端口 8082 支付服务的子智能体 `payment_service`，可以将支付相关查询委派给它。这展示了一种嵌套的分布式模式，即一个微服务智能体可以调用另一个远程智能体。

**核心组件:**
- `HttpLLM` — 用于订单相关推理的 LLM 后端
- `StdioMCPClient` ("order_tools") — 订单管理工具的 MCP 客户端
- `SSEOxyGent` ("payment_service") — 连接到端口 8082 支付服务的远程代理
- `ReActAgent` ("order_agent") — 处理订单查询并支持支付委派的主控智能体

**[详细文档 →](./app_order_service.md)**

---

### 支付服务

**文件:** `examples/ecommerce/app_payment_service.py`

本示例将支付处理微服务部署在端口 8082 上。它配置了一个名为 `payment_service` 的 `ReActAgent`，配备 `payment_tools` MCP 客户端，用于处理支付相关操作，如按订单号查询支付状态、支付详情，以及提供支付方式信息。这是一个无子智能体的叶子级服务，作为专注于单一领域的智能体，供其他服务远程调用。

**核心组件:**
- `HttpLLM` — 用于支付相关推理的 LLM 后端
- `StdioMCPClient` ("payment_tools") — 支付处理工具的 MCP 客户端
- `ReActAgent` ("payment_service") — 处理支付查询的主控智能体

**[详细文档 →](./app_payment_service.md)**

---

### 物流服务

**文件:** `examples/ecommerce/app_logistics_service.py`

本示例将物流和配送微服务部署在端口 8083 上。它配置了一个名为 `logistics_agent` 的 `ReActAgent`，配备两个 MCP 工具客户端：`logistics_tools` 用于包裹追踪和发货状态查询，`delivery_tools` 用于配送信息管理和运费计算。与支付服务类似，这是一个专注于单一领域的叶子级服务，由网关智能体通过 SSE 进行调用。

**核心组件:**
- `HttpLLM` — 用于物流相关推理的 LLM 后端
- `StdioMCPClient` ("logistics_tools") — 物流追踪工具的 MCP 客户端
- `StdioMCPClient` ("delivery_tools") — 配送管理工具的 MCP 客户端
- `ReActAgent` ("logistics_agent") — 处理物流和配送查询的主控智能体

**[详细文档 →](./app_logistics_service.md)**
