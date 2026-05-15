# Ollama 集成示例

**源文件:** `examples/llms/demo_ollama.py`

## 概述

本示例演示如何将 OxyGent 连接到本地运行的 Ollama 实例。Ollama 提供了一种简便的方式，通过 HTTP API 在本地运行开源 LLM。将 `HttpLLM` 指向 Ollama 的聊天端点，即可使用任何 Ollama 托管的模型作为 OxyGent 智能体的 LLM 后端。

## 前置条件

- 已安装并运行 **Ollama**（参见 [ollama.com](https://ollama.com)）
- Ollama 中已拉取至少一个模型（如 `ollama pull llama3`）
- Ollama 在默认端口运行（`http://localhost:11434`）
- Python 3.10+ 且已安装项目依赖

**注意:** 不需要 API 密钥 -- Ollama 在本地运行，默认不需要认证。

## 运行方式

1. 启动 Ollama（如果尚未运行）：
   ```bash
   ollama serve
   ```

2. 如需拉取模型：
   ```bash
   ollama pull llama3
   ```

3. 将源代码中的 `model_name` 修改为您已拉取的模型名：
   ```python
   model_name="llama3",  # 或您选择的模型
   ```

4. 运行示例：
   ```bash
   python -m examples.llms.demo_ollama
   ```

## 代码详解

### 配置

```python
oxy.HttpLLM(
    name="default_llm",
    base_url="http://localhost:11434/api/chat",
    model_name="ollama_model_name",
)
```

`HttpLLM` 配置为 Ollama 的聊天 API 端点（`/api/chat`）。由于 Ollama 不需要认证，未提供 `api_key`。`model_name` 应与您在本地拉取的 Ollama 模型名称一致。

### 组件（`oxy_space`）

仅包含一个组件：

1. **`HttpLLM("default_llm")`** -- 指向本地 Ollama 服务器的 HTTP LLM。

未定义智能体，直接调用 LLM 以演示连接。

### 入口点

`main()` 协程创建 MAS 并直接调用 LLM：

```python
await mas.call(
    callee="default_llm",
    arguments={"messages": [{"role": "user", "content": "hello"}]},
)
```

向 Ollama 模型发送一条用户消息并接收响应。

## 核心概念

- **Ollama** -- 一个在本地运行开源 LLM 的应用，提供简单的 HTTP API。支持 LLaMA、Mistral、Phi、Gemma 等众多模型。
- **HttpLLM 连接本地端点** -- `HttpLLM` 不仅限于云端 API，通过设置合适的 `base_url`，可以连接任何 HTTP 兼容的 LLM 端点（包括本地服务器）。
- **无需 API 密钥** -- 连接 Ollama 等本地服务时，可以省略 `api_key` 参数。
- **直接调用 LLM** -- 使用 `mas.call()` 直接调用 LLM，表明在 OxyGent 中 LLM 是独立于智能体的可调用组件。

## 预期行为

1. MAS 初始化并连接到 `http://localhost:11434/api/chat` 的 Ollama 服务器。
2. 消息 `"hello"` 发送给指定的 Ollama 模型。
3. 模型在本地生成响应。
4. 响应由框架返回并打印/记录。
