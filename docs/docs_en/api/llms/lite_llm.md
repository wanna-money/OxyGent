# LiteLLM

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

`LiteLLM` provides access to 100+ LLM providers (OpenAI, Anthropic, Google, Azure, AWS Bedrock, Ollama, etc.) through a single unified interface via the [LiteLLM](https://github.com/BerriAI/litellm) library. It uses `litellm.acompletion` under the hood and routes to the correct provider based on the `model_name` prefix (e.g. `anthropic/claude-sonnet-4-20250514`, `openai/gpt-4o`, `bedrock/anthropic.claude-3`). Requires the `litellm` package to be installed.

## Parameters

| Parameter     | Type / Allowed value | Default  | Description                                                                 |
| ------------- | -------------------- | -------- | --------------------------------------------------------------------------- |
| `model_name`  | `str`                | required | LiteLLM model identifier, e.g. `"anthropic/claude-sonnet-4-20250514"`.               |
| `api_key`     | `Optional[str]`      | `None`   | API key for the underlying provider. Falls back to provider-specific env vars when unset. |
| `base_url`    | `Optional[str]`      | `None`   | Optional base URL for a LiteLLM proxy server.                               |
| `drop_params` | `bool`               | `True`   | Silently drop provider-unsupported params (recommended).                    |

## Methods

| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                                        |
| ----------------------- | ----------------- | ------------- | ------------------------------------------------------------------------ |
| `init()`                | Yes               | `None`        | Import the `litellm` package and initialize the provider.                |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | Build payload, call `litellm.acompletion`, stream/collect the response.  |

## Inherited

Please refer to the [BaseLLM](./base_llm.md) class for inherited parameters and methods.

## Usage

```python
oxy.LiteLLM(
    name="lite_llm",
    model_name="anthropic/claude-sonnet-4-20250514",
    api_key="sk-...",
    drop_params=True,
)
```
