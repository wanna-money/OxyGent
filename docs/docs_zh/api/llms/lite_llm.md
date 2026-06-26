# LiteLLM

---
该类在类层次结构中的位置：

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

## 简介

`LiteLLM` 通过 [LiteLLM](https://github.com/BerriAI/litellm) 库提供统一接口，支持 100+ LLM 提供商（OpenAI、Anthropic、Google、Azure、AWS Bedrock、Ollama 等）。底层使用 `litellm.acompletion`，根据 `model_name` 前缀自动路由到对应的提供商（例如 `anthropic/claude-sonnet-4-20250514`、`openai/gpt-4o`、`bedrock/anthropic.claude-3`）。需要安装 `litellm` 包。

## 参数

| 参数          | 类型 / 允许值        | 默认值   | 描述                                                                       |
| ------------- | -------------------- | -------- | -------------------------------------------------------------------------- |
| `model_name`  | `str`                | 必填     | LiteLLM 模型标识符，例如 `"anthropic/claude-sonnet-4-20250514"`。                       |
| `api_key`     | `Optional[str]`      | `None`   | 底层提供商的 API 密钥。未设置时回退到提供商特定的环境变量。                    |
| `base_url`    | `Optional[str]`      | `None`   | 可选的 LiteLLM 代理服务器基础 URL。                                         |
| `drop_params` | `bool`               | `True`   | 静默丢弃提供商不支持的参数（推荐开启）。                                     |

## 方法

| 方法                    | 协程 (async) | 返回值        | 用途（简述）                                                    |
| ----------------------- | ------------ | ------------- | -------------------------------------------------------------- |
| `init()`                | 是           | `None`        | 导入 `litellm` 包并初始化提供商。                                |
| `_execute(oxy_request)` | 是           | `OxyResponse` | 构建 payload，调用 `litellm.acompletion`，流式/收集响应。        |

## 继承

请参阅 [BaseLLM](./base_llm.md) 类了解继承的参数和方法。

## 用法

```python
oxy.LiteLLM(
    name="lite_llm",
    model_name="anthropic/claude-sonnet-4-20250514",
    api_key="sk-...",
    drop_params=True,
)
```
