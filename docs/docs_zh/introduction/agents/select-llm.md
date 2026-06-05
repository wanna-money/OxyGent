# 如何调用LLM模型？

OxyGent所指的LLM是传统的LLM形式，它支持输入一个字符串并输出一个字符串。您可以通过`oxy.HttpLLM`或者`oxy.OpenAILLM`调用模型。

## 如何选择 LLM 类型？

| 场景 | 推荐类 | 关键参数 |
|------|--------|----------|
| 云端 API（DeepSeek、通义千问、Gemini 等） | `oxy.HttpLLM` | `api_key`, `base_url`, `model_name` |
| OpenAI 或 OpenAI 兼容接口 | `oxy.OpenAILLM` | `api_key`, `base_url`, `model_name` |
| Ollama 本地部署模型 | `oxy.HttpLLM` | `base_url`（不传 api_key） |
| HuggingFace 本地模型 | `oxy.LocalLLM` | `model_path`, `device_map` |
| 测试/开发（无需真实 LLM） | `oxy.MockLLM` | `func_mock_process` |

## 调用一般模型

```python
import os

oxy.HttpLLM(
    name="default_llm",
    api_key=os.getenv("DEFAULT_LLM_API_KEY"),
    base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
    model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    llm_params={"temperature": 0.01},
    semaphore=4, # 并发量
    timeout=240, # 最大执行时间
),
```

对于常见的开源模型和闭源模型，OxyGent均支持以这种方式进行调用。
> OxyGent支持直接url调用和加后缀`/chat/completions`的模型调用。

## 调用OpenAI接口模型

对于支持OpenAI接口的模型，可以使用以下方法进行调用：

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

### OpenAILLM 特性

`OpenAILLM` 基于官方 AsyncOpenAI 客户端，适用于所有兼容 OpenAI 协议的 API。主要特性包括：

- **流式传输支持**：支持实时内容传递和增量消息转发。在流式传输过程中，会自动检测 `reasoning_content` 并用 `<think>` / `</think>` 标签包装推理内容，实时转发到前端。
- **动态配置合并**：配置从多个来源合并，优先级为：请求参数（最高） > 实例 LLM 参数 > 全局 LLM 配置。
- **统一响应格式**：对流式和非流式响应均提供统一的 `OxyResponse` 格式处理。

**额外参数**：`headers` — 支持 `dict[str, str]` 或 `Callable[[OxyRequest], dict[str, str]]`，用于传递额外的 HTTP 请求头。

## 调用ollama部署模型

如果您使用ollama在本地部署了模型，请使用以下方式进行调用：

```python
oxy.HttpLLM(                
    name="local_gemma",  
    # 注意不要传入api_key参数
    base_url="http://localhost:11434/api/chat", # 替换为本地的url接口
    model_name=os.getenv("DEFAULT_OLLAMA_MODEL"),   
    llm_params={"temperature": 0.2},    
    semaphore=1,              
    timeout=240,
),
```
### URL 自动补全规则

| 模型提供商 | `base_url` 示例 | 自动补全后缀 |
|-----------|----------------|-------------|
| Gemini | `https://generativelanguage.googleapis.com/v1beta` | `/models/{model_name}:generateContent` |
| OpenAI 协议 | `https://api.openai.com/v1` | `/chat/completions` |
| Ollama | `http://localhost:11434` | `/api/chat` |

> 如果您的 `base_url` 已经包含完整路径（如以 `/chat/completions` 结尾），OxyGent 不会重复添加后缀。

因此，请您注意以下内容，如果您遇到404问题，大概率是url错误导致的：
- 使用Gemini是可以直接传入模型api，例如`https://generativelanguage.googleapis.com/v1beta`
- 使用通用开源模型（DeepSeek, Qwen）时，即使api_key为EMPTY，也请您写在环境变量中并传入`oxy.HttpLLM`。
- 使用基于OpenAI协议的闭源模型（ChatGPT）时，请使用`oxy.OpenAILLM`。
- 使用ollama模型时，不要传入`api_key`参数。

## 使用 MockLLM 进行测试

`oxy.MockLLM` 不调用真实的 LLM API，而是返回预设的模拟输出。适用于开发调试和单元测试：

```python
oxy.MockLLM(
    name="mock_llm",
    func_mock_process=lambda oxy_request: "这是一个模拟回复，用于测试。",
),
```

`func_mock_process` 接收 `OxyRequest` 对象，返回字符串作为模拟的 LLM 输出。如果不传此参数，默认返回 `"output"`。

## 使用本地模型 (LocalLLM)

如果您需要使用本地部署的 HuggingFace 模型，可以使用 `oxy.LocalLLM`：

```python
oxy.LocalLLM(
    name="local_llm",
    model_path="/path/to/your/model",
    device_map="auto",
    dtype="bfloat16",
),
```

> LocalLLM 需要额外安装 `torch` 和 `transformers` 包。

## 常用参数设置
OxyGent支持细致设置模型参数，您可以在调用时或者在[设置](../getting-started/config.md)里设置LLM参数。以下是一些常用的参数列表：
- **category**: 始终为"llm"，表示这是LLM模型的配置。
- **timeout**: 最大执行时间，单位为秒。
- **llm_params**: 模型的额外参数（如温度设置等）。
- **is_send_think**: 是否向前端发送思考消息。
- **friendly_error_text**: 错误信息的用户友好提示。
- **is_multimodal_supported**: 模式是否支持多模态输入。
- **is_convert_url_to_base64**: 是否将媒体URL转换为base64格式。
- **max_image_pixels**: 图片处理的最大像素数。
- **max_video_size**: 视频处理的最大字节数。

OxyGent默认为每个agent提供单独的LLM。如果您需要配置统一的LLM，请参考[设置默认LLM](../getting-started/config.md)；如果您需要并行运行多种LLM，请参考[并行](../multi-agent/parallel.md)。

[上一章：和智能体交流](./chat-with-agent.md)
[下一章：预设提示词](./select-prompt.md)
[回到首页](../readme.md)

---

## 相关示例

- [Ollama 本地模型示例](../../examples/llms/demo_ollama.md) — 使用 Ollama 部署的本地模型
- [本地 LLM 示例](../../examples/llms/demo_local_llm.md) — 本地 LLM 的使用方法
- [LLM 参数重置示例](../../examples/llms/demo_reset_llm_params.md) — 动态设置 LLM 参数
- [禁用系统 Prompt 示例](../../examples/llms/demo_disable_system_prompt.md) — 禁用 LLM 的系统 Prompt
