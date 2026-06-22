# E-Commerce Gateway Agent

**Source:** `examples/ecommerce/app_gateway.py`

## Overview

This file defines the **gateway agent**, the central orchestrator of a five-service e-commerce multi-agent system. Running on port 8085, it acts as the single entry point for all user requests, routing them to the appropriate domain-specific remote agents: product (port 8080), order (port 8081), payment (port 8082, accessed via the order service), and logistics (port 8083). It also includes a custom `WorkflowAgent` that handles the complex cross-domain process of cancelling an order.

## Prerequisites

- Environment variables (in `.env` or exported):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider.
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM endpoint.
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier.
- **All four backend services** must be running before starting the gateway. See [Startup Order](#startup-order) below.

### Startup Order

The services form a dependency chain. Start them in this order:

1. **Port 8080** -- Product service: `python -m examples.ecommerce.app_product_service`
2. **Port 8082** -- Payment service: `python -m examples.ecommerce.app_payment_service`
3. **Port 8081** -- Order service (depends on payment at 8082): `python -m examples.ecommerce.app_order_service`
4. **Port 8083** -- Logistics service: `python -m examples.ecommerce.app_logistics_service`
5. **Port 8085** -- Gateway (depends on all above): `python -m examples.ecommerce.app_gateway`

## How to Run

```bash
# Terminal 1 -- Product service
python -m examples.ecommerce.app_product_service

# Terminal 2 -- Payment service
python -m examples.ecommerce.app_payment_service

# Terminal 3 -- Order service
python -m examples.ecommerce.app_order_service

# Terminal 4 -- Logistics service
python -m examples.ecommerce.app_logistics_service

# Terminal 5 -- Gateway
python -m examples.ecommerce.app_gateway
```

Open the web UI at `http://127.0.0.1:8085`.

## Code Walkthrough

### Configuration

```python
Config.set_server_port(8085)
```

The gateway runs on port **8085**, separate from all backend services.

### Components (`oxy_space`)

| Component | Type | Purpose |
|---|---|---|
| `default_llm` | `HttpLLM` | Shared LLM backend for the gateway's local agents. |
| `cancel_order_workflow` | `WorkflowAgent` | A workflow agent that orchestrates order cancellation across the order and product services. Uses `trust_mode=True` (skips LLM confirmation) and has a 20-second `timeout`. |
| `gateway_agent` | `ReActAgent` | The master agent (`is_master=True`). Routes user queries to the appropriate sub-agent or workflow based on intent. Has access to `order_agent`, `product_agent`, `logistics_agent`, and `cancel_order_workflow`. |
| `product_agent` | `SSEOxyGent` | Remote proxy to the product service on port 8080. Handles product queries, inventory checks, and stock management. |
| `order_agent` | `SSEOxyGent` | Remote proxy to the order service on port 8081. Handles order queries, order history, and order cancellation. |
| `logistics_agent` | `SSEOxyGent` | Remote proxy to the logistics service on port 8083. Handles package tracking, delivery info, and shipping method queries. |

### Hook Functions / Callbacks

#### `update_query(oxy_request: OxyRequest)`

A pre-processing function (`func_process_input`) attached to the `product_agent`, `order_agent`, and `logistics_agent` SSE proxies. It enriches the request by combining the original user query (from `master_level=True`) with the current sub-query, ensuring the remote service has full context:

```python
oxy_request.set_query(f"user query is {user_query}\ncurrent query is {current_query}")
```

#### `cancel_order_workflow(oxy_request: OxyRequest)`

The workflow function for the `cancel_order_workflow` agent. It performs a multi-step cross-service operation:

1. **Calls `order_agent`** -- Sends the cancellation request to the order service, which cancels the order and returns the order details (including product IDs and quantities).
2. **Calls `product_agent`** -- Sends the order agent's response to the product service, which releases the reserved inventory (calls `release_reserved_stock`).
3. **Returns a combined result** -- Merges the order cancellation and inventory update results into a single response.

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(
        first_query="Because the user doesn't want it anymore, so to cancel ORDER003 order, please help me cancel this order",
    )
```

Starts the web service on port 8085 with a demo query that triggers the order cancellation workflow.

## Key Concepts

- **Multi-service architecture** -- The gateway pattern separates concerns: each domain (products, orders, payments, logistics) runs as an independent service. The gateway provides a unified interface and handles cross-domain orchestration.
- **WorkflowAgent for cross-domain operations** -- Operations like order cancellation span multiple domains (order + inventory). The `WorkflowAgent` with a custom `func_workflow` provides deterministic orchestration of these cross-cutting concerns.
- **func_process_input** -- A hook that transforms the `OxyRequest` before it is sent to a remote agent. Here it appends the original user query so the remote service has sufficient context to act.
- **trust_mode=True** -- On the `cancel_order_workflow`, this bypasses any LLM confirmation steps, allowing the workflow to execute its steps directly without asking the user for approval at each stage.
- **SSEOxyGent** -- Each remote service is represented as an `SSEOxyGent` in the gateway's `oxy_space`. This makes remote services indistinguishable from local agents at the routing level.

## Expected Behavior

1. The web UI opens at `http://127.0.0.1:8085` with a demo query to cancel ORDER003.
2. The `gateway_agent` recognizes this as an order cancellation task and routes it to `cancel_order_workflow`.
3. The workflow calls `order_agent` (port 8081), which cancels ORDER003 (status changes from "Pending Payment" to "Cancelled") and returns the product details (Product C x2, Product A x1).
4. The workflow then calls `product_agent` (port 8080), which releases the reserved stock for the cancelled items.
5. The combined result is returned to the user showing both the cancellation confirmation and the inventory update.
6. Users can also ask product questions ("What is Product A?"), order questions ("Show me ORDER001"), or logistics questions ("Track JD1234567890"), and the gateway will route to the appropriate service.
