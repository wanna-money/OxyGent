# 设置自定义日志

**源文件:** `examples/backend/demo_logger_setup.py`

## 概述

本示例演示如何使用 `setup_logging` 工具函数在 OxyGent 中配置自定义日志。示例展示了如何获取 logger 实例并在智能体钩子函数中使用它进行调试和请求处理监控。此模式适用于需要统一格式化结构化日志的生产环境部署。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`

## 运行方式

```bash
python -m examples.backend.demo_logger_setup
```

## 代码详解

### 配置

```python
from oxygent.log_setup import setup_logging
logger = setup_logging()
```

`setup_logging()` 函数初始化并返回一个已配置的 logger 实例。该 logger 使用 OxyGent 的日志配置（格式、级别、处理器）。

### 钩子函数

```python
def update_query(oxy_request: OxyRequest) -> OxyRequest:
    query = oxy_request.get_query()
    logger.info(f"The current query is: {query}")
    return oxy_request
```

`update_query` 函数是一个 `func_process_input` 钩子，在智能体处理之前以 INFO 级别记录传入的查询。这使得在应用日志中可以进行请求追踪。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | 从环境变量获取的标准 LLM 凭证 |
| `master_agent` | `ChatAgent` | `func_process_input=update_query` -- 记录每个传入查询 |

### 入口函数

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="hello")
```

## 核心概念

- **setup_logging**：来自 `oxygent.log_setup` 的工具函数，初始化 OxyGent 日志系统并返回可在自定义代码中使用的 logger。
- **在钩子中使用日志**：如 `func_process_input` 这样的钩子函数是添加日志的理想位置，因为它们在请求生命周期的明确节点上执行。
- **OxyRequest.get_query()**：从请求中获取当前查询字符串，用于日志记录和调试。

## 预期行为

1. logger 在模块加载时初始化。
2. 当 Web 服务启动并处理初始查询 `"hello"` 时，钩子记录：`The current query is: hello`。
3. 通过 Web UI 输入的每个后续查询也以 INFO 级别记录。
4. 日志输出使用 `setup_logging()` 配置的格式和处理器。
