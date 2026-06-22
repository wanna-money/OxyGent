# OpenAILLM
---
该类在类层次结构中的位置：


```markdown
[Oxy](../agent/base_oxy.md)
├── [BaseFlow](../agent/base_flow.md)
├── [BaseLLM](./base_llm.md)
│   ├── [RemoteLLM](./remote_llm.md)
│   │   ├── [HttpLLM](./http_llm.md)
│   │   └── [OpenAILLM](./openai_llm.md)
│   ├── [LocalLLM](./local_llm.md)
│   └── [MockLLM](./mock_llm.md)
└── [BaseTool](../tools/base_tools.md)
```

---

## 简介

`OpenAILLM` 是 `RemoteLLM` 的具体实现，专为 OpenAI 语言模型设计。它使用官方 `AsyncOpenAI` 客户端以获得最佳性能和兼容性。该类支持所有 OpenAI 模型及兼容 API，处理 payload 构建、配置合并以及 OpenAI Chat Completion API 的响应处理。

## 参数

| 参数            | 类型 / 允许值        | 默认值   | 描述                                                                  |
| --------------- | -------------------- | ------- | --------------------------------------------------------------------- |
| *无新增参数*     | --                   | --      | `OpenAILLM` 未添加新字段；所有内容均继承自 `RemoteLLM`。                |

## 方法

| 方法                    | 协程 (async) | 返回值        | 用途（简述）                                                                        |
| ----------------------- | ------------ | ------------- | ---------------------------------------------------------------------------------- |
| `_execute(oxy_request)` | 是           | `OxyResponse` | 通过 AsyncOpenAI 客户端执行请求，支持流式传输和 reasoning_content。                   |

## 继承
 请参阅 [RemoteLLM](./remote_llm.md) 类了解继承的参数和方法。

## 用法

```python
oxy.OpenAILLM(
    name="default_llm",
    api_key=os.getenv("DEFAULT_LLM_API_KEY"),
    base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
    model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    llm_params={"temperature": 0.01},
    semaphore=4,
    timeout=240,
)
```
