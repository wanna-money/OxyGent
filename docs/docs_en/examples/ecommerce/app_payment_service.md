# E-Commerce Payment Service

**Source:** `examples/ecommerce/app_payment_service.py`

## Overview

This file defines the **payment service**, the simplest of the four backend microservices in the e-commerce multi-agent system. Running on port 8082, it provides a `ReActAgent` with payment-related MCP tools that can query payment status by payment ID or order ID and list supported payment methods. It is called by the order service on port 8081.

## Prerequisites

- Environment variables (in `.env` or exported):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider.
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM endpoint.
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier.
- **uv** must be installed (used to run the MCP tool server).
- No other services need to be running first -- this is a leaf service.

### Startup Order (in the full e-commerce system)

This service has no downstream dependencies. Start it before the order service:

1. **Port 8082** -- Start this payment service first.
2. **Port 8081** -- Then start `app_order_service.py` (which depends on this service).

## How to Run

```bash
python -m examples.ecommerce.app_payment_service
```

The service will be available at `http://127.0.0.1:8082`.

## Code Walkthrough

### Configuration

```python
Config.set_app_name("payment-service")
Config.set_server_port(8082)
```

Sets the app name to `payment-service` and binds to port **8082**.

### Components (`oxy_space`)

| Component | Type | Purpose |
|---|---|---|
| `default_llm` | `HttpLLM` | Shared LLM backend with `temperature=0.01` and `semaphore=4`. |
| `payment_tools` | `StdioMCPClient` | Runs `mcp_servers/payment_tools.py` via `uv`. Provides two tools: `query_payment_status` (payment details by payment ID or order ID) and `get_payment_methods` (list of supported payment methods with fee rates and limits). |
| `payment_service` | `ReActAgent` | The master agent (`is_master=True`) for this service. Uses `payment_tools` to answer payment-related queries through LLM-driven reasoning. |

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service()
```

Starts the web service on port 8082 with no pre-filled query.

## Key Concepts

- **Leaf service pattern** -- Like the time agent in the distributed example, the payment service is a leaf node with no downstream dependencies. It demonstrates the smallest deployable unit in a microservice architecture.
- **Dual-key lookup** -- The `query_payment_status` tool accepts either a payment ID (e.g., `PAY001`) or an order ID (e.g., `ORDER001`) and resolves it internally using the `ORDER_TO_PAYMENT` mapping. This simplifies the calling agent's logic since it does not need to know the payment ID.
- **Mock payment data** -- Two payment records are available: PAY001 (for ORDER001, 5999.00, paid via method A) and PAY002 (for ORDER002, 12999.00, paid via method B). ORDER003 has no associated payment record (it is "Pending Payment").

## Expected Behavior

1. When called by the order service or accessed directly, the payment agent can answer queries like:
   - "What is the payment status of ORDER001?" -- Returns payment details: PAY001, amount 5999.00, paid via payment method A.
   - "Show payment PAY002" -- Returns payment details for the specified payment ID.
   - "What payment methods are supported?" -- Returns three methods (A, B, C) with their fee rates, maximum amounts, and descriptions.
2. Querying a payment for ORDER003 will return an error since no payment record exists for that order (it is still pending).
