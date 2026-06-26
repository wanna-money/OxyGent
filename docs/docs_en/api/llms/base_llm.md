# BaseLLM
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

`BaseLLM` is the abstract base class for all Large Language Model implementations in the OxyGent system. It provides common functionality including multimodal input processing, think message extraction and forwarding, Base64 conversion for media URLs, token usage tracking, and error handling with user-friendly messages.

## Parameters

| Parameter                  | Type / Allowed value | Default                                                              | Description                                                   |
| -------------------------- | -------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------- |
| `category`                 | `str`                | `"llm"`                                                              | Category flag identifying the object as an LLM.               |
| `semaphore`                | `int`                | `Config.get_llm_semaphore()`                                         | Concurrency limit for parallel LLM calls.                     |
| `timeout`                  | `float`              | `Config.get_llm_timeout()`                                           | Maximum execution time in seconds.                            |
| `llm_params`               | `dict`               | `{}`                                                                 | Additional provider-specific LLM parameters.                  |
| `is_send_think`            | `bool`               | `Config.get_message_is_send_think()`                                 | Whether to send think messages to the frontend.               |
| `friendly_error_text`      | `Optional[str]`      | `"Sorry, I seem to have encountered a problem. Please try again."`   | User-friendly error message displayed when exceptions occur.  |
| `is_multimodal_supported`  | `bool`               | `False`                                                              | Whether to support multimodal input.                          |
| `is_convert_url_to_base64` | `bool`               | `False`                                                              | Whether to convert image/video URLs to base64 format.         |
| `max_image_pixels`         | `int`                | `10000000`                                                           | Maximum pixel count allowed per image.                        |
| `max_video_size`           | `int`                | `12582912` (12 MB)                                                   | Maximum video file size in bytes.                             |
| `max_file_size_bytes`      | `int`                | `2097152` (2 MB)                                                     | Maximum non-media file size for base64 embedding.             |
| `base64_image_prefix`      | `str`                | `"data:image"`                                                       | Prefix used to detect base64-encoded image data URIs.         |
| `base64_video_prefix`      | `str`                | `"data:video"`                                                       | Prefix used to detect base64-encoded video data URIs.         |
| `is_disable_system_prompt` | `bool`               | `False`                                                              | Whether to omit the system prompt from the LLM call.          |

## Methods

| Method                            | Coroutine (async) | Return Value  | Purpose (concise)                                                                     |
| --------------------------------- | ----------------- | ------------- | ------------------------------------------------------------------------------------- |
| `_get_messages(oxy_request)`      | Yes               | `list`        | Preprocess messages for multimodal input; convert URLs to base64 if enabled.          |
| `_execute(oxy_request)`           | Yes               | `OxyResponse` | **Abstract** -- must be implemented by subclasses.                                    |
| `_post_send_message(oxy_response)`| Yes               | `None`        | Extract and forward thinking process messages to the frontend.                        |
| `_after_execute(oxy_response)`    | Yes               | `OxyResponse` | Aggregate token usage and serialize to dict.                                          |
| `_build_payload(oxy_request, payload)` | No           | `dict`        | Merge global LLM config, instance params, and request args into the payload.          |
| `_build_token_usage(usage_data, messages, output)` | No | `TokenUsage` | Build token usage with fallback to estimation.                                       |

## Inherited
 Please refer to the [Oxy](../agent/base_oxy.md) class for inherited parameters and methods.

## Usage

The class `BaseLLM` must be inherited.
