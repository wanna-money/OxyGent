# Plan-and-Solve 规划求解示例

**源文件:** `examples/flows/plan_and_solve_demo.py`

## 概述

本示例展示了 OxyGent 中的 **Plan-and-Solve**（规划求解）流程模式。一个规划智能体将复杂的用户请求分解为逐步计划，执行智能体使用丰富的子智能体和工具集来执行每个步骤 -- 包括时间查询、文件操作、数学计算和讲笑话。本示例还展示了自定义 `WorkflowAgent`，将编程逻辑与智能体调用相结合。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- 已安装 OxyGent 包（`pip install -r requirements.txt`）
- Node.js（文件系统 MCP 工具需要通过 `npx` 运行）
- PATH 中可用 `uvx`（用于 `mcp-server-time` 包）
- PATH 中可用 `uv`（用于运行自定义数学 MCP 服务器）
- 工作目录中需要 `config.json` 文件（启动时加载）
- 需要 `./local_file` 目录（文件系统工具使用）
- 需要 `./mcp_servers` 目录，包含 `math_tools.py`

## 运行方式

```bash
python -m examples.flows.plan_and_solve_demo
```

示例会启动 Web 服务，预定义了多个查询。默认发送第一个查询："What time is it now? Please save it to the file log.txt under the local_file folder."（现在几点？请将时间保存到 local_file 文件夹下的 log.txt 文件中。）

## 代码详解

### 配置

```python
Config.load_from_json("./config.json", env="default")
```

从 `config.json` 加载配置，使用"default"环境层。这会覆盖 LLM、服务器等默认设置。

### 自定义工作流函数

```python
async def workflow(oxy_request: OxyRequest):
```

这是赋给 `math_agent`（`WorkflowAgent`）的自定义工作流函数，它：

1. 获取智能体级别和主控级别的短期记忆（对话历史）。
2. 通过 `oxy_request.send_message("msg")` 发送中间消息。
3. 调用 `time_agent` 获取当前时间。
4. 解析用户查询中的数字；如果找到，调用 `pi` 数学工具计算对应精度的圆周率。
5. 返回格式化的结果字符串。

### 自定义 FunctionHub 工具

```python
fh = oxy.FunctionHub(name="joke_tools")

@fh.tool(description="A tool that is good at telling jokes")
async def joke_tool(joke_type: str = Field(description="Type of joke")):
```

定义了一个 `FunctionHub`，包含单个工具 `joke_tool`，从硬编码列表中随机返回一个笑话。这展示了如何创建自定义 Python 函数工具。

### 组件（`oxy_space`）

| 组件 | 类型 | 角色 |
|---|---|---|
| `default_llm` | `HttpLLM` | 共享语言模型 |
| `intent_agent` | `ChatAgent` | 意图分类智能体（使用 `INTENTION_PROMPT`） |
| `joke_tools` (fh) | `FunctionHub` | 自定义讲笑话函数工具 |
| `time_tools` | `StdioMCPClient` | 时间查询 MCP 客户端（Asia/Shanghai 时区） |
| `file_tools` | `StdioMCPClient` | 文件系统操作 MCP 客户端，操作 `./local_file` |
| `math_tools` | `StdioMCPClient` | 数学计算 MCP 客户端（自定义服务器） |
| `planner_agent` | `ChatAgent` | 根据用户目标创建逐步计划 |
| `executor_agent` | `ReActAgent` | 使用子智能体和工具执行计划中的单个步骤 |
| `master_agent` | `PlanAndSolve` | 编排规划和执行流程；标记为 `is_master=True` |
| `time_agent` / `time_agent_b` / `time_agent_c` | `ReActAgent` | 封装时间 MCP 工具的智能体（3 个实例） |
| `file_agent` | `ReActAgent` | 封装文件系统 MCP 工具的智能体 |
| `math_agent` | `WorkflowAgent` | 使用自定义工作流函数处理数学/圆周率查询的智能体 |

### Plan-and-Solve 配置

`master_agent`（`PlanAndSolve`）配置如下：
- `planner_agent_name="planner_agent"` -- 负责创建计划的智能体。
- `executor_agent_name="executor_agent"` -- 负责执行每个步骤的智能体。
- `enable_replanner=False` -- 禁用步骤失败后的重新规划。
- `is_discard_react_memory=True` -- 在步骤之间清除 ReAct 记忆，防止上下文污染。

### 入口

```python
async def main():
    mas = await MAS.create(oxy_space=oxy_space)
    queries = [...]
    await mas.start_web_service(first_query=queries[0])
```

使用 `MAS.create()`（异步上下文管理器的替代方式）并使用预定义查询中的第一个启动 Web 服务。

## 核心概念

- **Plan-and-Solve**：一种两阶段方法，规划器将复杂任务分解为原子步骤，执行器按顺序执行每个步骤。这对需要不同工具的多步骤任务非常有效。
- **WorkflowAgent**：执行逻辑为自定义 Python 函数（`func_workflow`）的智能体，在参与智能体层级结构的同时提供完全的编程控制。
- **FunctionHub**：基于装饰器的系统，将普通 Python 函数包装为智能体可调用的 Oxy 工具。
- **StdioMCPClient**：通过标准 I/O 连接 MCP（模型上下文协议）工具服务器，实现对时间、文件系统和数学工具的访问。
- **`is_retain_master_short_memory`**：在 `math_agent` 上设为 `True` 时，智能体保留主控级别的对话历史，允许引用之前的交互。
- **`is_discard_react_memory`**：设为 `True` 时，在计划步骤之间清除执行器的 ReAct 记忆，防止跨步骤的上下文泄漏。

## 预期行为

1. Web 界面打开并发送第一个查询（将当前时间保存到文件）。
2. `planner_agent` 将查询分解为步骤（例如"获取当前时间"然后"保存到 log.txt"）。
3. `executor_agent` 通过委派给相应的子智能体执行每个步骤（`time_agent` 负责时间，`file_agent` 负责文件操作）。
4. 最终结果被汇总并显示在 Web 界面中。
5. 可以交互式发送其他查询（美食评价、Hive SQL）来测试系统的多功能性。
