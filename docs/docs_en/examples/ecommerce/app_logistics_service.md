# E-Commerce Logistics Service

**Source:** `examples/ecommerce/app_logistics_service.py`

## Overview

This file defines the **logistics service**, one of four backend microservices in the e-commerce multi-agent system. Running on port 8083, it provides a `ReActAgent` equipped with logistics tracking and delivery management MCP tools. It handles package tracking by tracking number or order ID, delivery information retrieval, and shipping method recommendations with cost calculations.

## Prerequisites

- Environment variables (in `.env` or exported):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider.
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM endpoint.
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier.
- **uv** must be installed (used to run the MCP tool servers).
- No other services need to be running first -- this service has no downstream dependencies.

### Startup Order (in the full e-commerce system)

This service can be started independently. In the full system, it should be started before the gateway:

1. **Port 8083** -- Start this logistics service.
2. **Port 8085** -- Then start `app_gateway.py`.

## How to Run

```bash
python -m examples.ecommerce.app_logistics_service
```

The service will be available at `http://127.0.0.1:8083`.

## Code Walkthrough

### Configuration

```python
Config.set_app_name("logistics-service")
Config.set_server_port(8083)
```

Sets the app name to `logistics-service` and binds to port **8083**.

### Components (`oxy_space`)

| Component | Type | Purpose |
|---|---|---|
| `default_llm` | `HttpLLM` | Shared LLM backend with `temperature=0.01` and `semaphore=4`. |
| `logistics_tools` | `StdioMCPClient` | Runs `mcp_servers/logistics_tools.py` via `uv`. Provides: `track_package` (track by tracking number) and `track_by_order` (track by order ID). Uses in-memory mock data for shipments. |
| `delivery_tools` | `StdioMCPClient` | Runs `mcp_servers/delivery_tools.py` via `uv`. Provides: `get_delivery_info` (delivery details by order ID) and `get_delivery_methods` (available shipping methods by city and weight with cost calculation). |
| `logistics_agent` | `ReActAgent` | The master agent (`is_master=True`) for this service. Uses both `logistics_tools` and `delivery_tools` to answer logistics and delivery queries through LLM-driven reasoning. |

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service()
```

Starts the web service on port 8083 with no pre-filled query.

## Key Concepts

- **Domain-specific microservice** -- This service encapsulates all logistics-related functionality (tracking, delivery info, shipping methods) behind a single agent. The gateway accesses it as an opaque `SSEOxyGent`, decoupling the logistics domain from other concerns.
- **Multiple MCP tool clients** -- A single agent can use tools from multiple MCP servers. Here, `logistics_tools` handles package tracking while `delivery_tools` handles delivery management, but both are exposed to the same `logistics_agent`.
- **Mock data** -- The MCP servers use in-memory dictionaries simulating a real database. Available mock data includes tracking info for `JD1234567890` (ORDER001, in transit) and `JD1234567891` (ORDER002, delivered), plus delivery info for ORDER001 and ORDER002.

## Expected Behavior

1. When called by the gateway, the logistics agent can answer queries like:
   - "Track package JD1234567890" -- Returns full tracking history showing the package in transit.
   - "What is the delivery status of ORDER002?" -- Returns delivery info showing the order was delivered.
   - "What delivery methods are available for Province A, 2kg?" -- Returns available methods including Standard, Express, Next Day, and Same Day delivery with calculated fees.
2. The agent uses ReAct reasoning to determine which tool to call based on the user's query.
3. Tracking history includes timestamps, locations, and status descriptions for each transit event.
