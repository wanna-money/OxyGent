# Workflow
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

`Workflow` is a flow that executes custom workflow functions within the OxyGent flow system. It serves as a bridge between the flow framework and user-defined workflow logic, enabling execution of custom workflow functions that accept `OxyRequest` and return `OxyResponse`.

## Parameters


| Parameter        | Type / Allowed value | Default | Description                                   |
| ---------------- | -------------------- | ------- | --------------------------------------------- |
| `func_workflow`  | `Optional[Callable]` | `None`  | The custom workflow function to execute.       |

## Methods


| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                                  |
| ----------------------- | ----------------- | ------------- | ------------------------------------------------------------------ |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | Execute the custom workflow function with the given request.       |

## Inherited
 Please refer to the [BaseFlow](../agent/base_flow.md) class for inherited parameters and methods.

## Usage

```python
oxy.Workflow(
    name="custom_workflow",
    desc="A flow for executing custom workflow functions",
    func_workflow=my_workflow_function,
)
```

Where `my_workflow_function` is an async callable that defines the workflow logic.
