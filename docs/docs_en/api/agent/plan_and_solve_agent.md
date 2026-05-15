# PlanAndSolveAgent
---
The position of the class is:


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

## Introduction

`PlanAndSolveAgent` is an agent that performs explicit task decomposition, step-by-step execution, and dynamic replanning. It delegates planning to a **planner agent** and execution to an **executor agent**, with an LLM-based supervisor that evaluates each step and decides whether to continue, replan, or mark the task as complete.

## Parameters


| Parameter           | Type / Allowed value | Default           | Description                                                     |
| ------------------- | -------------------- | ----------------- | --------------------------------------------------------------- |
| `max_replan_rounds` | `int`                | `30`              | Maximum number of replanning iterations allowed.                |
| `planner_agent`     | `str`                | `"planner_agent"` | Name of the agent responsible for generating the plan (a JSON list of steps). |
| `executor_agent`    | `str`                | `"executor_agent"`| Name of the agent responsible for executing each step.          |

## Methods


| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                                                                                                               |
| ----------------------- | ----------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `__init__(**kwargs)`    | No                | `None`        | Initialise the agent and register `planner_agent` and `executor_agent` as permitted tools.                                                      |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | Run the plan-and-solve loop: plan steps, execute each step, evaluate progress (continue / replan / complete), replan if needed, summarise at end.|

## Inherited
 Please refer to the [LocalAgent](./local_agent.md) class for inherited parameters and methods.

## Usage

A simple usage of `PlanAndSolveAgent` is like:

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

Where `planner` is an agent that returns a JSON list of task steps (e.g. `["step1", "step2"]`), and `executor` is an agent that executes each individual step.
