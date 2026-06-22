# MCP 工具自定义 Headers 示例

**源文件:** `examples/tools/demo_mcp_with_headers.py`

## 概述

本示例演示了通过 `StreamableMCPClient` 向远程 MCP 工具服务器传递自定义 HTTP Headers 的三种策略。Headers 可以在客户端上静态指定、通过 `shared_data` 动态传入，或从前端请求中继承透传。示例运行了三个独立的 MAS 实例分别展示每种方式，并说明了多个 Headers 来源重叠时的优先级顺序。

## 前置条件

- 环境变量（在 `.env` 或终端中设置）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥
  - `DEFAULT_LLM_BASE_URL` -- LLM API 的基础 URL
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符
- 在 `http://127.0.0.1:8000/mcp` 运行一个支持接收 HTTP Headers 的 MCP 服务器（如兼容 `StreamableMCPClient` 的服务器，需提供 `power` 工具）

## 运行方式

```bash
python -m examples.tools.demo_mcp_with_headers
```

## 代码详解

### 配置

定义了三个独立的 `oxy_space` 配置，分别演示不同的 Headers 传递策略。

### 组件（`oxy_space`）

#### `oxy_space1` -- 静态 Headers

```python
oxy.StreamableMCPClient(
    name="time_tools",
    server_url="http://127.0.0.1:8000/mcp",
    headers={"key1": "value1"},
)
```

Headers 直接设置在 `StreamableMCPClient` 上。该客户端发起的每次 MCP 调用都会在 HTTP 请求头中包含 `{"key1": "value1"}`。

#### `oxy_space2` -- 通过 `shared_data` 动态传入 Headers

```python
oxy.StreamableMCPClient(
    name="time_tools",
    server_url="http://127.0.0.1:8000/mcp",
    headers={"key1": "value1"},
    is_dynamic_headers=True,
)
```

设置 `is_dynamic_headers=True` 后，客户端会在调用时从 `OxyRequest` 的 `shared_data["headers"]` 字段读取额外的 Headers。本示例中通过 payload 的 `shared_data` 传入 `{"key2": "value2"}`。

#### `oxy_space3` -- 继承前端请求 Headers

```python
oxy.StreamableMCPClient(
    name="time_tools",
    server_url="http://127.0.0.1:8000/mcp",
    headers={"key1": "value1"},
    is_dynamic_headers=True,
    is_inherit_headers=True,
)
```

设置 `is_inherit_headers=True` 后，客户端会将原始前端 HTTP 请求（如浏览器或 API 客户端）的 Headers 透传给 MCP 服务器。适用于传播认证令牌或会话标识符等场景。

### 入口点

`main()` 协程依次运行三个 MAS 实例：

1. **静态 Headers** -- 通过 `mas.call()` 直接调用 `power` 工具，使用静态 Headers。
2. **动态 Headers** -- 通过 `mas.chat_with_agent()` 发送包含 `shared_data.headers` 的 payload。
3. **继承 Headers** -- 启动 Web 服务，使前端请求的 Headers 可用于透传。

## 核心概念

- **静态 Headers**（`headers` 参数）-- 在客户端实例化时配置的固定 Headers，每次 MCP 请求都会发送。
- **动态 Headers**（`is_dynamic_headers=True`）-- 运行时从请求 payload 的 `shared_data["headers"]` 中读取，允许按请求自定义 Headers。
- **继承 Headers**（`is_inherit_headers=True`）-- 将原始前端 HTTP 请求的 Headers 透明转发到 MCP 服务器，实现认证令牌、链路追踪 ID 等的透传。
- **Headers 优先级** -- 当多个来源的 Headers 存在同名 key 时，优先级为：**前端请求 Headers > `shared_data` 中的 Headers > 客户端静态 Headers**。高优先级的来源会覆盖低优先级的值。
- **`mas.call()`** -- 直接调用指定名称的 Oxy 组件（工具或 LLM），不经过智能体的推理循环。适用于脚本化和测试场景。

## 预期行为

1. **第一个 MAS**（`oxy_space1`）：直接调用 `power` 工具，传入 `n=2, m=3`，发送 `{"key1": "value1"}` 作为 Headers。工具计算 2^3 = 8。
2. **第二个 MAS**（`oxy_space2`）：智能体处理查询"2的3次方是多少"，动态 Headers `{"key2": "value2"}` 与静态 `{"key1": "value1"}` 合并发送。
3. **第三个 MAS**（`oxy_space3`）：Web 服务启动，智能体调用 MCP 工具时会连同静态和动态 Headers 一起透传前端请求的 Headers。
