# HttpLLM
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

`HttpLLM` 是基于 HTTP 的 LLM 实现，通过 HTTP 与远程语言模型 API 进行通信。它支持遵循 OpenAI 兼容 API 标准的多种供应商，包括 OpenAI、Google Gemini 和 Ollama，并具备自动供应商检测和格式处理能力。

## 参数

| 参数            | 类型 / 允许值        | 默认值   | 描述                                                                 |
| --------------- | -------------------- | ------- | -------------------------------------------------------------------- |
| *无新增参数*     | --                   | --      | `HttpLLM` 未添加新字段；所有内容均继承自 `RemoteLLM`。                 |

## 方法

| 方法                    | 协程 (async) | 返回值        | 用途（简述）                                                                   |
| ----------------------- | ------------ | ------------- | ----------------------------------------------------------------------------- |
| `_execute(oxy_request)` | 是           | `OxyResponse` | 向远程 LLM API 发送 HTTP 请求，处理认证和响应解析。                              |

## 继承
 请参阅 [RemoteLLM](./remote_llm.md) 类了解继承的参数和方法。

## 用法

```python
oxy.HttpLLM(
    name="default_llm",
    api_key=os.getenv("DEFAULT_LLM_API_KEY"),
    base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
    model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    llm_params={"temperature": 0.01},
    semaphore=4,
)
```
