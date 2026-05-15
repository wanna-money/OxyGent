# LLM Examples

This directory contains examples demonstrating how to configure and use different LLM backends in OxyGent, including parameter customization, system prompt control, local model loading, and Ollama integration.

---

## Examples

### Disable System Prompt

**File:** `examples/llms/demo_disable_system_prompt.py`

Demonstrates how to adapt OxyGent for LLM models that do not support system prompts. By setting `is_disable_system_prompt=True` on the `HttpLLM` instance, the framework will omit the system message from API calls, making it compatible with models that only accept user/assistant message roles. The example uses environment variables specific to a ChatRhino 750B model (`CHATRHINO_750B_API_KEY`, `CHATRHINO_750B_BASE_URL`, `CHATRHINO_750B_MODEL_NAME`) and pairs the LLM with a `ChatAgent` launched via web service.

**Key Components:**
- `HttpLLM` -- HTTP-based LLM client with `is_disable_system_prompt=True`
- `ChatAgent` -- simple conversational agent
- Environment variables for model-specific credentials

**[Detailed Guide →](./demo_disable_system_prompt.md)**

---

### Reset LLM Parameters

**File:** `examples/llms/demo_reset_llm_params.py`

Shows how to reset default LLM parameters and override them with custom values to accommodate specific model requirements. The example calls `Config.set_llm_config({})` to clear all default LLM parameters (which may include settings incompatible with certain models like GPT-5), then configures the `HttpLLM` with explicit `llm_params={"thinking": False, "stream": False}`. Instead of launching a web service, it directly calls the LLM via `mas.call()` with a manually constructed message list, demonstrating programmatic LLM invocation outside an agent context.

**Key Components:**
- `Config.set_llm_config({})` -- clears all default LLM parameters
- `HttpLLM` -- configured with explicit `llm_params` overrides
- `mas.call()` -- direct Oxy component invocation without an agent

**[Detailed Guide →](./demo_reset_llm_params.md)**

---

### Local LLM

**File:** `examples/llms/demo_local_llm.py`

Demonstrates how to use a locally loaded language model instead of a remote API. The `LocalLLM` class is instantiated with a `model_path` pointing to a local model directory (e.g., a Hugging Face model). This LLM is then paired with a `ChatAgent` and launched as a web service. This setup is useful for offline or air-gapped environments, or when using fine-tuned models stored on disk.

**Key Components:**
- `LocalLLM` -- loads and runs a language model from a local file path
- `ChatAgent` -- conversational agent backed by the local model

**[Detailed Guide →](./demo_local_llm.md)**

---

### Ollama Integration

**File:** `examples/llms/demo_ollama.py`

Shows how to connect OxyGent to an Ollama-served model. An `HttpLLM` is configured with `base_url` pointing to the local Ollama API endpoint (`http://localhost:11434/api/chat`) and `model_name` set to the desired Ollama model. No API key is needed since Ollama runs locally. The example directly invokes the LLM via `mas.call()` with a user message, demonstrating the simplest possible integration with Ollama's chat API.

**Key Components:**
- `HttpLLM` -- configured with Ollama's local API endpoint
- `mas.call()` -- direct LLM invocation for testing connectivity

**[Detailed Guide →](./demo_ollama.md)**
