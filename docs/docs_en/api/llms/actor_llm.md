# ActorLLM

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

`ActorLLM` runs inference on a local transformer model via a Ray actor (or a `ray_adapter` shim when Ray is not installed). It extracts system/user messages from the standard message format and delegates generation to the actor.

## Parameters

| Parameter           | Type / Allowed value | Default | Description                                                                                         |
| ------------------- | -------------------- | ------- | --------------------------------------------------------------------------------------------------- |
| `name`              | `str`                | `"llm"` | Identifier for the LLM instance.                                                                    |
| `actor_llm`         | `Any`                | `None`  | A Ray actor handle (or compatible object) that exposes an `agent_generate_one_step` method.          |
| `actor_llm_timeout` | `float`              | `0.0`   | Timeout in seconds for the actor call. `0` means no timeout. Overridable via `OXYGENT_ACTOR_LLM_TIMEOUT` env var. |
| `raise_on_error`    | `bool`               | `True`  | Whether to raise a `RuntimeError` on generation failure. When `False`, returns an `OxyResponse` with `FAILED` state instead. |

## Methods

| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                                                        |
| ----------------------- | ----------------- | ------------- | ---------------------------------------------------------------------------------------- |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | Extract system/user messages, call the actor's `agent_generate_one_step`, and return the result. |

## Inherited

Please refer to the [BaseLLM](./base_llm.md) class for inherited parameters and methods.

## Usage

```python
oxy.ActorLLM(
    name="actor_llm",
    actor_llm=your_ray_actor_handle,
    actor_llm_timeout=120,
)
```
