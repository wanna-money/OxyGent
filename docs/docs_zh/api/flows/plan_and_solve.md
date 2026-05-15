# PlanAndSolve
---
该类在类层次结构中的位置：


```markdown
[Oxy](../agent/base_oxy.md)
├── [BaseFlow](../agent/base_flow.md)
│   ├── [Workflow](./workflow.md)
│   ├── [ParallelFlow](./parallel_flow.md)
│   ├── [PlanAndSolve](./plan_and_solve.md)
│   ├── [Reflexion](./reflexion.md)
│   │   └── [MathReflexion](./reflexion.md)
│   └── [BaseAgent](../agent/base_agent.md)
├── [BaseLLM](../llms/base_llm.md)
└── [BaseTool](../tools/base_tools.md)
```

---

## 简介

`PlanAndSolve` 是一个实现"规划-求解"策略的 Flow，用于解决复杂问题。它通过规划智能体将复杂任务分解为结构化的计划，然后通过执行智能体按顺序执行每个步骤，并可选地支持动态重新规划以实现自适应执行。

## 参数

| 参数                               | 类型 / 允许值          | 默认值                               | 描述                                                     |
| ---------------------------------- | ---------------------- | ------------------------------------ | -------------------------------------------------------- |
| `max_replan_rounds`                | `int`                  | `30`                                 | 允许的最大重新规划迭代次数。                                |
| `planner_agent_name`               | `str`                  | `"planner_agent"`                    | 用于生成计划的智能体名称。                                  |
| `pre_plan_steps`                   | `List[str]`            | `None`                               | 预定义的计划步骤，用于替代动态生成的计划。                    |
| `enable_replanner`                 | `bool`                 | `False`                              | 是否在执行过程中启用动态重新规划。                           |
| `replanner_agent_name`             | `str`                  | `"replanner_agent"`                  | 在失败时用于重新规划的智能体名称。                           |
| `executor_agent_name`              | `str`                  | `"executor_agent"`                   | 执行各个计划步骤的智能体名称。                               |
| `llm_model`                        | `str`                  | `"default_llm"`                      | 用于回退操作的 LLM 模型名称。                               |
| `func_parse_planner_response`      | `Optional[Callable]`   | `None`                               | 规划智能体响应的自定义解析器。                               |
| `pydantic_parser_planner`          | `PydanticOutputParser` | `PydanticOutputParser(Plan)`         | 规划响应的 Pydantic 解析器。                                |
| `func_parse_replanner_response`    | `Optional[Callable]`   | `None`                               | 重新规划响应的自定义解析器。                                 |
| `pydantic_parser_replanner`        | `PydanticOutputParser` | `PydanticOutputParser(Action)`       | 重新规划响应的 Pydantic 解析器。                            |

## 方法

| 方法                    | 协程 (async) | 返回值        | 用途（简述）                                                                      |
| ----------------------- | ------------ | ------------- | -------------------------------------------------------------------------------- |
| `__init__(**kwargs)`    | 否           | `None`        | 将 `planner_agent_name` 和 `executor_agent_name` 注册为允许的工具。                |
| `_execute(oxy_request)` | 是           | `OxyResponse` | 执行"规划-求解"工作流：规划步骤、按顺序执行、必要时重新规划。                         |

## 继承
 请参阅 [BaseFlow](../agent/base_flow.md) 类了解继承的参数和方法。

## 用法

```python
oxy.PlanAndSolve(
    name="master_agent",
    llm_model="default_llm",
    is_master=True,
    planner_agent_name="planner_agent",
    executor_agent_name="executor_agent",
    enable_replanner=False,
    timeout=100,
)
```
