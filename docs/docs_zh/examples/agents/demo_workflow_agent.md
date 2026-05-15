# 工作流代理与多组件编排

**源文件:** `examples/agents/demo_workflow_agent.py`

## 概述

本示例充分展示了 `WorkflowAgent` 的能力：一个编程式工作流函数通过 `oxy_request.call()` 直接调用子代理、LLM 和工具。它演示了如何访问对话记忆、发送自定义消息、调用 LLM 进行辅助推理以及调用 MCP 工具 -- 所有这些都在一个确定性的工作流中完成。这种模式非常适合需要精确控制执行顺序的复杂多步骤任务。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包
- 已安装 `uv`（用于运行自定义数学 MCP 服务器）
- 项目根目录下必须存在包含 `math_tools.py` 的 `mcp_servers/` 目录

## 运行方式

```bash
python -m examples.agents.demo_workflow_agent
```

## 代码详解

### 钩子函数

#### `workflow(oxy_request: OxyRequest)`

通过 `func_workflow` 注册的核心异步工作流函数。它展示了 `OxyRequest` 的全部能力：

1. **访问记忆：**
   - `oxy_request.get_short_memory()` -- 获取当前代理的短期对话记忆。
   - `oxy_request.get_short_memory(master_level=True)` -- 获取主代理级别的记忆（顶层代理的对话历史）。

2. **访问查询：**
   - `oxy_request.get_query()` -- 获取当前指向此代理的查询。
   - `oxy_request.get_query(master_level=True)` -- 获取主代理级别的原始用户查询。

3. **发送自定义消息：**
   - `await oxy_request.send_message({"type": "msg_type", "content": "msg_content"})` -- 向前端发送自定义 SSE 消息。

4. **调用子代理：**
   - 使用当前查询调用 `chat_agent`，捕获其直接回答。

5. **直接调用 LLM：**
   - 使用自定义消息列表和 `llm_params={"temperature": 0.2}` 调用 `default_llm`，确定用户想要圆周率的多少位小数。

6. **调用 MCP 工具：**
   - 使用提取的精度参数调用 `calc_pi`（由数学 MCP 服务器提供）来计算圆周率。

7. **返回最终结果：** 格式化的字符串，结合精度和计算出的圆周率值。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量 |
| `math_tools` | `StdioMCPClient` | `params.command="uv"`，`params.args=["--directory", "./mcp_servers", "run", "math_tools.py"]` |
| `chat_agent` | `ChatAgent` | `llm_model="default_llm"`（最简配置） |
| `math_agent` | `WorkflowAgent` | `is_master=True`；`sub_agents=["chat_agent"]`；`tools=["math_tools"]`；`func_workflow=workflow`；`llm_model="default_llm"` |

### 入口函数

```python
await mas.start_web_service(
    first_query="Please calculate the 20 positions of Pi",
)
```

启动 Web 服务，初始查询为圆周率计算问题。

## 核心概念

- **`oxy_request.call()`** -- 工作流中的通用调用方法。通过指定 `callee` 和 `arguments`，你可以调用任何已注册的 Oxy 组件：代理、LLM 或工具。
- **`get_short_memory()` / `get_query()`** -- `OxyRequest` 上用于访问对话上下文的方法。`master_level=True` 标志访问根级别的上下文。
- **`send_message()`** -- 向已连接的前端发送自定义 SSE 事件，适用于进度更新或中间结果展示。
- **直接 LLM 调用** -- 在工作流中，你可以使用自定义消息和参数直接调用 LLM，绕过代理抽象以实现细粒度控制。
- **`StdioMCPClient` 与自定义服务器** -- `math_tools.py` MCP 服务器通过 `uv run` 从 `mcp_servers/` 目录启动。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 查询 "Please calculate the 20 positions of Pi" 被发送。
3. 工作流按顺序执行：
   - 在终端打印当前和主代理级别的短期记忆和查询。
   - 向前端发送自定义消息 `{"type": "msg_type", "content": "msg_content"}`。
   - 调用 `chat_agent` 获取直接回答（打印到终端）。
   - 调用 `default_llm` 从查询中提取数字 "20"（打印到终端）。
   - 使用 `prec=20` 调用 `calc_pi` MCP 工具。
4. 最终响应 "Save 20 positions: [Pi 值]" 显示在 Web UI 中。
