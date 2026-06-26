# LiteLLM 集成示例

**源文件:** `examples/llms/demo_litellm.py`

## 概述

本示例演示如何在 OxyGent 中通过 LiteLLM 使用任意 LLM 提供商。LiteLLM 是一个统一接口，支持 100+ 个 LLM 提供商（OpenAI、Anthropic、Google、Mistral、Cohere 等），使用一致的 API 格式。通过使用 `LiteLLM` 组件，您可以在不修改 OxyGent 智能体其余配置的情况下，轻松切换不同的提供商。

## 前置条件

- 已安装 **LiteLLM**：`pip install litellm`
- 拥有所需 LLM 提供商的 API 密钥（如 `ANTHROPIC_API_KEY`、`OPENAI_API_KEY` 等），通过环境变量设置或直接传入
- Python 3.10+ 且已安装项目依赖

**注意:** 如果使用 LiteLLM 代理服务器，请将 `base_url` 参数设置为代理端点（如 `http://localhost:4000`）。

## 运行方式

1. 安装 LiteLLM：
   ```bash
   pip install litellm
   ```

2. 设置 API 密钥环境变量（以 Anthropic 为例）：
   ```bash
   export ANTHROPIC_API_KEY="sk-..."
   ```

3. 将源代码中的 `model_name` 修改为您所需的提供商和模型：
   ```python
   model_name="anthropic/claude-sonnet-4-20250514",  # 或 "openai/gpt-4o"、"gemini/gemini-pro" 等
   ```

4. 运行示例：
   ```bash
   python -m examples.llms.demo_litellm
   ```

## 代码详解

### 配置

```python
oxy.LiteLLM(
    name="default_llm",
    model_name="anthropic/claude-sonnet-4-20250514",
    # api_key="sk-...",         # 或设置 ANTHROPIC_API_KEY 环境变量
    # base_url="http://localhost:4000",  # 可选：LiteLLM 代理
)
```

`LiteLLM` 组件的 `model_name` 遵循 LiteLLM 的 `provider/model` 命名规范。`api_key` 可以直接传入，也可以从对应提供商的环境变量中读取。`base_url` 可选配置，用于指向 LiteLLM 代理服务器。

### 组件（`oxy_space`）

定义了两个组件：

1. **`LiteLLM("default_llm")`** -- 基于 LiteLLM 的 LLM，将请求路由到指定的提供商。
2. **`ReActAgent("agent")`** -- 由 LiteLLM 模型驱动的推理与行动智能体，配置了简单的系统提示词。

### 入口点

`main()` 协程创建 MAS 并调用智能体：

```python
await mas.call(
    callee="agent",
    arguments={"messages": [{"role": "user", "content": "What is 2 + 2?"}]},
)
```

向 ReActAgent 发送一条用户消息，智能体使用 LiteLLM 模型生成响应。

## 核心概念

- **LiteLLM** -- 一个统一的 Python 库，为 100+ 个 LLM 提供商提供一致的调用接口。它会将调用转换为各提供商的原生 API 格式，因此只需修改 `model_name` 即可切换提供商。
- **提供商/模型命名规范** -- LiteLLM 使用 `provider/model` 格式（如 `anthropic/claude-sonnet-4-20250514`、`openai/gpt-4o`、`gemini/gemini-pro`）来标识使用的提供商和模型。
- **LiteLLM 代理** -- 您可以选择运行 LiteLLM 代理服务器，集中管理 API 密钥和负载均衡。将 `base_url` 指向代理端点即可将所有请求通过代理路由。
- **即插即用的提供商切换** -- 由于 `LiteLLM` 将多个提供商封装在统一接口之后，从一个 LLM 提供商切换到另一个只需更改 `model_name` 和 API 密钥，无需修改其他代码。

## 预期行为

1. MAS 初始化 `LiteLLM` 组件和 `ReActAgent`。
2. 用户消息 `"What is 2 + 2?"` 发送给智能体。
3. 智能体使用 LiteLLM 模型进行推理并回答问题。
4. 结果被打印输出，显示模型的响应（如 `"4"`）。
