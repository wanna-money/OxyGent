# 启动 MAS：所有执行模式

**源文件:** `examples/backend/demo_launch_mas.py`

## 概述

本示例是一个综合参考，演示了创建、初始化和启动 MAS 实例的所有方式。涵盖了通过 `mas.call()` 直接调用组件、通过 `chat_with_agent()` 进行智能体级交互，以及三种运行模式：CLI、批量处理和 Web 服务。同时展示了替代的 `MAS.create()` 工厂方法。可将本示例作为快速入门指南，了解完整的 MAS API。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- 需要安装 Node.js 和 `uvx`（用于 MCP 时间服务器工具）

## 运行方式

```bash
python -m examples.backend.demo_launch_mas
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | 标准 LLM 凭证 |
| `time_tools` | `StdioMCPClient` | MCP 时间服务器，用于时区查询 |
| `time_agent` | `ReActAgent` | `tools=["time_tools"]` -- 配备时间工具的 ReAct 智能体 |

### 替代初始化方式：MAS.create()

```python
async def get_mas_object():
    mas = await MAS.create(oxy_space=oxy_space)
    await mas.start_web_service()
```

`MAS.create()` 是一个异步工厂方法，无需使用 `async with` 上下文管理器即可返回已初始化的 MAS 实例。当你需要更精细地控制 MAS 生命周期或与管理自身事件循环的框架集成时，此方法非常有用。

### 入口函数

主函数按顺序演示五种使用模式：

**1. 直接调用工具：**
```python
await mas.call(
    callee="get_current_time",
    arguments={"timezone": "Asia/Shanghai"},
)
```
通过名称调用 MCP 客户端注册的特定工具。

**2. 直接调用 LLM：**
```python
await mas.call(
    callee="default_llm",
    arguments={
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "hello"},
        ],
        "llm_params": {"temperature": 0.2},
    },
)
```
使用自定义消息和参数直接调用 LLM。

**3. 直接调用智能体：**
```python
await mas.call(
    callee="time_agent",
    arguments={"query": "What time it is?"},
)
```
通过名称调用特定智能体并传入查询。

**4. 与主智能体对话：**
```python
payload = {"query": "What time it is?"}
oxy_response = await mas.chat_with_agent(payload=payload)
```
将查询路由到主智能体（`oxy_space` 中的第一个智能体或标记为 `is_master=True` 的智能体）。

**5. 运行模式：**
```python
await mas.start_cli_mode(first_query="What time it is?")
await mas.start_batch_processing(["What time it is?"] * 10)
await mas.start_web_service(first_query="What time it is?")
```
- `start_cli_mode`：终端中的交互式 REPL。
- `start_batch_processing`：多个查询的并发处理。
- `start_web_service`：带有 Web UI 的 FastAPI 服务器。

## 核心概念

- **mas.call()**：底层 API，通过名称调用任何已注册的 Oxy 组件（智能体、工具或 LLM）。
- **mas.chat_with_agent()**：高层 API，将查询路由到主智能体，处理 trace 管理和响应格式化。
- **MAS.create()**：用于在上下文管理器之外初始化 MAS 的异步工厂方法。
- **三种运行模式**：CLI 模式用于开发/调试，批量模式用于大规模处理，Web 服务模式用于生产部署。
- **MCP 工具注册**：`StdioMCPClient` 提供的工具会自动按其工具名称注册（如 `get_current_time`），使其可通过 `mas.call()` 调用。

## 预期行为

1. MAS 使用 LLM、MCP 客户端和智能体初始化。
2. 直接工具调用返回上海时区的当前时间。
3. 直接 LLM 调用返回问候响应。
4. 直接智能体调用触发 ReAct 循环：智能体对查询进行推理，调用时间工具，返回结果。
5. `chat_with_agent` 通过主智能体路由并返回 `OxyResponse`。
6. 每种运行模式按顺序启动（实际使用中，你会选择其中一种）。
