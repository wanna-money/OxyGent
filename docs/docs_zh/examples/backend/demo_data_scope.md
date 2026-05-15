# 理解数据作用域：shared_data、group_data 和 global_data

**源文件:** `examples/backend/demo_data_scope.py`

## 概述

本示例演示 OxyGent 中三个数据作用域层级 -- `shared_data`、`group_data` 和 `global_data` -- 以及它们在多智能体系统中的传播方式。示例展示了每个作用域如何在对话轮次间持久化，以及子智能体如何从父智能体继承数据。此模式对于理解复杂多智能体架构中的数据流至关重要。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- 需要安装 Node.js 和 `uvx`（用于 MCP 时间服务器工具）

## 运行方式

```bash
python -m examples.backend.demo_data_scope
```

## 代码详解

### 钩子函数

```python
def process_input(oxy_request: OxyRequest) -> OxyRequest:
    print("--- agent name --- :", oxy_request.callee)
    print("--- arguments --- :", oxy_request.get_arguments())
    print("--- shared_data --- :", oxy_request.get_shared_data())
    print("--- group_data --- :", oxy_request.get_group_data())
    print("--- global_data --- :", oxy_request.get_global_data())
    return oxy_request
```

此诊断钩子附加到两个智能体上，每次智能体被调用时打印所有三个数据作用域。这使你能观察数据如何在智能体层级中传播。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | 标准 LLM 凭证 |
| `time_tools` | `StdioMCPClient` | MCP 时间服务器（`mcp-server-time`），用于时区查询 |
| `master_agent` | `ReActAgent` | `is_master=True`，`sub_agents=["time_agent"]`，挂载 `process_input` 钩子 |
| `time_agent` | `ReActAgent` | `tools=["time_tools"]`，挂载 `process_input` 钩子，描述为时间查询工具 |

### 入口函数

示例进行三次顺序调用以演示数据作用域行为：

**第 1-1 轮 -- 基准调用（无额外数据）：**
```python
oxy_response = await mas.chat_with_agent({"query": "What time is it"})
```
仅 `global_data`（在 MAS 初始化时设置）可用。

**第 2-1 轮 -- 携带 shared_data 和 group_data 的调用：**
```python
oxy_response = await mas.chat_with_agent({
    "query": "What time is it",
    "shared_data": {"shared_key": "shared_value"},
    "group_data": {"group_key": "group_value"},
})
```
`shared_data` 和 `group_data` 均被注入到请求中。

**第 2-2 轮 -- 通过 from_trace_id 延续第 2-1 轮：**
```python
trace_id = oxy_response.oxy_request.current_trace_id
oxy_response = await mas.chat_with_agent({
    "query": "What time is it",
    "from_trace_id": trace_id,
})
```
使用 `from_trace_id` 延续上一次对话，继承其 `shared_data` 和 `group_data`。

### MAS 初始化

```python
global_data = {"global_key": "global_value"}
async with MAS(oxy_space=oxy_space, global_data=global_data) as mas:
```

`global_data` 字典在 MAS 构建时传入，在 MAS 实例的整个生命周期内可被所有智能体在所有请求中访问。

## 核心概念

- **shared_data**：请求级作用域数据。通过 payload 或编程方式设置。在单个 trace 内持久化，可通过 `from_trace_id` 传递到后续轮次。
- **group_data**：请求级作用域数据，与 `shared_data` 类似，但设计用于组级上下文（如用户会话数据）。同样支持 trace 延续间的持久化。
- **global_data**：MAS 级作用域数据。在 MAS 初始化时设置。在 MAS 实例的整个生命周期内，所有请求和所有智能体共享。
- **from_trace_id**：允许延续之前的对话，继承其数据作用域。
- **数据继承**：当主智能体委派给子智能体时，数据作用域沿调用链向下传播。

## 预期行为

1. 第 1-1 轮：`process_input` 钩子打印空的 `shared_data` 和 `group_data`，但显示 `global_data` 包含 `{"global_key": "global_value"}`。
2. 第 2-1 轮：钩子打印 `shared_data` 为 `{"shared_key": "shared_value"}`，`group_data` 为 `{"group_key": "group_value"}`，以及相同的 `global_data`。
3. 第 2-2 轮：尽管未显式传递 `shared_data` 或 `group_data`，这些值通过 `from_trace_id` 从上一个 trace 继承。
4. 子智能体 `time_agent` 在被 `master_agent` 调用时也接收到传播的数据作用域。
