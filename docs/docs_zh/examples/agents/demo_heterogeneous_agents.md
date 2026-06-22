# 异构多代理系统

**源文件:** `examples/agents/demo_heterogeneous_agents.py`

## 概述

本示例展示了由不同类型代理协作组成的多代理系统：一个 `ReActAgent` 作为主编排器，一个 `ChatAgent` 负责通用知识，以及一个 `WorkflowAgent` 用于结构化的时间查询。同时演示了与 MCP（模型上下文协议）工具服务器的集成，以及使用 `Config.set_agent_llm_model()` 设置全局默认 LLM。当不同子任务需要不同的代理策略时，这种模式非常理想。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包
- 已安装 `uvx`（用于运行 MCP 时间服务器 `mcp-server-time`）

## 运行方式

```bash
python -m examples.agents.demo_heterogeneous_agents
```

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
```

为所有代理设置全局默认 LLM 模型名称。未显式指定 `llm_model` 的代理将使用 `"default_llm"`。本示例中，`QA_agent` 和 `time_agent` 依赖此默认值。

### 钩子函数

#### `workflow(oxy_request: OxyRequest)`

注册在 `WorkflowAgent` 上的异步工作流函数（`func_workflow`）。它定义了确定性的执行序列：

1. 调用 `get_current_time` 工具（由 MCP 时间服务器提供），参数为 `{"timezone": "Asia/Shanghai"}`。
2. 直接返回工具的输出。

这展示了 `WorkflowAgent` 如何在无需 LLM 推理的情况下执行固定步骤序列。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量 |
| `time_tools` | `StdioMCPClient` | `params.command="uvx"`，`params.args=["mcp-server-time", "--local-timezone=Asia/Shanghai"]` |
| `master_agent` | `ReActAgent` | `llm_model="default_llm"`；`sub_agents=["QA_agent", "time_agent"]` |
| `QA_agent` | `ChatAgent` | `desc="A tool for knowledge."`；`llm_model="default_llm"` |
| `time_agent` | `WorkflowAgent` | `desc="A tool for time query."`；`tools=["time_tools"]`；`func_workflow=workflow` |

### 入口函数

```python
await mas.start_web_service(
    first_query="What time it is?",
)
```

启动 Web 服务，初始查询为时间相关的问题。

## 核心概念

- **异构代理** -- 在一个主代理下组合不同类型的代理（`ReActAgent`、`ChatAgent`、`WorkflowAgent`），每个代理专注于不同的能力。
- **`sub_agents`** -- 主 `ReActAgent` 将子代理视为可调用工具。它根据用户查询推理决定调用哪个子代理。
- **`StdioMCPClient`** -- 通过标准输入输出连接外部 MCP 工具服务器。`mcp-server-time` 包提供时间相关工具。
- **`WorkflowAgent`** -- 执行预定义的编程式工作流（无 LLM 驱动推理），适用于确定性的多步骤任务。
- **`desc`** -- 子代理上的描述字段帮助主代理决定将查询路由到哪个子代理。
- **`Config.set_agent_llm_model()`** -- 设置全局默认 LLM，当多个代理共享同一模型时减少重复配置。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 初始查询 "What time it is?" 被发送。
3. 主 `ReActAgent` 推理出这是一个时间查询，并委派给 `time_agent`。
4. `time_agent`（一个 `WorkflowAgent`）执行其工作流：调用 `get_current_time` MCP 工具，时区为 `Asia/Shanghai`。
5. 当前时间通过代理链返回并显示在 Web UI 中。
6. 对于知识相关的查询，主代理会改为委派给 `QA_agent`。
