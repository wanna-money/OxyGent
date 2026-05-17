# How to Call an LLM Model?

The LLM in OxyGent refers to the traditional LLM form, which supports taking a string as input and outputting a string. You can call models using `oxy.HttpLLM` or `oxy.OpenAILLM`.

## How to Choose an LLM Type?

| Scenario | Recommended Class | Key Parameters |
|----------|-------------------|----------------|
| Cloud API (DeepSeek, Qwen, Gemini, etc.) | `oxy.HttpLLM` | `api_key`, `base_url`, `model_name` |
| OpenAI or OpenAI-compatible API | `oxy.OpenAILLM` | `api_key`, `base_url`, `model_name` |
| 100+ providers via LiteLLM (Anthropic, Bedrock, Vertex, etc.) | `oxy.LiteLLM` | `model_name` (e.g. `anthropic/claude-sonnet-4-20250514`) |
| Ollama locally deployed model | `oxy.HttpLLM` | `base_url` (do not pass api_key) |
| HuggingFace local model | `oxy.LocalLLM` | `model_path`, `device_map` |
| Testing/Development (no real LLM needed) | `oxy.MockLLM` | `func_mock_process` |

## Calling General Models

```python
import os

oxy.HttpLLM(
    name="default_llm",
    api_key=os.getenv("DEFAULT_LLM_API_KEY"),
    base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
    model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    llm_params={"temperature": 0.01},
    semaphore=4, # concurrency limit
    timeout=240, # maximum execution time
),
```

OxyGent supports calling both common open-source and closed-source models in this way.
> OxyGent supports both direct URL calls and model calls with the `/chat/completions` suffix.

## Calling OpenAI-Compatible Models

For models that support the OpenAI interface, you can use the following method:

```python
oxy.OpenAILLM(
    name="default_llm",
    api_key=os.getenv("DEFAULT_LLM_API_KEY"),
    base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
    model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    llm_params={"temperature": 0.01},
    semaphore=4,
    timeout=240,
),
```

### OpenAILLM Features

`OpenAILLM` is built on the official AsyncOpenAI client and works with all OpenAI-compatible APIs. Key features include:

- **Streaming support**: Supports real-time content delivery and incremental message forwarding. During streaming, it automatically detects `reasoning_content` and wraps reasoning content with `<think>` / `</think>` tags, forwarding it to the frontend in real time.
- **Dynamic config merging**: Configuration is merged from multiple sources with the following priority: request params (highest) > instance LLM params > global LLM config.
- **Unified response format**: Provides unified `OxyResponse` format handling for both streaming and non-streaming responses.

**Additional parameter**: `headers` — accepts `Dict[str, str]` or `Callable[[OxyRequest], Dict[str, str]]` for passing extra HTTP request headers.

## Using LiteLLM (100+ Providers)

[LiteLLM](https://github.com/BerriAI/litellm) provides a unified interface to 100+ LLM providers. Install with `pip install litellm`.

```python
oxy.LiteLLM(
    name="default_llm",
    model_name="anthropic/claude-sonnet-4-20250514",
    # api_key="sk-...",  # or set ANTHROPIC_API_KEY env var
)
```

LiteLLM routes to the correct provider based on the model name prefix:

| Provider | `model_name` Example |
|----------|---------------------|
| Anthropic | `anthropic/claude-sonnet-4-20250514` |
| OpenAI | `openai/gpt-4o` |
| Google | `gemini/gemini-2.5-flash` |
| AWS Bedrock | `bedrock/anthropic.claude-3-sonnet` |
| Azure OpenAI | `azure/gpt-4o` |
| Ollama | `ollama/llama3` |

When `api_key` is not provided, LiteLLM falls back to provider-specific environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.). You can also point at a LiteLLM proxy server via `base_url`.

> LiteLLM requires `pip install litellm` separately. It is not included in the default requirements.

## Calling Ollama-Deployed Models

If you have deployed a model locally using Ollama, use the following approach:

```python
oxy.HttpLLM(                
    name="local_gemma",  
    # Note: do not pass the api_key parameter
    base_url="http://localhost:11434/api/chat", # replace with your local URL endpoint
    model_name=os.getenv("DEFAULT_OLLAMA_MODEL"),   
    llm_params={"temperature": 0.2},    
    semaphore=1,              
    timeout=240,
),
```
### URL Auto-Completion Rules

| Model Provider | `base_url` Example | Auto-Completed Suffix |
|---------------|-------------------|----------------------|
| Gemini | `https://generativelanguage.googleapis.com/v1beta` | `/models/{model_name}:generateContent` |
| OpenAI Protocol | `https://api.openai.com/v1` | `/chat/completions` |
| Ollama | `http://localhost:11434` | `/api/chat` |

> If your `base_url` already contains the full path (e.g., ends with `/chat/completions`), OxyGent will not append the suffix again.

Therefore, please note the following. If you encounter a 404 error, it is most likely caused by an incorrect URL:
- When using Gemini, you can pass the model API directly, e.g., `https://generativelanguage.googleapis.com/v1beta`
- When using common open-source models (DeepSeek, Qwen), even if the api_key is EMPTY, please include it in the environment variables and pass it to `oxy.HttpLLM`.
- When using closed-source models based on the OpenAI protocol (ChatGPT), please use `oxy.OpenAILLM`.
- When using Ollama models, do not pass the `api_key` parameter.

## Using MockLLM for Testing

`oxy.MockLLM` does not call a real LLM API. Instead, it returns a preset mock output. It is suitable for development debugging and unit testing:

```python
oxy.MockLLM(
    name="mock_llm",
    func_mock_process=lambda oxy_request: "This is a mock response for testing.",
),
```

`func_mock_process` receives an `OxyRequest` object and returns a string as the simulated LLM output. If this parameter is not provided, it returns `"output"` by default.

## Using Local Models (LocalLLM)

If you need to use a locally deployed HuggingFace model, you can use `oxy.LocalLLM`:

```python
oxy.LocalLLM(
    name="local_llm",
    model_path="/path/to/your/model",
    device_map="auto",
    dtype="bfloat16",
),
```

> LocalLLM requires additional installation of the `torch` and `transformers` packages.

## Common Parameter Settings
OxyGent supports fine-grained model parameter configuration. You can set LLM parameters either at call time or in [Config](../getting-started/config.md). Here are some commonly used parameters:
- **category**: Always "llm", indicating this is an LLM model configuration.
- **timeout**: Maximum execution time in seconds.
- **llm_params**: Additional model parameters (such as temperature settings, etc.).
- **is_send_think**: Whether to send thinking messages to the frontend.
- **friendly_error_text**: User-friendly error message text.
- **is_multimodal_supported**: Whether the model supports multimodal input.
- **is_convert_url_to_base64**: Whether to convert media URLs to base64 format.
- **max_image_pixels**: Maximum pixel count for image processing.
- **max_video_size**: Maximum byte size for video processing.

OxyGent provides a separate LLM for each agent by default. If you need to configure a unified LLM, please refer to [Setting a Default LLM](../getting-started/config.md); if you need to run multiple LLMs in parallel, please refer to [Parallel](../multi-agent/parallel.md).

[Previous: Chat with an Agent](./chat-with-agent.md)
[Next: Preset Prompts](./select-prompt.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Ollama Local Model Example](../../examples/llms/demo_ollama.md) -- Using a locally deployed model with Ollama
- [Local LLM Example](../../examples/llms/demo_local_llm.md) -- How to use a local LLM
- [LLM Parameter Reset Example](../../examples/llms/demo_reset_llm_params.md) -- Dynamically setting LLM parameters
- [Disable System Prompt Example](../../examples/llms/demo_disable_system_prompt.md) -- Disabling the LLM's system prompt
