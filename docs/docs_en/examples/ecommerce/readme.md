# E-Commerce Examples

These examples demonstrate a complete distributed e-commerce multi-agent system using OxyGent, where specialized microservices for products, orders, payments, and logistics are orchestrated through a central gateway agent.

---

## Examples

### Gateway Agent

**File:** `examples/ecommerce/app_gateway.py`

This example implements the central gateway that orchestrates the entire e-commerce system. It defines a `ReActAgent` named `gateway_agent` (marked as `is_master=True`) that routes user requests to four sub-agents: `order_agent`, `product_agent`, `logistics_agent`, and `cancel_order_workflow`. The first three are remote agents connected via `SSEOxyGent` to services on ports 8081, 8080, and 8083 respectively, each using a `func_process_input` hook to merge the user-level query with the current query before forwarding. The `cancel_order_workflow` is a local `WorkflowAgent` that implements a multi-step order cancellation process: it first calls `order_agent` to cancel the order, then calls `product_agent` to release reserved stock. The gateway runs on port 8085 and demonstrates complex cross-service workflow orchestration with trust mode enabled.

**Key Components:**
- `HttpLLM` ("default_llm") — LLM backend for the gateway agent's reasoning
- `ReActAgent` ("gateway_agent") — master agent that routes requests across all sub-agents
- `WorkflowAgent` ("cancel_order_workflow") — local workflow agent with a custom `cancel_order_workflow` function that chains order cancellation and inventory release across remote services
- `SSEOxyGent` ("product_agent") — remote proxy to the product service on port 8080
- `SSEOxyGent` ("order_agent") — remote proxy to the order service on port 8081
- `SSEOxyGent` ("logistics_agent") — remote proxy to the logistics service on port 8083
- `func_process_input` (update_query) — input preprocessing hook that combines master-level and current queries

**[Detailed Guide →](./app_gateway.md)**

---

### Product Service

**File:** `examples/ecommerce/app_product_service.py`

This example deploys the product and inventory management microservice on port 8080. It configures a `ReActAgent` named `product_agent` equipped with two MCP tool clients: `product_db` for product database queries (product info, keyword search, category browsing) and `inventory_tools` for inventory management operations (stock checking, availability validation, warehouse distribution). The agent is marked as the master of this service and uses `HttpLLM` for reasoning about which tools to invoke.

**Key Components:**
- `HttpLLM` — LLM backend for product-related reasoning
- `StdioMCPClient` ("product_db") — MCP client for the product database tools
- `StdioMCPClient` ("inventory_tools") — MCP client for inventory management tools
- `ReActAgent` ("product_agent") — master agent handling product queries and inventory operations

**[Detailed Guide →](./app_product_service.md)**

---

### Order Service

**File:** `examples/ecommerce/app_order_service.py`

This example deploys the order management microservice on port 8081. It configures a `ReActAgent` named `order_agent` with the `order_tools` MCP client for order management operations (querying order details, user order history, order cancellation). The agent also has a sub-agent `payment_service` connected via `SSEOxyGent` to the payment service on port 8082, allowing it to delegate payment-related queries. This demonstrates a nested distributed pattern where one microservice agent can call another remote agent.

**Key Components:**
- `HttpLLM` — LLM backend for order-related reasoning
- `StdioMCPClient` ("order_tools") — MCP client for order management tools
- `SSEOxyGent` ("payment_service") — remote proxy to the payment service on port 8082
- `ReActAgent` ("order_agent") — master agent handling order queries with payment delegation

**[Detailed Guide →](./app_order_service.md)**

---

### Payment Service

**File:** `examples/ecommerce/app_payment_service.py`

This example deploys the payment processing microservice on port 8082. It configures a `ReActAgent` named `payment_service` with the `payment_tools` MCP client for handling payment-related operations such as querying payment status, payment details by order number, and providing payment method information. This is a leaf-level service with no sub-agents, serving as a focused single-domain agent that other services call remotely.

**Key Components:**
- `HttpLLM` — LLM backend for payment-related reasoning
- `StdioMCPClient` ("payment_tools") — MCP client for payment processing tools
- `ReActAgent` ("payment_service") — master agent handling payment queries

**[Detailed Guide →](./app_payment_service.md)**

---

### Logistics Service

**File:** `examples/ecommerce/app_logistics_service.py`

This example deploys the logistics and delivery microservice on port 8083. It configures a `ReActAgent` named `logistics_agent` equipped with two MCP tool clients: `logistics_tools` for package tracking and shipment status queries, and `delivery_tools` for delivery information management and shipping cost calculation. Like the payment service, this is a leaf-level service focused on a single domain, callable by the gateway agent via SSE.

**Key Components:**
- `HttpLLM` — LLM backend for logistics-related reasoning
- `StdioMCPClient` ("logistics_tools") — MCP client for logistics tracking tools
- `StdioMCPClient` ("delivery_tools") — MCP client for delivery management tools
- `ReActAgent` ("logistics_agent") — master agent handling logistics and delivery queries

**[Detailed Guide →](./app_logistics_service.md)**
