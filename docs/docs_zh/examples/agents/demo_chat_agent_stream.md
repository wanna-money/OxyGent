# 流式聊天代理

**源文件:** `examples/agents/demo_chat_agent_stream.py`

## 概述

本示例演示如何在 OxyGent 中启用 LLM 流式输出。通过在 LLM 参数中设置 `"stream": True` 并启用终端消息显示，你可以在 Web UI 和服务端终端中获得实时逐 token 的响应体验。这非常适合需要低延迟增量输出的对话应用。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包

## 运行方式

```bash
python -m examples.agents.demo_chat_agent_stream
```

## 代码详解

### 配置

```python
Config.set_message_is_show_in_terminal(True)
```

启用在终端直接打印流式消息（SSE 事件）。这对于调试和实时监控代理输出非常有用，无需打开 Web UI 即可查看。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量；`llm_params={"stream": True}` |
| `qa_agent` | `ChatAgent` | `llm_model="default_llm"`（无自定义提示词，使用默认行为） |

关键参数是 `llm_params={"stream": True}`，它告诉 `HttpLLM` 向 LLM API 端点请求流式响应。Token 通过服务器发送事件（SSE）增量传递。

### 入口函数

```python
await mas.start_web_service(first_query="hello")
```

启动 Web 服务，初始查询为 "hello"。

## 核心概念

- **流式输出 (`stream: True`)** -- LLM 增量返回 token，而不是等待完整响应。这通过 SSE 传递到 Web UI，提供打字机式的体验效果。
- **`set_message_is_show_in_terminal`** -- 设为 `True` 时，所有 SSE 消息（包括流式 token）都会打印到服务端终端输出，便于实时监控。
- **最简代理配置** -- 此处的 `ChatAgent` 没有自定义提示词、工具和钩子函数，展示了最简化的配置方式。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 首个查询 "hello" 被自动发送。
3. 代理的响应在 Web UI 中逐 token 显示（流式效果）。
4. 同样的流式输出也会实时打印到终端。
5. 后续查询同样以增量方式流式输出。
