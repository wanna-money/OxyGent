# 人机协同与反馈流

**源文件:** `examples/backend/demo_human_in_the_loop.py`

## 概述

本示例演示 OxyGent 中的人机协同模式，智能体在执行过程中暂停以等待外部反馈，然后再继续执行。通过使用 `send_message` 通知前端和 `get_feedback_stream` 监听响应，此模式支持在智能体执行期间需要人工审批、输入或干预的交互式工作流。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`

## 运行方式

```bash
python -m examples.backend.demo_human_in_the_loop
```

## 代码详解

### 钩子函数

```python
async def workflow(oxy_request: OxyRequest):
    # 发消息
    await oxy_request.send_message({"type": "msg_type", "content": "msg_content"})

    # 监听数据流，channel_id 默认是 trace_id
    feedbacks = []
    async for data in oxy_request.get_feedback_stream():
        print(data)
        feedbacks.append(data)

    return ",".join(feedbacks)
```

工作流函数：
1. 向前端发送自定义消息（例如提示用户输入）。
2. 使用 `get_feedback_stream()` 打开反馈流，该流会阻塞并在数据到达时逐条产出。
3. 收集所有反馈项并以逗号分隔的字符串形式返回。

外部客户端可通过 `/feedback` 端点发送反馈：
```
POST http://127.0.0.1:8080/feedback
Body: {"channel_id": "xxx", "data": "用户输入内容"}
```

`channel_id` 默认为当前的 `trace_id`。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | 标准 LLM 凭证（已包含但工作流中未直接使用） |
| `master_agent` | `WorkflowAgent` | `func_workflow=workflow` -- 包含人工交互的自定义异步工作流 |

### 入口函数

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="hello")
```

## 核心概念

- **人机协同**：一种设计模式，自动化的智能体执行暂停以请求并纳入人工输入后再继续。
- **send_message**：通过 SSE 流向前端推送消息，此处用于提示用户提供反馈。
- **get_feedback_stream**：`OxyRequest` 上的异步生成器，当外部来源的反馈数据到达时逐条产出。流通过 `channel_id`（默认为 `trace_id`）进行标识。
- **反馈端点**：MAS Web 服务暴露 `POST /feedback` 接口，外部系统或前端可以通过它向等待中的智能体发送数据。
- **WorkflowAgent**：执行用户定义的异步函数而非 LLM 驱动的推理，完全控制执行流程，包括暂停等待人工输入。

## 预期行为

1. Web 服务启动，工作流智能体处理初始查询 `"hello"`。
2. 智能体向前端发送消息 `{"type": "msg_type", "content": "msg_content"}`。
3. 智能体随后阻塞，通过 `get_feedback_stream()` 等待反馈。
4. 当用户或外部系统向 `/feedback` 发送包含相应 `channel_id` 的 POST 请求时，数据被流产出。
5. 智能体收集所有反馈，用逗号连接后作为最终响应返回。
