# BaseFlow

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

`BaseFlow` 是 OxyGent 框架的基础流程模块。

该模块提供了 `BaseFlow` 类，作为 OxyGent 系统中所有 Agent 和流程的抽象基类。流程是特殊的 Oxy 实例，用于编排复杂的工作流并协调多个 Agent 或工具。

## 参数


| 参数                     | 类型 / 允许的值        | 默认值      | 描述                                                                      |
| ------------------------ | -------------------- | --------- | ------------------------------------------------------------------------- |
| `is_permission_required` | `bool`               | `True`    | 该流程在运行前是否需要显式授权。                                             |
| `category`               | `str`                | `"agent"` | 继承自 `Oxy` 的类别标志；流程后续可能会将其覆盖为 `"flow"`。                  |
| `is_master`              | `bool`               | `False`   | 设置后将该流程标记为中央"MASTER"控制器。                                     |


## 方法


| 方法                          | 协程（async）        | 用途（简要）                                                                                    |
| ----------------------------- | ----------------- | --------------------------------------------------------------------------------------------------------- |
| `_execute(self, oxy_request)` | 是                | 流程的核心执行钩子；子类**必须**实现——当前方法体会抛出 `NotImplementedError`。                         |


## 继承
 请参阅 [Oxy](./base_oxy.md) 类以了解继承的参数和方法。

## 使用方式

`BaseFlow` 类必须被继承使用。
