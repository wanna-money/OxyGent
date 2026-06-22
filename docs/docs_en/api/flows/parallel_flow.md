# ParallelFlow
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

`ParallelFlow` is a flow that executes multiple tools or agents concurrently. It orchestrates concurrent execution of the same request across all permitted tools simultaneously using `asyncio.gather` and aggregates their results into a unified response.

## Parameters


| Parameter       | Type / Allowed value | Default | Description                                                                     |
| --------------- | -------------------- | ------- | ------------------------------------------------------------------------------- |
| *None declared* | --                   | --      | `ParallelFlow` adds no new fields; it inherits everything from `BaseFlow`.      |

## Methods

| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                                                  |
| ----------------------- | ----------------- | ------------- | ---------------------------------------------------------------------------------- |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | Execute the request concurrently across all permitted tools and aggregate results. |

## Inherited
 Please refer to the [BaseFlow](../agent/base_flow.md) class for inherited parameters and methods.

## Usage

```python
oxy.ParallelFlow(
    name="parallel_eval",
    desc="Run multiple agents in parallel",
    permitted_tool_name_list=["agent_a", "agent_b", "agent_c"],
)
```
