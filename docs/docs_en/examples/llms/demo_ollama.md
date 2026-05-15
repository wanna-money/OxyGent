# Ollama Integration Demo

**Source:** `examples/llms/demo_ollama.py`

## Overview

This example demonstrates how to connect OxyGent to a locally running Ollama instance. Ollama provides a simple way to run open-source LLMs locally with an HTTP API. By pointing an `HttpLLM` at Ollama's chat endpoint, any Ollama-hosted model can be used as the LLM backend for OxyGent agents.

## Prerequisites

- **Ollama** installed and running locally (see [ollama.com](https://ollama.com))
- At least one model pulled in Ollama (e.g., `ollama pull llama3`)
- Ollama serving on its default port (`http://localhost:11434`)
- Python 3.10+ with project dependencies installed

**Note:** No API key is required -- Ollama runs locally and does not need authentication by default.

## How to Run

1. Start Ollama (if not already running):
   ```bash
   ollama serve
   ```

2. Pull a model if needed:
   ```bash
   ollama pull llama3
   ```

3. Update the `model_name` in the source code to match your pulled model:
   ```python
   model_name="llama3",  # or your chosen model
   ```

4. Run the example:
   ```bash
   python -m examples.llms.demo_ollama
   ```

## Code Walkthrough

### Configuration

```python
oxy.HttpLLM(
    name="default_llm",
    base_url="http://localhost:11434/api/chat",
    model_name="ollama_model_name",
)
```

The `HttpLLM` is configured with Ollama's chat API endpoint (`/api/chat`). No `api_key` is provided since Ollama does not require authentication. The `model_name` should match an Ollama model you have pulled locally.

### Components (`oxy_space`)

Only a single component:

1. **`HttpLLM("default_llm")`** -- An HTTP-based LLM pointing to the local Ollama server.

No agent is defined. The LLM is called directly to demonstrate the connection.

### Entry Point

The `main()` coroutine creates a MAS and calls the LLM directly:

```python
await mas.call(
    callee="default_llm",
    arguments={"messages": [{"role": "user", "content": "hello"}]},
)
```

This sends a single user message to the Ollama model and receives the response.

## Key Concepts

- **Ollama** -- An application for running open-source LLMs locally with a simple HTTP API. Supports models like LLaMA, Mistral, Phi, Gemma, and many others.
- **HttpLLM with local endpoints** -- `HttpLLM` is not limited to cloud APIs. Any HTTP-compatible LLM endpoint (including local servers) can be used by setting the appropriate `base_url`.
- **No API key** -- When connecting to local services like Ollama, the `api_key` parameter can be omitted.
- **Direct LLM invocation** -- Using `mas.call()` to invoke the LLM directly demonstrates that LLMs are standalone callable components in OxyGent, independent of agents.

## Expected Behavior

1. The MAS initializes and connects to the Ollama server at `http://localhost:11434/api/chat`.
2. The message `"hello"` is sent to the specified Ollama model.
3. The model generates a response locally.
4. The response is returned and printed/logged by the framework.
