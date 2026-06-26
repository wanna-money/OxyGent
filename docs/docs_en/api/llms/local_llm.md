# LocalLLM

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

`LocalLLM` loads a HuggingFace transformer model from disk and runs inference locally. It requires `torch` and `transformers` to be installed. The model and tokenizer are loaded during `init()` and reused across requests.

## Parameters

| Parameter    | Type / Allowed value | Default    | Description                                       |
| ------------ | -------------------- | ---------- | ------------------------------------------------- |
| `model_path` | `str`                | `""`       | Path to the HuggingFace model directory.          |
| `device_map` | `str`                | `"auto"`   | Device mapping strategy for model placement.      |
| `dtype`      | `str`                | `"bfloat16"` | Data type for model weights (e.g., `"bfloat16"`, `"float16"`). |

## Methods

| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                              |
| ----------------------- | ----------------- | ------------- | -------------------------------------------------------------- |
| `init()`                | Yes               | `None`        | Load the model and tokenizer from `model_path`.                |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | Build payload, tokenize, generate text, and return the result. |

## Inherited

Please refer to the [BaseLLM](./base_llm.md) class for inherited parameters and methods.

## Usage

```python
oxy.LocalLLM(
    name="local_llm",
    model_path="/path/to/huggingface/model",
    device_map="auto",
    dtype="bfloat16",
)
```
