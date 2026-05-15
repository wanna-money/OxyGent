# 控制消息存储与推送

**源文件:** `examples/backend/demo_save_message.py`

## 概述

本示例演示 OxyGent 中对消息存储和推送的细粒度控制。示例展示了如何在智能体钩子中发送自定义消息，并控制每条消息是否持久化到 Elasticsearch 和/或通过 SSE 推送到前端。当你需要发送进度更新、状态通知或调试信息，同时有选择地决定哪些消息需要保存以供后续检索时，此模式非常有用。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`

## 运行方式

```bash
python -m examples.backend.demo_save_message
```

## 代码详解

### 配置

```python
Config.set_message_is_show_in_terminal(True)
Config.set_message_is_stored(True)
```

- `set_message_is_show_in_terminal(True)`：启用在终端打印消息以供调试。
- `set_message_is_stored(True)`：设置全局默认值，将消息存储到 Elasticsearch。

### 钩子函数

```python
async def update_query(oxy_request: OxyRequest) -> OxyRequest:
    await oxy_request.send_message(
        {"type": "test1", "content": "test1", "_is_stored": False, "_is_send": False}
    )
    await oxy_request.send_message(
        {"type": "test2", "content": "test2", "_is_stored": False, "_is_send": True}
    )
    await oxy_request.send_message(
        {"type": "test3", "content": "test3", "_is_stored": True, "_is_send": False}
    )
    await oxy_request.send_message(
        {"type": "test4", "content": "test4", "_is_stored": True, "_is_send": True}
    )
    return oxy_request
```

发送四条消息，使用 `_is_stored` 和 `_is_send` 标志的不同组合：

| 消息 | `_is_stored` | `_is_send` | 行为 |
|------|-------------|-----------|------|
| test1 | `False` | `False` | 既不存储也不推送到前端 |
| test2 | `False` | `True` | 通过 SSE 推送到前端但不持久化 |
| test3 | `True` | `False` | 持久化到 ES 但不推送到前端 |
| test4 | `True` | `True` | 既持久化又推送到前端 |

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `llm_params={"stream": True}` -- 启用流式响应 |
| `qa_agent` | `ChatAgent` | `func_process_input=update_query` -- 在处理前发送自定义消息 |

### 入口函数

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="hello")
```

## 核心概念

- **send_message**：`OxyRequest` 上的异步方法，将自定义消息推入 MAS 消息管道。每条消息是包含 `type` 和 `content` 的字典。
- **_is_stored 标志**：控制消息是否持久化到 Elasticsearch。适用于审计追踪和对话历史。
- **_is_send 标志**：控制消息是否通过 SSE/Redis 推送到前端。适用于实时 UI 更新。
- **流式 LLM**：设置 `llm_params={"stream": True}` 启用 LLM 的逐 token 流式输出，与自定义消息管道协同工作。

## 预期行为

1. 当智能体处理查询时，发送四条自定义消息。
2. `test1` 被静默丢弃（既不存储也不推送）。
3. `test2` 出现在前端 SSE 流中，但不保存到 Elasticsearch。
4. `test3` 保存到 Elasticsearch，但不出现在前端。
5. `test4` 既出现在前端又保存到 Elasticsearch。
6. 所有四条消息都打印到终端（因为 `is_show_in_terminal` 已启用）。
7. 自定义消息之后，LLM 响应流式推送到前端。
