# E-Commerce Product Service

**Source:** `examples/ecommerce/app_product_service.py`

## Overview

This file defines the **product service**, one of four backend microservices in the e-commerce multi-agent system. Running on the default port 8080, it provides a `ReActAgent` equipped with two sets of MCP tools: product information tools and inventory management tools. It handles product lookups, category browsing, inventory checks, stock availability, warehouse distribution queries, low-stock alerts, restock suggestions, and reserved stock release (used during order cancellation).

## Prerequisites

- Environment variables (in `.env` or exported):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider.
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM endpoint.
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier.
- **uv** must be installed (used to run the MCP tool servers).
- No other services need to be running first -- this service has no downstream dependencies.

### Startup Order (in the full e-commerce system)

This service can be started independently. In the full system:

1. **Port 8080** -- Start this product service first.
2. Start other services as needed, then the gateway last.

## How to Run

```bash
python -m examples.ecommerce.app_product_service
```

The service will be available at `http://127.0.0.1:8080`.

## Code Walkthrough

### Configuration

```python
Config.set_app_name("product-service")
Config.set_server_port(8080)
```

Sets the app name to `product-service` and binds to port **8080**.

### Components (`oxy_space`)

| Component | Type | Purpose |
|---|---|---|
| `default_name` | `HttpLLM` | Shared LLM backend with `temperature=0.01` and `semaphore=4`. |
| `product_db` | `StdioMCPClient` | Runs `mcp_servers/product_tools.py` via `uv`. Provides: `get_product_info` (product details by ID or name) and `get_products_by_category` (list products in a category). Mock catalog has 3 products: Product A (Electronics, 5999), Product B (Computing Devices, 12999), Product C (Accessories, 899). |
| `inventory_tools` | `StdioMCPClient` | Runs `mcp_servers/inventory_tools.py` via `uv`. Provides six tools: `check_inventory`, `check_stock_availability`, `release_reserved_stock`, `get_low_stock_products`, `get_inventory_by_warehouse`, and `get_restock_suggestions`. Tracks stock across four warehouses. |
| `product_agent` | `ReActAgent` | The master agent (`is_master=True`) for this service. Uses both `product_db` and `inventory_tools` to handle all product and inventory queries through LLM-driven reasoning. |

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service()
```

Starts the web service on port 8080 with no pre-filled query.

## Key Concepts

- **Dual-tool-set agent** -- The product agent combines product catalog tools and inventory management tools under a single agent. The LLM decides which tool to invoke based on the user's query, providing a unified interface for the entire product domain.
- **Inventory management** -- The inventory tools track total stock, available stock, and reserved stock separately. Reserved stock represents items allocated to orders that have not yet shipped. When an order is cancelled, `release_reserved_stock` moves units from reserved back to available.
- **Warehouse distribution** -- Inventory is distributed across four warehouses (A, B, C, D). The `get_inventory_by_warehouse` tool allows querying stock levels at a specific warehouse.
- **Smart restocking** -- The `get_restock_suggestions` tool generates restock recommendations for products below their low-stock threshold, including suggested quantities, supplier info, and priority levels.
- **Name-to-ID resolution** -- Both the product and inventory tools support lookup by product name (e.g., "Product A") in addition to product ID (e.g., "PROD001"), using an internal mapping dictionary.

## Expected Behavior

1. When called by the gateway or accessed directly, the product agent can answer queries like:
   - "Tell me about Product A" -- Returns product details: PROD001, price 5999, Electronics category, Brand A, 4.8 rating.
   - "Show all Computing Devices" -- Returns a list of products in that category.
   - "Check inventory for PROD001" -- Returns stock details: 1500 total, 1200 available, 300 reserved, warehouse distribution, and stock status.
   - "Is there enough stock for 100 units of Product B?" -- Checks availability and confirms sufficient stock (650 available).
   - "Release 2 units of PROD003 for ORDER003" -- Releases reserved stock, increasing available stock and decreasing reserved stock.
   - "Which products have low stock?" -- Returns products below their threshold (if any).
   - "What are the restock suggestions?" -- Returns suggestions with quantities, suppliers, and priorities.
2. The `release_reserved_stock` tool is specifically used during the order cancellation workflow triggered by the gateway.
