# PlanAndSolveAgent
---
该类在类层次结构中的位置：


```markdown
[Oxy](./base_oxy.md)
├── [BaseFlow](./base_flow.md)
│   └── [BaseAgent](./base_agent.md)
│       ├── [LocalAgent](./local_agent.md)
│       │   ├── [ChatAgent](./chat_agent.md)
│       │   │   └── [RAGAgent](./rag_agent.md)
│       │   ├── [ReActAgent](./react_agent.md)
│       │   │   ├── [ShellUseAgent](./shell_use_agent.md)
│       │   │   └── [SkillAgent](./skill_agent.md)
│       │   ├── [ParallelAgent](./parallel_agent.md)
│       │   ├── [WorkflowAgent](./workflow_agent.md)
│       │   └── [PlanAndSolveAgent](./plan_and_solve_agent.md)
│       └── [RemoteAgent](./remote_agent.md)
│           ├── [SSEOxyGent](./sse_oxy_agent.md)
│           └── [A2AClientAgent](./a2a_client_agent.md)
└── [BaseTool](../tools/base_tools.md)
```

---

## 简介

`PlanAndSolveAgent` 是一个执行显式任务分解、逐步执行和动态重新规划的 Agent。它将规划委托给**规划 Agent**，将执行委托给**执行 Agent**，并通过基于 LLM 的监督器评估每一步，决定是继续、重新规划还是标记任务完成。

## 参数


| 参数                  | 类型 / 允许的值        | 默认值              | 描述                                                          |
| ------------------- | -------------------- | ----------------- | --------------------------------------------------------------- |
| `max_replan_rounds` | `int`                | `30`              | 允许的最大重新规划迭代次数。                                       |
| `planner_agent`     | `str`                | `"planner_agent"` | 负责生成计划（JSON 步骤列表）的 Agent 名称。                        |
| `executor_agent`    | `str`                | `"executor_agent"`| 负责执行每一步的 Agent 名称。                                      |

## 方法


| 方法                      | 协程（async）        | 返回值          | 用途（简要）                                                                                                                          |
| ----------------------- | ----------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `__init__(**kwargs)`    | 否                | `None`        | 初始化 Agent，并将 `planner_agent` 和 `executor_agent` 注册为允许的工具。                                                                  |
| `_execute(oxy_request)` | 是                | `OxyResponse` | 运行规划-求解循环：规划步骤、执行每一步、评估进度（继续/重新规划/完成）、必要时重新规划、最终汇总。 |

## 继承
 请参阅 [LocalAgent](./local_agent.md) 类以了解继承的参数和方法。

## 使用方式

`PlanAndSolveAgent` 的简单用法如下：

```python
oxy.PlanAndSolveAgent(
    name="plan_solve_agent",
    desc="An agent that plans and solves complex tasks",
    llm_model="default_llm",
    planner_agent="planner",
    executor_agent="executor",
    max_replan_rounds=5,
),
```

其中 `planner` 是一个返回 JSON 任务步骤列表的 Agent（例如 `["step1", "step2"]`），`executor` 是执行每个单独步骤的 Agent。
