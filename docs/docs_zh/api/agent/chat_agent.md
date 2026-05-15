# ChatAgent
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

## 参数


| 参数              | 类型 / 允许的值        | 默认值    | 描述                                                                                                                                         |
| --------------- | -------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *无新增参数*       | —                    | —       | `ChatAgent` **未引入新的数据字段**；它**继承**了 `LocalAgent`（以及 `BaseAgent`/`Oxy`）中已定义的所有参数。 |


## 方法


| 方法                          | 协程（async）        | 返回值          | 用途（简要）                                                                                                                                                                        |
| ----------------------------- | ----------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `_execute(self, oxy_request)` | 是                | `OxyResponse` | 构建临时对话**记忆**，追加最新的用户查询，合并 `llm_params`，然后调用配置的 LLM 模型；将模型回复封装在 `OxyResponse` 中返回。 |

## 继承
 请参阅 [LocalAgent](./local_agent.md) 类以了解继承的参数和方法。

## 使用方式

`ChatAgent` 的简单用法如下：
```python
oxy.ChatAgent(
    name="planner_agent",
    desc="An agent capable of making plans",
    llm_model="default_llm",
    prompt="""
        For a given goal, create a simple and step-by-step executable plan. \
        The plan should be concise, with each step being an independent and complete functional module—not an atomic function—to avoid over-fragmentation. \
        The plan should consist of independent tasks that, if executed correctly, will lead to the correct answer. \
        Ensure that each step is actionable and includes all necessary information for execution. \
        The result of the final step should be the final answer. Make sure each step contains all the information required for its execution. \
        Do not add any redundant steps, and do not skip any necessary steps.
    """.strip(),
),
```
