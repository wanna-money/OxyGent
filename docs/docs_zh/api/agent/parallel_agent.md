# ParallelAgent
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


| 参数              | 类型 / 允许的值        | 默认值    | 描述                                                                                                    |
| --------------- | -------------------- | ------- | ---------------------------------------------------------------------------------------------------------------- |
| *无新增参数*       | —                    | —       | `ParallelAgent` **未新增数据字段**；它继承了 `LocalAgent`（及其基类）的所有参数。 |


## 方法


| 方法                          | 协程（async）        | 返回值          | 用途（简要）                                                                                                                                                                |
| ----------------------------- | ----------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `_execute(self, oxy_request)` | 是                | `OxyResponse` | 将传入任务**并发**分发给所有允许的工具，收集它们的输出，然后使用 Agent 的 LLM 将这些并行结果汇总为单一响应。 |

## 继承
 请参阅 [LocalAgent](./local_agent.md) 类以了解继承的参数和方法。
 
## 使用方式

`ParallelAgent` 的简单用法如下：
```python
    oxy.ParallelAgent(
        name="expert_panel",
        llm_model="default_llm",
        desc="Expert panel parallel evaluation",
        permitted_tool_name_list=[
            "tech_expert",
            "business_expert",
            "risk_expert",
            "legal_expert",
        ],
        is_master=True,
    ),
```
