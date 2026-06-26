# LLM 示例

本目录包含了 OxyGent 中配置和使用不同 LLM 后端的示例，涵盖参数自定义、系统提示词控制、本地模型加载以及 Ollama 集成。

---

## 示例列表

### 禁用系统提示词

**文件:** `examples/llms/demo_disable_system_prompt.py`

演示了如何适配不支持系统提示词的 LLM 模型。通过在 `HttpLLM` 实例上设置 `is_disable_system_prompt=True`，框架在 API 调用时会省略 system 消息，从而兼容仅接受 user/assistant 消息角色的模型。本示例使用了 ChatRhino 750B 模型专用的环境变量（`CHATRHINO_750B_API_KEY`、`CHATRHINO_750B_BASE_URL`、`CHATRHINO_750B_MODEL_NAME`），并将该 LLM 与一个 `ChatAgent` 配合，以 Web 服务方式启动。

**核心组件:**
- `HttpLLM` -- 基于 HTTP 的 LLM 客户端，设置了 `is_disable_system_prompt=True`
- `ChatAgent` -- 简单的对话 Agent
- 模型专用的环境变量凭证配置

**[详细文档 →](./demo_disable_system_prompt.md)**

---

### 重置 LLM 参数

**文件:** `examples/llms/demo_reset_llm_params.py`

展示了如何重置默认的 LLM 参数并用自定义值覆盖，以适配特定模型的要求。示例调用 `Config.set_llm_config({})` 清除所有默认 LLM 参数（这些默认参数可能与 GPT-5 等特定模型不兼容），然后在 `HttpLLM` 上显式配置 `llm_params={"thinking": False, "stream": False}`。与启动 Web 服务不同，本示例通过 `mas.call()` 直接调用 LLM，手动构造消息列表，演示了在 Agent 上下文之外以编程方式调用 LLM 的方法。

**核心组件:**
- `Config.set_llm_config({})` -- 清除所有默认 LLM 参数
- `HttpLLM` -- 使用显式 `llm_params` 覆盖配置
- `mas.call()` -- 不通过 Agent 直接调用 Oxy 组件

**[详细文档 →](./demo_reset_llm_params.md)**

---

### 本地 LLM

**文件:** `examples/llms/demo_local_llm.py`

演示了如何使用本地加载的语言模型替代远程 API。`LocalLLM` 类通过 `model_path` 参数指向本地模型目录（例如 Hugging Face 模型）进行实例化，然后与一个 `ChatAgent` 配合，以 Web 服务方式启动。该配置适用于离线或隔离网络环境，或使用存储在磁盘上的微调模型的场景。

**核心组件:**
- `LocalLLM` -- 从本地文件路径加载并运行语言模型
- `ChatAgent` -- 由本地模型驱动的对话 Agent

**[详细文档 →](./demo_local_llm.md)**

---

### Ollama 集成

**文件:** `examples/llms/demo_ollama.py`

展示了如何将 OxyGent 连接到 Ollama 部署的模型。示例将 `HttpLLM` 的 `base_url` 配置为本地 Ollama API 端点（`http://localhost:11434/api/chat`），`model_name` 设置为所需的 Ollama 模型名称。由于 Ollama 在本地运行，无需配置 API 密钥。示例通过 `mas.call()` 直接向 LLM 发送用户消息，演示了与 Ollama Chat API 最简单的集成方式。

**核心组件:**
- `HttpLLM` -- 配置了 Ollama 本地 API 端点
- `mas.call()` -- 直接调用 LLM 以测试连通性

**[详细文档 →](./demo_ollama.md)**

---

### LiteLLM 集成

**文件:** `examples/llms/demo_litellm.py`

演示了如何在 OxyGent 中通过 LiteLLM 使用任意 LLM 提供商。示例将 `LiteLLM` 组件的 `model_name` 按照 LiteLLM 的 `provider/model` 命名规范进行配置（如 `anthropic/claude-sonnet-4-20250514`）。API 密钥可以直接传入，也可以从对应提供商的环境变量中读取。`base_url` 可选配置，用于指向 LiteLLM 代理服务器以集中管理 API 密钥。示例将 LiteLLM 模型与一个 `ReActAgent` 配合，通过 `mas.call()` 发送一个简单的数学问题进行调用。

**核心组件:**
- `LiteLLM` -- 支持 100+ 提供商的统一 LLM 接口
- `ReActAgent` -- 由 LiteLLM 驱动的推理与行动智能体
- `mas.call()` -- 通过用户消息调用智能体

**[详细文档 →](./demo_litellm.md)**
