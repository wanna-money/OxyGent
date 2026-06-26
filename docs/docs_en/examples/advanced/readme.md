# Advanced Examples

This section covers advanced OxyGent features including multimodal agents, custom parsers, tool retrieval, execution control, and training data generation.

---

### Custom Agent Input Schema

**File:** `examples/advanced/demo_custom_agent_input_schema.py`

Demonstrates how to define a custom `input_schema` on a WorkflowAgent so that the master agent passes structured arguments instead of a plain query string. In this example the WorkflowAgent declares two required fields (`query` and `precision`) and implements a workflow function that returns pi to the requested number of decimal places. The master ReActAgent automatically formats its tool call to match the schema.

**Key Components:** `HttpLLM`, `ReActAgent`, `WorkflowAgent(input_schema)`

**[Detailed Guide →](./demo_custom_agent_input_schema.md)**

---

### Multimodal (Vision) Agent

**File:** `examples/advanced/demo_multimodal.py`

Shows how to build a ChatAgent that processes images using a vision-language model (VLM). The HttpLLM is configured with `is_multimodal_supported=True` and `is_convert_url_to_base64=True` so that image URLs or local file paths are automatically converted to base64-encoded payloads before being sent to the model. The agent can then answer questions about the content of the provided images.

**Key Components:** `HttpLLM(is_multimodal_supported, is_convert_url_to_base64)`, `ChatAgent`

**[Detailed Guide →](./demo_multimodal.md)**

---

### Multimodal Transfer

**File:** `examples/advanced/demo_multimodal_transfer.py`

Combines image understanding and image generation in a single multi-agent system. A vision-capable ChatAgent interprets an uploaded image, while a ReActAgent uses the preset `image_gen_tools` to generate new images (e.g., a cartoon version) based on the vision agent's description. Two separate HttpLLM instances serve the VLM and the text LLM respectively.

**Key Components:** `HttpLLM` (x2), `preset_tools.image_gen_tools`, `ChatAgent`, `ReActAgent`

**[Detailed Guide →](./demo_multimodal_transfer.md)**

---

### Trust Mode

**File:** `examples/advanced/demo_trust_mode.py`

Compares the behavior of `trust_mode=True` versus `trust_mode=False` on a ReActAgent. When trust mode is enabled, the agent automatically executes tool calls without waiting for user confirmation. When disabled, each tool call requires explicit approval. Both agents use the same StdioMCPClient time tool so the difference in execution flow is easy to observe.

**Key Components:** `HttpLLM`, `StdioMCPClient`, `ReActAgent(trust_mode=True/False)`

**[Detailed Guide →](./demo_trust_mode.md)**

---

### Continue / Restart Execution

**File:** `examples/advanced/demo_continue_exec.py`

Demonstrates how to continue or restart agent execution from an intermediate node using `restart_node_id`. After a first run completes, you can pass a `restart_node_id` (and optionally a `restart_node_output`) in the payload to replay from that specific point in the execution trace. This is useful for debugging, correcting intermediate results, or branching execution paths.

**Key Components:** `HttpLLM`, `StdioMCPClient`, `ReActAgent`, `restart_node_id`, `restart_node_output`

**[Detailed Guide →](./demo_continue_exec.md)**

---

### Send Message from Tool

**File:** `examples/advanced/demo_send_message_from_tool.py`

Shows how a FunctionHub tool can send messages back to the user and interrupt task execution mid-flight. The example defines a `calc_pi` tool that, after computing pi to the requested precision, calls `oxy_request.send_message()` to push the result to the frontend and then calls `oxy_request.break_task()` to halt the agent loop early. This pattern is useful when a tool produces the final answer directly and no further LLM reasoning is needed.

**Key Components:** `HttpLLM`, `FunctionHub`, `ReActAgent`, `oxy_request.send_message()`, `oxy_request.break_task()`

**[Detailed Guide →](./demo_send_message_from_tool.md)**

---

### GRPO-Style Resampling

**File:** `examples/advanced/demo_grpo_resample.py`

Illustrates how to replay LLM nodes from a completed task trace to generate multiple alternative answers, which can then be used as SFT (supervised fine-tuning) training data in a GRPO-style pipeline. The example first runs a multi-agent task, retrieves all LLM nodes from the trace using `get_task_info`, and then replays each node concurrently via `restart_node_id` to produce diverse outputs.

**Key Components:** `HttpLLM`, `preset_tools` (time, file, math), `ReActAgent` (x4), `get_task_info`, `restart_node_id`

**[Detailed Guide →](./demo_grpo_resample.md)**

---

### Custom LLM Response Parser

**File:** `examples/advanced/demo_custom_llm_parser.py`

Replaces the default JSON-based LLM response parser with a custom XML-based parser by setting `func_parse_llm_response` on a ReActAgent. The custom parser extracts tool calls and answers from XML tags (`<tool>`, `<answer>`) instead of JSON, returning structured `LLMResponse` objects with the appropriate `LLMState`. A matching XML-format prompt is provided to instruct the LLM. This is useful when working with models that produce non-standard output formats.

**Key Components:** `HttpLLM`, `StdioMCPClient` (x2), `ReActAgent(func_parse_llm_response)`, `LLMResponse`, `LLMState`

**[Detailed Guide →](./demo_custom_llm_parser.md)**

---

### Top-K Tool Retrieval

**File:** `examples/advanced/demo_top_k_tools.py`

Demonstrates automatic top-K tool retrieval using vector similarity. By setting `top_k_tools=N` on a ReActAgent, only the N most relevant tools (ranked by embedding similarity to the current query) are included in the LLM prompt on each turn. This reduces prompt size and improves tool selection accuracy when an agent has many tools registered. Requires a Vearch vector database and an embedding model to be configured.

**Key Components:** `HttpLLM`, `StdioMCPClient` (x2), `ReActAgent(top_k_tools=3)`, Vearch vector DB

**[Detailed Guide →](./demo_top_k_tools.md)**

---

### Runtime Oxy Management

**File:** `examples/advanced/demo_oxy_manage.py`

Demonstrates how to use the built-in `oxy_manage_tools` FunctionHub to dynamically manage the agent organization at runtime. A "doctor_agent" equipped with `oxy_manage_tools` can create new agents, assign tools, move Oxy instances between parents, and delete agents — all while the system is running. The example uses `first_query` with a `list[str]` to issue four sequential commands: creating a math agent, solving a math problem, reorganizing agents, and querying the time.

**Key Components:** `HttpLLM`, `preset_tools` (math, time, file), `ReActAgent` (x3), `preset_tools.oxy_manage_tools`, `first_query` as `list[str]`

**[Detailed Guide →](./demo_oxy_manage.md)**
