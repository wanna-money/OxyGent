# 电商商品服务

**源文件:** `examples/ecommerce/app_product_service.py`

## 概述

本文件定义了电商多智能体系统中四个后端微服务之一的**商品服务**。它运行在默认端口 8080，提供一个配备两套 MCP 工具的 `ReActAgent`：商品信息工具和库存管理工具。该服务处理商品查询、分类浏览、库存检查、库存可用性验证、仓库分布查询、低库存预警、补货建议以及预留库存释放（用于订单取消时）。

## 前置条件

- 环境变量（在 `.env` 文件中配置或直接导出）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥。
  - `DEFAULT_LLM_BASE_URL` -- LLM 端点的基础 URL。
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符。
- 必须安装 **uv**（用于运行 MCP 工具服务器）。
- 无需先启动其他服务——本服务没有下游依赖。

### 启动顺序（在完整电商系统中）

本服务可以独立启动。在完整系统中：

1. **端口 8080** -- 首先启动本商品服务。
2. 按需启动其他服务，最后启动网关。

## 运行方式

```bash
python -m examples.ecommerce.app_product_service
```

服务启动后可通过 `http://127.0.0.1:8080` 访问。

## 代码详解

### 配置

```python
Config.set_app_name("product-service")
Config.set_server_port(8080)
```

将应用名称设为 `product-service`，并绑定到 **8080** 端口。

### 组件（`oxy_space`）

| 组件 | 类型 | 用途 |
|---|---|---|
| `default_llm` | `HttpLLM` | 共享的 LLM 后端，`temperature=0.01`，`semaphore=4`。 |
| `product_db` | `StdioMCPClient` | 通过 `uv` 运行 `mcp_servers/product_tools.py`。提供：`get_product_info`（按 ID 或名称查询商品详情）和 `get_products_by_category`（按分类列出商品）。模拟商品目录包含 3 个商品：商品 A（电子产品，5999 元）、商品 B（计算设备，12999 元）、商品 C（配件，899 元）。 |
| `inventory_tools` | `StdioMCPClient` | 通过 `uv` 运行 `mcp_servers/inventory_tools.py`。提供六个工具：`check_inventory`、`check_stock_availability`、`release_reserved_stock`、`get_low_stock_products`、`get_inventory_by_warehouse` 和 `get_restock_suggestions`。跨四个仓库跟踪库存。 |
| `product_agent` | `ReActAgent` | 本服务的主代理（`is_master=True`）。使用 `product_db` 和 `inventory_tools` 通过 LLM 驱动的推理处理所有商品和库存查询。 |

### 入口点

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service()
```

在 8080 端口启动 Web 服务，无预填查询。

## 核心概念

- **双工具集代理** -- 商品代理在一个代理下整合了商品目录工具和库存管理工具。LLM 根据用户查询决定调用哪个工具，为整个商品领域提供统一接口。
- **库存管理** -- 库存工具分别跟踪总库存、可用库存和预留库存。预留库存代表已分配给尚未发货的订单的商品。当订单取消时，`release_reserved_stock` 将单位数从预留移回可用。
- **仓库分布** -- 库存分布在四个仓库（A、B、C、D）中。`get_inventory_by_warehouse` 工具允许查询特定仓库的库存水平。
- **智能补货** -- `get_restock_suggestions` 工具为低于低库存阈值的商品生成补货建议，包括建议数量、供应商信息和优先级。
- **名称到 ID 解析** -- 商品工具和库存工具都支持通过商品名称（如"商品 A"）查询，除了商品 ID（如"PROD001"）外，使用内部映射字典进行解析。

## 预期行为

1. 当被网关调用或直接访问时，商品代理可以回答以下查询：
   - "介绍一下商品 A" -- 返回商品详情：PROD001，价格 5999，电子产品类别，品牌 A，评分 4.8。
   - "显示所有计算设备" -- 返回该分类下的商品列表。
   - "查看 PROD001 的库存" -- 返回库存详情：总计 1500，可用 1200，预留 300，仓库分布和库存状态。
   - "商品 B 有 100 件现货吗？" -- 检查可用性并确认库存充足（可用 650 件）。
   - "为 ORDER003 释放 2 件 PROD003" -- 释放预留库存，增加可用库存并减少预留库存。
   - "哪些商品库存不足？" -- 返回低于阈值的商品（如果有）。
   - "有什么补货建议？" -- 返回包含数量、供应商和优先级的建议。
2. `release_reserved_stock` 工具专门在网关触发的订单取消工作流中使用。
