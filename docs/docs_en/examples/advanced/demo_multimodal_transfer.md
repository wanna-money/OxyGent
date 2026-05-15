# Multimodal Transfer Between Agents

**Source:** `examples/advanced/demo_multimodal_transfer.py`

## Overview

This example demonstrates how to combine a vision-language model (VLM) agent with an image-generation tool in a multi-agent setup. The master agent can delegate image understanding to a vision agent and image creation to an image generation tool, enabling a workflow where one agent analyzes an image and another generates a new one based on the analysis.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Environment variables for VLM: `DEFAULT_VLM_API_KEY`, `DEFAULT_VLM_BASE_URL`, `DEFAULT_VLM_MODEL_NAME`
- The VLM endpoint must support multimodal (image + text) inputs

## How to Run

```bash
python -m examples.advanced.demo_multimodal_transfer
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_vlm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from VLM env vars; `is_multimodal_supported=True`, `is_convert_url_to_base64=True` |
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from standard LLM env vars |
| `image_gen_tools` | `preset_tools.image_gen_tools` | Built-in preset image generation tool hub |
| `vision_agent` | `ChatAgent` | `desc="一个图片理解工具"` (an image understanding tool), `llm_model="default_vlm"` |
| `master_agent` | `ReActAgent` | `is_master=True`, `sub_agents=["vision_agent"]`, `tools=["image_gen_tools"]`, `llm_model="default_llm"` |

**VLM Configuration:**

- `is_multimodal_supported=True` -- Tells the framework this LLM accepts image inputs alongside text.
- `is_convert_url_to_base64=True` -- Automatically converts image URLs to base64-encoded data before sending to the model.

### Entry Point

`main()` creates a `MAS` context and starts the web service with `first_query="这是什么，生成一张卡通的"` ("What is this? Generate a cartoon version."). The user is expected to upload an image via the web UI. The master agent will delegate to `vision_agent` for understanding and then use `image_gen_tools` to generate a cartoon version.

## Key Concepts

- **Multimodal LLM** -- An LLM configured with `is_multimodal_supported=True` that can process both text and image inputs.
- **Base64 Conversion** -- `is_convert_url_to_base64=True` automatically converts image URLs to inline base64 data for models that require this format.
- **Agent Collaboration** -- The master agent (text-only LLM) orchestrates between a vision sub-agent (VLM) and image generation tools, creating a pipeline from image understanding to image creation.
- **preset_tools.image_gen_tools** -- A built-in FunctionHub providing image generation capabilities.

## Expected Behavior

1. The web service starts on `127.0.0.1:8080`.
2. The user uploads an image (or one is provided via the web UI).
3. The master agent delegates to `vision_agent` to understand the image content.
4. The master agent then uses `image_gen_tools` to generate a cartoon version based on the description.
5. The generated cartoon image is returned to the user.
