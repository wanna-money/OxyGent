# Multimodal Agent

**Source:** `examples/advanced/demo_multimodal.py`

## Overview

This example demonstrates how to configure a vision-language model (VLM) for multimodal input, allowing a ChatAgent to process both text and image inputs. It shows two usage patterns: a web-service mode where users upload images via the UI, and a programmatic test mode that constructs multimodal messages directly.

## Prerequisites

- Environment variables for VLM: `DEFAULT_VLM_API_KEY`, `DEFAULT_VLM_BASE_URL`, `DEFAULT_VLM_MODEL_NAME`
- The VLM endpoint must support multimodal (image + text) inputs
- For the `test()` function: a file named `test_pic.png` in the working directory

## How to Run

```bash
python -m examples.advanced.demo_multimodal
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_vlm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from VLM env vars; `is_multimodal_supported=True`, `is_convert_url_to_base64=True`, `base64_image_prefix="data:image/jpeg"` |
| `vision_agent` | `ChatAgent` | `llm_model="default_vlm"` |

**VLM Configuration Details:**

- `is_multimodal_supported=True` -- Enables the framework to handle image content in messages.
- `is_convert_url_to_base64=True` -- Converts image URLs (including local file paths) to base64-encoded data.
- `base64_image_prefix="data:image/jpeg"` -- Sets the MIME type prefix for base64-encoded images, required by some model APIs.

### Entry Point (Web Mode)

`main()` creates a `MAS` context and starts the web service with `first_query="What is this?"`. The user uploads an image through the web UI, and the vision agent analyzes it.

### Test Function (Programmatic Mode)

`test()` demonstrates how to construct multimodal messages programmatically:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": "./test_pic.png"}},
        {"type": "text", "text": "What is this?"},
    ]},
]
await mas.call(callee="default_vlm", arguments={"messages": messages})
```

This calls the VLM directly (not through an agent) with a structured multimodal message containing both an image and a text prompt.

## Key Concepts

- **Multimodal LLM Configuration** -- Three flags (`is_multimodal_supported`, `is_convert_url_to_base64`, `base64_image_prefix`) work together to enable image understanding in the LLM.
- **ChatAgent** -- A simple agent that forwards the conversation directly to the LLM without tool-calling or ReAct reasoning, ideal for straightforward Q&A or image understanding.
- **Direct LLM Invocation** -- `mas.call(callee="default_vlm", ...)` can call an LLM component directly, bypassing the agent layer, useful for low-level control over message formatting.

## Expected Behavior

1. The web service starts on `127.0.0.1:8080`.
2. The user uploads an image via the web UI.
3. The vision agent passes the image and the question "What is this?" to the VLM.
4. The VLM analyzes the image and returns a textual description.
