# ParallelFlow
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

`ParallelFlow` 是一个并发执行多个工具或智能体的 Flow。它使用 `asyncio.gather` 协调所有被允许的工具同时对同一请求进行并发执行，并将各自的结果汇总为统一的响应。

## 参数


| 参数            | 类型 / 允许值        | 默认值   | 描述                                                                     |
| --------------- | -------------------- | ------- | ------------------------------------------------------------------------ |
| *无新增参数*     | --                   | --      | `ParallelFlow` 未添加新字段；所有内容均继承自 `BaseFlow`。                  |

## 方法

| 方法                    | 协程 (async) | 返回值        | 用途（简述）                                                         |
| ----------------------- | ------------ | ------------- | -------------------------------------------------------------------- |
| `_execute(oxy_request)` | 是           | `OxyResponse` | 在所有被允许的工具上并发执行请求并汇总结果。                            |

## 继承
 请参阅 [BaseFlow](../agent/base_flow.md) 类了解继承的参数和方法。

## 用法

```python
oxy.ParallelFlow(
    name="parallel_eval",
    desc="Run multiple agents in parallel",
    permitted_tool_name_list=["agent_a", "agent_b", "agent_c"],
)
```
