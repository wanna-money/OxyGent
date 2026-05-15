# Reflexion
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

`Reflexion` is a flow for iterative answer improvement through self-reflection. It coordinates between a worker agent that generates answers and a reflexion agent that evaluates and provides feedback, enabling continuous improvement of responses through multiple rounds of refinement.

## Parameters

| Parameter                        | Type / Allowed value   | Default                                      | Description                                        |
| -------------------------------- | ---------------------- | -------------------------------------------- | -------------------------------------------------- |
| `max_reflexion_rounds`           | `int`                  | `3`                                          | Maximum reflexion iterations.                      |
| `worker_agent`                   | `str`                  | `"worker_agent"`                             | Worker agent name for generating answers.          |
| `reflexion_agent`                | `str`                  | `"reflexion_agent"`                          | Reflexion agent name for evaluation.               |
| `func_parse_worker_response`     | `Optional[Callable]`   | `None`                                       | Custom worker response parser function.            |
| `func_parse_reflexion_response`  | `Optional[Callable]`   | `None`                                       | Custom reflexion response parser function.         |
| `pydantic_parser_reflexion`      | `PydanticOutputParser` | `PydanticOutputParser(ReflexionEvaluation)`  | Pydantic parser for reflexion responses.           |
| `evaluation_template`            | `str`                  | Default template                             | Template for evaluation query.                     |
| `improvement_template`           | `str`                  | Default template                             | Template for improvement query.                    |

## Methods

| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                                              |
| ----------------------- | ----------------- | ------------- | ------------------------------------------------------------------------------ |
| `__init__(**kwargs)`    | No                | `None`        | Register worker and reflexion agents as permitted tools; set default parsers.  |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | Execute the reflexion flow: worker generates, evaluator critiques, loop.       |

## Inherited
 Please refer to the [BaseFlow](../agent/base_flow.md) class for inherited parameters and methods.

## Usage

```python
oxy.Reflexion(
    name="general_reflexion",
    worker_agent="worker_agent",
    reflexion_agent="reflexion_agent",
    max_reflexion_rounds=3,
)
```

---

## MathReflexion

`MathReflexion` is a specialized subclass of `Reflexion` pre-configured for mathematical problem-solving. It sets default agent names (`math_expert_agent`, `math_checker_agent`) and a math-specific evaluation template.

```python
oxy.MathReflexion(
    name="math_reflexion",
    worker_agent="math_expert_agent",
    reflexion_agent="math_checker_agent",
)
```
