# Reflexion
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

`Reflexion` 是一个通过自我反思来迭代改进答案的 Flow。它协调工作智能体（生成答案）和反思智能体（评估并提供反馈）之间的配合，通过多轮优化实现响应的持续改进。

## 参数

| 参数                               | 类型 / 允许值            | 默认值                                         | 描述                                      |
| ---------------------------------- | ------------------------ | ---------------------------------------------- | ----------------------------------------- |
| `max_reflexion_rounds`             | `int`                    | `3`                                            | 最大 Reflexion 迭代次数。                   |
| `worker_agent`                     | `str`                    | `"worker_agent"`                               | 用于生成答案的工作智能体名称。               |
| `reflexion_agent`                  | `str`                    | `"reflexion_agent"`                            | 用于评估的反思智能体名称。                   |
| `func_parse_worker_response`       | `Optional[Callable]`     | `None`                                         | 自定义工作智能体响应解析函数。               |
| `func_parse_reflexion_response`    | `Optional[Callable]`     | `None`                                         | 自定义反思智能体响应解析函数。               |
| `pydantic_parser_reflexion`        | `PydanticOutputParser`   | `PydanticOutputParser(ReflexionEvaluation)`    | 反思响应的 Pydantic 解析器。                |
| `evaluation_template`              | `str`                    | 默认模板                                        | 评估查询的模板。                            |
| `improvement_template`             | `str`                    | 默认模板                                        | 改进查询的模板。                            |

## 方法

| 方法                    | 协程 (async) | 返回值        | 用途（简述）                                                             |
| ----------------------- | ------------ | ------------- | ----------------------------------------------------------------------- |
| `__init__(**kwargs)`    | 否           | `None`        | 将工作智能体和反思智能体注册为允许的工具；设置默认解析器。                  |
| `_execute(oxy_request)` | 是           | `OxyResponse` | 执行 Reflexion 流程：工作智能体生成、评估智能体评审，循环迭代。            |

## 继承
 请参阅 [BaseFlow](../agent/base_flow.md) 类了解继承的参数和方法。

## 用法

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

`MathReflexion` 是 `Reflexion` 的专用子类，预配置用于数学问题求解。它设置了默认的智能体名称（`math_expert_agent`、`math_checker_agent`）和数学专用的评估模板。

```python
oxy.MathReflexion(
    name="math_reflexion",
    worker_agent="math_expert_agent",
    reflexion_agent="math_checker_agent",
)
```
