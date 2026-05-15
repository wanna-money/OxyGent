# WorkflowAgent
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

## 简介

`WorkflowAgent` 是在 OxyGent 框架内执行自定义工作流函数的 Agent。它充当 Agent 系统与用户自定义工作流逻辑之间的桥梁。

## 参数


| 参数                        | 类型 / 允许的值                                    | 默认值          | 描述                                               |
| ------------------------- | -------------------------------------------- | ------------- | -------------------------------------------------------- |
| `func_workflow`        | `Optional[Callable]`                                        | `None`          | 要执行的工作流函数              |

## 方法


| 方法                                                            | 协程（async）        | 返回值            | 用途（简要）                                                                                                    |
| ------------------------------------------------------------- | ----------------- | --------------- | ----------------------------------------------------------------------------------------------------------------- |

| `_execute(oxy_request)`                                       | 是                | `OxyResponse`   | 执行 func_workflow                       |


## 继承
 请参阅 [LocalAgent](./local_agent.md) 类以了解继承的参数和方法。

## 使用方式
`WorkflowAgent` 的简单用法如下：

```python
    oxy.WorkflowAgent(
        name="workflow_agent",
        desc="An agent for executing workflows",
        func_workflow=my_workflow_function,
    ),
```

其中 `my_workflow_function` 是一个可调用对象，定义了该 Agent 要执行的工作流逻辑。
