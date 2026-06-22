# 使用 global_data 作为 MAS 级持久化存储

**源文件:** `examples/backend/demo_global_data.py`

## 概述

本示例演示如何使用 `global_data` 作为持久化的 MAS 级键值存储，使数据在多次请求间保持存在。示例实现了一个自定义的 `CounterAgent`，每次调用时在 `global_data` 中递增计数器，展示了智能体如何读写共享状态。此模式适用于维护跨请求的状态，如计数器、缓存或所有智能体需要访问的配置。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`

## 运行方式

```bash
python -m examples.backend.demo_global_data
```

## 代码详解

### 自定义智能体：CounterAgent

```python
class CounterAgent(BaseAgent):
    async def execute(self, oxy_request: OxyRequest):
        cnt = oxy_request.get_global_data("counter", 0) + 1
        oxy_request.set_global_data("counter", cnt)

        return OxyResponse(
            state=OxyState.COMPLETED,
            output=f"This MAS has been called {cnt} time(s).",
            oxy_request=oxy_request,
        )
```

`CounterAgent` 继承 `BaseAgent` 并重写 `execute` 方法。每次调用时：
1. 从 `global_data` 读取当前计数器值（默认为 0）。
2. 递增计数器并写回。
3. 返回包含当前计数的 `OxyResponse`。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | 标准 LLM 凭证（已包含但 CounterAgent 不直接使用） |
| `master_agent` | `CounterAgent` | `is_master=True` -- 将其标记为 `chat_with_agent` 的入口点 |

### 入口函数

```python
async with MAS(oxy_space=oxy_space) as mas:
    r1 = await mas.chat_with_agent({"query": "first"})
    print(r1.output)  # "This MAS has been called 1 time(s)."

    r2 = await mas.chat_with_agent({"query": "second"})
    print(r2.output)  # "This MAS has been called 2 time(s)."

    print("Current global_data:", mas.global_data)
```

## 核心概念

- **global_data 持久化**：与 `shared_data`（请求级）不同，`global_data` 在整个 MAS 实例的生命周期内持久化，并在所有请求间共享。
- **通过 BaseAgent 自定义智能体**：你可以通过继承 `BaseAgent` 并实现 `execute` 方法来创建自定义智能体。这使你无需依赖 LLM 驱动的推理即可完全控制智能体的逻辑。
- **OxyResponse**：智能体返回的标准响应对象。包含 `state`（如 `OxyState.COMPLETED`）、`output` 字符串和用于追踪的 `oxy_request`。
- **从 MAS 读取 global_data**：可以直接查看 `mas.global_data` 属性来了解全局存储的当前状态。

## 预期行为

1. 第一次调用：计数器初始化为 1，输出为 `"This MAS has been called 1 time(s)."`。
2. 第二次调用：计数器递增为 2，输出为 `"This MAS has been called 2 time(s)."`。
3. 两次调用完成后，`mas.global_data` 字典显示 `{"counter": 2}`。
