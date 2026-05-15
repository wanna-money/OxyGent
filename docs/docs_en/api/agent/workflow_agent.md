# WorkflowAgent
---
The position of the class is:


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

## Introduction

`WorkflowAgent` is an agent that executes custom workflow functions within the OxyGent framework. It serves as a bridge between the agent system and user-defined workflow logic.

## Parameters


| Parameter                 | Type / Allowed value                         | Default       | Description                                              |
| ------------------------- | -------------------------------------------- | ------------- | -------------------------------------------------------- |
| `func_workflow`        | `Optional[Callable]`                                        | `None`          | The workflow function to execute              |

## Methods


| Method                                                        | Coroutine (async) | Return Value    | Purpose (concise)                                                                                                 |
| ------------------------------------------------------------- | ----------------- | --------------- | ----------------------------------------------------------------------------------------------------------------- |

| `_execute(oxy_request)`                                       | Yes               | `OxyResponse`   | Execute func_workflow                       |


## Inherited
 Please refer to the [LocalAgent](./local_agent.md) class for inherited parameters and methods.

## Usage
A simple usage of `WorkflowAgent` is like:

```python
    oxy.WorkflowAgent(
        name="workflow_agent",
        desc="An agent for executing workflows",
        func_workflow=my_workflow_function,
    ),
```

Where `my_workflow_function` is a callable that defines the workflow logic to be executed by the agent.
