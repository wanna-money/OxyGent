# E-Commerce Order Service

**Source:** `examples/ecommerce/app_order_service.py`

## Overview

This file defines the **order service**, one of four backend microservices in the e-commerce multi-agent system. Running on port 8081, it provides a `ReActAgent` that manages order queries and order cancellation using MCP order tools. It also connects to the payment service on port 8082 as a sub-agent, enabling the order agent to answer payment-related questions for any given order.

## Prerequisites

- Environment variables (in `.env` or exported):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider.
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM endpoint.
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier.
- **uv** must be installed (used to run the MCP tool server).
- **The payment service** (`app_payment_service.py`) must already be running on `http://127.0.0.1:8082` before starting this service.

### Startup Order (in the full e-commerce system)

1. **Port 8082** -- Start the payment service first: `python -m examples.ecommerce.app_payment_service`
2. **Port 8081** -- Then start this order service: `python -m examples.ecommerce.app_order_service`
3. **Port 8085** -- Then start the gateway (if running the full system).

## How to Run

```bash
# Terminal 1 -- Payment service (must be running first)
python -m examples.ecommerce.app_payment_service

# Terminal 2 -- Order service
python -m examples.ecommerce.app_order_service
```

The service will be available at `http://127.0.0.1:8081`.

## Code Walkthrough

### Configuration

```python
Config.set_app_name("order-service")
Config.set_server_port(8081)
```

Sets the app name to `order-service` and binds to port **8081**.

### Components (`oxy_space`)

| Component | Type | Purpose |
|---|---|---|
| `default_name` | `HttpLLM` | Shared LLM backend with `temperature=0.01` and `semaphore=4`. |
| `order_tools` | `StdioMCPClient` | Runs `mcp_servers/order_tools.py` via `uv`. Provides three tools: `query_order` (order details by ID), `query_user_orders` (all orders for a user), and `cancel_order` (cancel with reason and timestamp). |
| `payment_service` | `SSEOxyGent` | Remote proxy to the payment service on port 8082. Allows the order agent to delegate payment-related queries (payment status, payment methods) to the payment microservice. |
| `order_agent` | `ReActAgent` | The master agent (`is_master=True`) for this service. Uses `order_tools` for order management and can delegate to `payment_service` for payment queries. |

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service()
```

Starts the web service on port 8081 with no pre-filled query.

## Key Concepts

- **Service composition** -- The order service demonstrates how one microservice can depend on another. By including `payment_service` as a sub-agent, the order agent can transparently handle queries like "What is the payment status of ORDER001?" by delegating to the payment service.
- **Order lifecycle** -- The MCP order tools simulate a complete order management system with three sample orders in different states: ORDER001 (Shipped), ORDER002 (Delivered), ORDER003 (Pending Payment). The `cancel_order` tool only allows cancellation of orders in "Processing" or "Pending Payment" status.
- **Cross-service agent hierarchy** -- Within this service, `order_agent` is the master. But when called from the gateway, it acts as a sub-agent. OxyGent's `is_master=True` flag only designates the entry point within a single MAS instance.

## Expected Behavior

1. When called by the gateway or accessed directly, the order agent can answer queries like:
   - "Show me ORDER001" -- Returns order details including products, total, status, and shipping address.
   - "List all orders for USER003" -- Returns all orders placed by that user.
   - "Cancel ORDER003 because the user doesn't want it" -- Cancels the order (changes status from "Pending Payment" to "Cancelled"), records the reason and timestamp, and returns the product details.
   - "What is the payment status of ORDER001?" -- Delegates to the payment service, which returns payment details (PAY001, paid via payment method A).
2. Attempting to cancel ORDER001 (status "Shipped") will fail with a message explaining that shipped orders cannot be cancelled.
