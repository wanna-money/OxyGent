# RemoteLLM
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
│   ├── [ActorLLM](./actor_llm.md)
│   ├── [LiteLLM](./lite_llm.md)
│   └── [MockLLM](./mock_llm.md)
└── [BaseTool](../tools/base_tools.md)
```

---

## Introduction

`RemoteLLM` extends `BaseLLM` for communicating with remote Large Language Model APIs. It provides a standardized interface for connecting to remote LLM services, handling API authentication, request formatting, and response parsing for OpenAI-compatible APIs.

## Parameters


| Parameter    | Type / Allowed value                                   | Default | Description                                                                |
| ------------ | ------------------------------------------------------ | ------- | -------------------------------------------------------------------------- |
| `api_key`    | `Optional[str]`                                        | `None`  | API key for authentication with the remote LLM service.                    |
| `base_url`   | `Optional[str]`                                        | `""`    | Base URL endpoint for the remote LLM API (required).                       |
| `model_name` | `Optional[str]`                                        | `""`    | Model identifier to use for requests (required).                           |
| `headers`    | `dict[str, str] \| Callable[[OxyRequest], dict[str, str]]` | `lambda: {}` | Extra HTTP headers or a callable that returns headers per request.   |

## Methods


| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                                                   |
| ----------------------- | ----------------- | ------------- | ----------------------------------------------------------------------------------- |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | **Abstract** -- subclasses implement the actual remote API call.                    |

## Inherited
 Please refer to the [BaseLLM](./base_llm.md) class for inherited parameters and methods.

## Usage

The class `RemoteLLM` must be inherited.
