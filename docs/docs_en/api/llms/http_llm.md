# HttpLLM
---
The position of the class is:


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

## Introduction

`HttpLLM` is an HTTP-based LLM implementation that communicates with remote language model APIs over HTTP. It supports various providers that follow OpenAI-compatible API standards, including OpenAI, Google Gemini, and Ollama, with automatic provider detection and format handling.

## Parameters

| Parameter       | Type / Allowed value | Default | Description                                                                      |
| --------------- | -------------------- | ------- | -------------------------------------------------------------------------------- |
| *None declared* | --                   | --      | `HttpLLM` adds no new fields; it inherits everything from `RemoteLLM`.           |

## Methods

| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                                                        |
| ----------------------- | ----------------- | ------------- | ---------------------------------------------------------------------------------------- |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | Execute an HTTP request to the remote LLM API with authentication and response parsing.  |

## Inherited
 Please refer to the [RemoteLLM](./remote_llm.md) class for inherited parameters and methods.

## Usage

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
