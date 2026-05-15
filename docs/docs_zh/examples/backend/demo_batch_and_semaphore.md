# 带并发控制的批量处理

**源文件:** `examples/backend/demo_batch_and_semaphore.py`

## 概述

本示例演示如何通过 MAS 运行批量查询，并对 LLM 和智能体分别设置并发限制（信号量）。此模式对于生产环境中需要并发处理大量请求、同时遵守速率限制或资源约束的场景至关重要。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`

## 运行方式

```bash
python -m examples.backend.demo_batch_and_semaphore
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `semaphore=4` -- 将 LLM 并发限制为 4 个同时请求 |
| `chat_agent` | `ChatAgent` | `semaphore=6` -- 将智能体并发限制为 6 个同时执行 |

信号量值定义了每个组件允许的最大并发执行数。在此配置中，即使智能体允许 6 个并发调用，每个调用在访问 LLM 时仍会受到 LLM 信号量 4 的进一步限制。

### 入口函数

```python
async with MAS(oxy_space=oxy_space) as mas:
    outs = await mas.start_batch_processing(["hello"] * 10, return_trace_id=True)
    [print(out) for out in outs]
```

- `start_batch_processing` 接受查询字符串列表并进行并发处理。
- `return_trace_id=True` 使每个结果包含 trace ID，用于调试和追踪。
- 示例发送了 10 个相同的 `"hello"` 查询。

## 核心概念

- **信号量（Semaphore）**：任何 Oxy 组件上的整数参数，限制同时运行的 `_execute()` 调用数量。其底层映射为 Python 的 `asyncio.Semaphore`。
- **批量处理**：`MAS.start_batch_processing()` 并发地将多个查询分发给主智能体，并收集所有结果。
- **分层并发控制**：信号量可以在智能体和 LLM 上独立设置。有效并发数为调用链中所有信号量的最小值。

## 预期行为

1. MAS 并发分发 10 个 `"hello"` 查询。
2. 最多 6 个智能体同时执行（智能体信号量）。
3. 最多 4 个 LLM 调用同时进行（LLM 信号量）。
4. 处理完成后，所有 10 个结果（每个包含 trace ID）被打印到控制台。
