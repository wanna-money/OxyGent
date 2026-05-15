# PlanAndSolve
---
The position of the class is:


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

## Introduction

`PlanAndSolve` is a flow that implements a plan-and-solve strategy for complex problem-solving. It breaks down complex tasks into structured plans through a planner agent, then executes each step sequentially through an executor agent, with optional replanning capabilities for adaptive execution.

## Parameters

| Parameter                        | Type / Allowed value | Default                              | Description                                                        |
| -------------------------------- | -------------------- | ------------------------------------ | ------------------------------------------------------------------ |
| `max_replan_rounds`              | `int`                | `30`                                 | Maximum number of replanning iterations allowed.                   |
| `planner_agent_name`             | `str`                | `"planner_agent"`                    | Name of the agent used to generate plans.                          |
| `pre_plan_steps`                 | `List[str]`          | `None`                               | Pre-defined plan steps to use instead of generating new ones.      |
| `enable_replanner`               | `bool`               | `False`                              | Whether to enable dynamic replanning during execution.             |
| `replanner_agent_name`           | `str`                | `"replanner_agent"`                  | Name of the agent used for replanning on failure.                  |
| `executor_agent_name`            | `str`                | `"executor_agent"`                   | Name of the agent that executes individual plan steps.             |
| `llm_model`                      | `str`                | `"default_llm"`                      | LLM model name for fallback operations.                            |
| `func_parse_planner_response`    | `Optional[Callable]` | `None`                               | Custom parser for planner agent responses.                         |
| `pydantic_parser_planner`        | `PydanticOutputParser` | `PydanticOutputParser(Plan)`       | Pydantic parser for planner responses.                             |
| `func_parse_replanner_response`  | `Optional[Callable]` | `None`                               | Custom parser for replanner responses.                             |
| `pydantic_parser_replanner`      | `PydanticOutputParser` | `PydanticOutputParser(Action)`     | Pydantic parser for replanner responses.                           |

## Methods

| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                                                       |
| ----------------------- | ----------------- | ------------- | --------------------------------------------------------------------------------------- |
| `__init__(**kwargs)`    | No                | `None`        | Register `planner_agent_name` and `executor_agent_name` as permitted tools.             |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | Execute the plan-and-solve workflow: plan steps, execute sequentially, replan if needed. |

## Inherited
 Please refer to the [BaseFlow](../agent/base_flow.md) class for inherited parameters and methods.

## Usage

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
