# 计划与执行代理

**源文件:** `examples/agents/demo_plan_and_solve_agent.py`

## 概述

本示例演示了 OxyGent 中的计划与执行（Plan-and-Solve）模式，其中 `PlanAndSolveAgent` 编排两个专业代理：一个规划器（`ChatAgent`）负责创建和更新任务计划，一个执行器（`ReActAgent`）负责执行各个步骤。规划器生成 JSON 格式的计划，执行器每次处理一个步骤，计划在每个步骤完成后动态更新。这种模式非常适合需要显式规划和自适应重新规划的复杂多步骤任务。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包

## 运行方式

```bash
python -m examples.agents.demo_plan_and_solve_agent
```

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
```

为所有代理设置全局默认 LLM 模型。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量 |
| `planner_agent` | `ChatAgent` | 自定义 `prompt`，包含 `{past_plan}` 和 `{past_steps}` 模板变量，用于迭代式计划优化；输出 JSON 列表格式 |
| `time_tools` | `preset_tools.time_tools` | 内置时间工具 |
| `file_tools` | `preset_tools.file_tools` | 内置文件操作工具 |
| `executor_agent` | `ReActAgent` | `additional_prompt` 指示它仅执行当前步骤；`tools=["time_tools", "file_tools"]` |
| `master_agent` | `PlanAndSolveAgent` | `is_master=True`；`planner_agent="planner_agent"`；`executor_agent="executor_agent"` |

**规划器的提示词** 专为迭代式规划设计：

```
The origin plan is:
{past_plan}

We have finished the following steps:
{past_steps}

Please update the plan considering the mentioned information.
...
Please reply in JSON list format only, nothing else
```

`{past_plan}` 和 `{past_steps}` 占位符由 `PlanAndSolveAgent` 在每次迭代时填充，为规划器提供已完成工作和剩余任务的上下文。

**执行器的 `additional_prompt`** 限制它每次只执行一个步骤："You should only execute the current step, and do not execute other steps in our plan. Do not execute more than one step continuously or skip any step."

### 入口函数

```python
await mas.start_web_service(
    first_query="What time is it now? Please save it into time.txt."
)
```

启动 Web 服务，初始查询为需要时间查询和文件写入的复合任务。

## 核心概念

- **计划与执行模式** -- 将规划与执行分离。规划器创建结构化计划，执行器处理单个步骤，然后规划器根据进度重新规划。
- **`PlanAndSolveAgent`** -- 在规划器和执行器代理之间循环的编排器，直到计划完成。
- **`planner_agent` / `executor_agent`** -- 两个必需的子组件。规划器必须输出 JSON 格式的步骤列表；执行器必须能够执行单个步骤。
- **迭代式重新规划** -- 每个步骤完成后，规划器接收更新的上下文（`past_plan` + `past_steps`），并可以调整剩余计划。
- **`preset_tools`** -- `time_tools` 和 `file_tools` 是内置的 FunctionHub 工具，分别提供时间查询和文件读写功能。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 查询 "What time is it now? Please save it into time.txt." 被发送。
3. `PlanAndSolveAgent` 编排开始：
   - 规划器创建初始计划，例如 `["获取当前时间", "将时间保存到 time.txt"]`。
   - 执行器执行步骤 1：使用 `time_tools` 获取当前时间。
   - 规划器根据已完成步骤的上下文重新规划，生成剩余计划。
   - 执行器执行步骤 2：使用 `file_tools` 将时间写入 `time.txt`。
4. 最终结果确认两个步骤均已完成，时间已保存。
5. 创建了包含当前时间的 `time.txt` 文件。
