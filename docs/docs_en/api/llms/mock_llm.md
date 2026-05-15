# MockLLM

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

`MockLLM` is a deterministic LLM stub for unit testing. It returns configurable mock responses without calling any real model, making it ideal for tests that need predictable LLM behavior.

## Parameters

| Parameter           | Type / Allowed value | Default | Description                                                                 |
| ------------------- | -------------------- | ------- | --------------------------------------------------------------------------- |
| `func_mock_process` | `Callable`           | `None`  | User-supplied async mock function. Defaults to internal `_mock_process`.    |

## Methods

| Method                        | Coroutine (async) | Return Value  | Purpose (concise)                                               |
| ----------------------------- | ----------------- | ------------- | --------------------------------------------------------------- |
| `_mock_process(oxy_request)`  | Yes               | `str`         | Default mock: sleeps 1s and returns the literal string `"output"`. |
| `_execute(oxy_request)`       | Yes               | `OxyResponse` | Calls `func_mock_process` and wraps the result in `OxyResponse`. |

## Inherited

Please refer to the [BaseLLM](./base_llm.md) class for inherited parameters and methods.

## Usage

```python
# Default mock — always returns "output"
oxy.MockLLM(name="mock_llm")

# Custom mock
async def my_mock(oxy_request):
    return "custom response"

oxy.MockLLM(name="mock_llm", func_mock_process=my_mock)
```
