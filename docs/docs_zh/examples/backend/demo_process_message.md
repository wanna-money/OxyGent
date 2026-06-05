# 处理和转换出站消息

**源文件:** `examples/backend/demo_process_message.py`

## 概述

本示例演示如何使用 `func_process_message` 钩子在消息到达前端之前拦截和转换出站消息。通过在传输过程中修改消息 payload，你可以添加格式化、注入元数据、过滤敏感内容或对 SSE 流应用自定义转换。此模式对于后处理流式 LLM 响应特别有用。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`

## 运行方式

```bash
python -m examples.backend.demo_process_message
```

## 代码详解

### 配置

```python
Config.set_message_is_show_in_terminal(True)
```

启用在终端显示所有出站消息以供调试。

### 钩子函数

```python
def process_message(dict_message: dict, oxy_request: OxyRequest) -> dict:
    if dict_message["data"]["type"] == "stream":
        dict_message["data"]["content"]["delta"] += "-"
    return dict_message
```

`process_message` 函数是一个 MAS 级钩子，对每条出站消息调用。它接收：
- `dict_message`：即将发送的消息字典。
- `oxy_request`：当前请求上下文。

在本示例中，它检查消息类型是否为 `"stream"`（流式 LLM token），并在每个 token delta 后追加 `"-"` 字符。这在 UI 输出中直观地展示了转换效果。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `llm_params={"stream": True}` -- 启用流式输出以展示逐 token 处理 |
| `qa_agent` | `ChatAgent` | 基础聊天智能体 |

### 入口函数

```python
async with MAS(oxy_space=oxy_space, func_process_message=process_message) as mas:
    await mas.start_web_service(first_query="hello")
```

`func_process_message` 钩子作为参数传递给 `MAS` 构造函数。

## 核心概念

- **func_process_message**：MAS 级钩子，在每条出站消息通过 SSE 发送到前端之前进行拦截。它接收消息字典和当前 `OxyRequest`，必须返回（可能已修改的）消息字典。支持同步和异步函数。
- **流式消息结构**：流式 LLM 消息的 `type` 为 `"stream"`，`content.delta` 字段包含增量文本 token。
- **消息转换**：你可以修改消息字典中的任何字段 -- 内容、元数据、类型 -- 甚至可以通过返回 `None` 或空字典来抑制消息。

> OxyGent 中所有 `func_*` 钩子函数均支持同步和异步函数。同步函数会在初始化时自动包装为异步函数。

## 预期行为

1. Web 服务以流式模式启动。
2. 当 LLM 响应 `"hello"` 时，每个流式 token 被钩子拦截。
3. 每个 token delta 后追加 `"-"` 字符，因此输出中字符间会出现连字符（例如 `H-e-l-l-o-` 而非 `Hello`）。
4. 非流式消息（如状态消息）不经修改直接通过。
5. 所有消息同时打印到终端以供验证。
