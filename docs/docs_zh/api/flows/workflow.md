# Workflow
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

`Workflow` 是在 OxyGent Flow 系统中执行自定义工作流函数的 Flow。它充当 Flow 框架与用户自定义工作流逻辑之间的桥梁，支持执行接受 `OxyRequest` 并返回 `OxyResponse` 的自定义工作流函数。

## 参数


| 参数             | 类型 / 允许值        | 默认值   | 描述                                   |
| ---------------- | -------------------- | ------- | -------------------------------------- |
| `func_workflow`  | `Optional[Callable]` | `None`  | 要执行的自定义工作流函数。               |

## 方法


| 方法                    | 协程 (async) | 返回值        | 用途（简述）                                       |
| ----------------------- | ------------ | ------------- | -------------------------------------------------- |
| `_execute(oxy_request)` | 是           | `OxyResponse` | 使用给定的请求执行自定义工作流函数。                 |

## 继承
 请参阅 [BaseFlow](../agent/base_flow.md) 类了解继承的参数和方法。

## 用法

```python
oxy.Workflow(
    name="custom_workflow",
    desc="A flow for executing custom workflow functions",
    func_workflow=my_workflow_function,
)
```

其中 `my_workflow_function` 是一个定义工作流逻辑的异步可调用对象。
