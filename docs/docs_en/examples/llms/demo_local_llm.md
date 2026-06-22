# Local LLM Demo

**Source:** `examples/llms/demo_local_llm.py`

## Overview

This example demonstrates how to use a locally hosted language model with OxyGent via the `LocalLLM` class. Instead of connecting to a remote API, `LocalLLM` loads a model from a local file path (e.g., a Hugging Face model directory). This is useful for offline deployments, privacy-sensitive applications, or when using custom fine-tuned models.

## Prerequisites

- A local model directory at the path specified in `model_path` (e.g., a Hugging Face Transformers-compatible model)
- Appropriate model-loading dependencies installed (e.g., `transformers`, `torch`)
- Python 3.10+ with project dependencies installed
- Sufficient system resources (GPU/RAM) for the model

**Note:** No API keys or environment variables are required since the model runs locally.

## How to Run

Before running, update the `model_path` in the source code to point to your actual local model directory:

```python
oxy.LocalLLM(
    name="default_llm",
    model_path="/path/to/your_model",  # <-- Change this
)
```

Then run:

```bash
python -m examples.llms.demo_local_llm
```

## Code Walkthrough

### Configuration

```python
oxy.LocalLLM(
    name="default_llm",
    model_path="/path/to/your_model",
)
```

`LocalLLM` takes a `model_path` pointing to a local model directory. The framework handles model loading and inference internally. No API key or base URL is needed.

### Components (`oxy_space`)

1. **`LocalLLM("default_llm")`** -- A locally loaded language model.
2. **`ChatAgent("master_agent")`** -- A chat agent that uses the local LLM for generating responses. The agent references the LLM by its name `"default_llm"`.

### Entry Point

The `main()` coroutine creates a MAS and starts the web service with the initial query `"hello"`. The chat agent processes queries using the locally loaded model.

## Key Concepts

- **LocalLLM** -- An LLM implementation that loads and runs models locally rather than calling a remote API. It supports Hugging Face Transformers-compatible model directories.
- **Offline operation** -- Since the model runs locally, no internet connection or API key is required after the model files are downloaded.
- **Resource requirements** -- Local models require significant system resources. Ensure you have adequate GPU memory (for GPU inference) or RAM (for CPU inference) for your chosen model.
- **Model path** -- The path should point to a directory containing the model weights, tokenizer config, and other necessary files (e.g., a standard Hugging Face model directory).

## Expected Behavior

1. The framework loads the model from the specified local path (this may take time depending on model size).
2. The web server starts at `http://127.0.0.1:8080`.
3. The agent receives the query "hello".
4. The local model generates a response, which is displayed in the web UI.
5. Subsequent queries are processed entirely locally without any external API calls.
