# 自定义 Elasticsearch 共享数据 Schema

**源文件:** `examples/backend/demo_custom_shared_data_schema.py`

## 概述

本示例演示如何为 `shared_data` 字段定义自定义的 Elasticsearch 映射，并在请求处理过程中填充数据。当你需要将结构化元数据（如用户身份信息）与对话 trace 一起持久化到 Elasticsearch 中以供后续查询和分析时，此模式非常有用。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Elasticsearch 实例（或使用本地回退的 `LocalEs`）

## 运行方式

```bash
python -m examples.backend.demo_custom_shared_data_schema
```

## 代码详解

### 配置

```python
Config.set_es_schema_shared_data(
    {
        "properties": {
            "user_pin": {"type": "keyword"},
            "user_name": {"type": "keyword"},
        }
    }
)
```

此调用自定义了 `shared_data` 的 Elasticsearch 映射。将 `user_pin` 和 `user_name` 声明为 `keyword` 字段后，即可在 Elasticsearch 中对这些字段进行精确匹配查询和聚合操作。

### 钩子函数

```python
def process_input(oxy_request: OxyRequest) -> OxyRequest:
    oxy_request.set_shared_data("user_pin", "123456")
    oxy_request.set_shared_data("user_name", "oxy")
    return oxy_request
```

`process_input` 函数是一个预执行钩子（`func_process_input`），在智能体执行之前将用户元数据注入到请求的 `shared_data` 中。这些数据将随 trace 一起存储到 Elasticsearch 中。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | 从环境变量获取的标准 LLM 凭证 |
| `master_agent` | `ReActAgent` | `func_process_input=process_input` -- 附加预处理钩子 |

### 入口函数

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="hello")
```

## 核心概念

- **自定义 ES shared_data schema**：`Config.set_es_schema_shared_data()` 允许你为 trace 文档上的 `shared_data` 字段定义 Elasticsearch 映射，实现结构化存储和查询。
- **shared_data**：挂载在 `OxyRequest` 上的按请求维度的键值存储。此处设置的数据会随 trace 持久化，并可被执行链中的所有组件访问。
- **func_process_input**：在智能体主执行逻辑之前运行的钩子函数。它接收并返回 `OxyRequest`，允许你丰富或转换请求内容。

## 预期行为

1. ES 映射被配置为包含 `user_pin` 和 `user_name` 作为 keyword 字段。
2. 每个请求中，`process_input` 钩子将 `shared_data` 填充为 `user_pin="123456"` 和 `user_name="oxy"`。
3. `ReActAgent` 处理查询，丰富后的 `shared_data` 随 trace 一起持久化到 Elasticsearch 中。
4. Web 服务以 `"hello"` 作为初始查询启动。
