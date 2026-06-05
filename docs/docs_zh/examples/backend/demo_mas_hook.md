# MAS 级钩子：过滤器与拦截器

**源文件:** `examples/backend/demo_mas_hook.py`

## 概述

本示例演示 MAS 级请求钩子：`func_filter` 用于修改传入的 payload，`func_interceptor` 用于完全拦截请求。这些钩子在请求到达任何智能体之前运行，非常适合在网关层面实现认证、授权、请求增强和速率限制。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`

## 运行方式

```bash
python -m examples.backend.demo_mas_hook
```

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
```

全局设置所有智能体的默认 LLM 模型名称，使各个智能体无需单独指定 `llm_model`。

### 钩子函数

**过滤器函数：**
```python
def func_filter(payload):
    print(payload)
    payload["group_data"] = {"user_pin": "123456"}
    return payload
```

过滤器函数接收原始传入的 payload，打印用于调试，注入包含 `user_pin` 字段的 `group_data`，然后返回修改后的 payload。这演示了请求增强 -- 例如从会话令牌中提取用户身份并附加到请求上。

**拦截器函数：**
```python
def func_interceptor(payload):
    print(payload)
    return {"code": 403, "message": "Permission denied."}
```

拦截器函数同样接收 payload，但不是修改它，而是返回一个错误响应字典。当拦截器返回非 `None` 值时，请求被短路，返回值直接作为响应发送给客户端。这演示了对未授权访问的请求拦截。

**注意：** 本示例中两个钩子同时注册，这意味着拦截器会阻止所有请求。在实际应用中，你应在拦截器内部使用条件逻辑（如检查认证令牌）来决定是拦截还是放行请求。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | 标准 LLM 凭证 |
| `master_agent` | `ChatAgent` | 使用全局配置的 `default_llm` |

### 入口函数

```python
async with MAS(
    oxy_space=oxy_space,
    func_filter=func_filter,
    func_interceptor=func_interceptor,
) as mas:
    await mas.start_web_service(first_query="hello")
```

两个钩子作为参数传递给 `MAS` 构造函数。

## 核心概念

- **func_filter**：MAS 级钩子，在处理之前修改传入的 payload。它接收并返回 payload 字典。用于请求增强（添加元数据、规范化字段）。支持同步和异步函数。
- **func_interceptor**：MAS 级钩子，可以短路请求处理。如果返回非 `None` 值，该值会立即返回给客户端，请求不会到达任何智能体。用于认证和授权。支持同步和异步函数。
- **钩子执行顺序**：拦截器在过滤器之前运行。如果拦截器阻止了请求，过滤器不会执行。
- **Config.set_agent_llm_model**：为所有智能体设置默认 LLM 模型名称，当所有智能体共享同一模型时减少样板代码。

> OxyGent 中所有 `func_*` 钩子函数均支持同步和异步函数。同步函数会在初始化时自动包装为异步函数。

## 预期行为

1. Web 服务在 `127.0.0.1:8080` 上启动。
2. 当请求到达时，拦截器打印 payload 并返回 `403 Permission denied` 响应。
3. 请求永远不会到达智能体；客户端直接收到错误响应。
4. 要查看过滤器的效果，需移除或有条件地绕过拦截器。
