# ShellUseAgent
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

`ShellUseAgent` is a ReAct-style agent that uses SSH shell tools to accomplish tasks on remote machines. It establishes an SSH connection during initialization, then uses a ReAct loop to iteratively send shell commands and observe their output until the task is completed.

## Parameters


| Parameter   | Type / Allowed value | Default | Description                                                                    |
| ----------- | -------------------- | ------- | ------------------------------------------------------------------------------ |
| `auth_info` | `dict`               | `{}`    | SSH connection parameters passed to `paramiko.SSHClient.connect()` (e.g. `hostname`, `username`, `password`). |

## Methods


| Method                                          | Coroutine (async) | Return Value  | Purpose (concise)                                                                                             |
| ----------------------------------------------- | ----------------- | ------------- | ------------------------------------------------------------------------------------------------------------- |
| `init()`                                        | Yes               | `None`        | Calls parent init, then opens an SSH channel via `paramiko` and stores it in `mas.global_data`.               |
| `_parse_llm_response(ori_response, oxy_request)` | No               | `LLMResponse` | Extracts shell code blocks from LLM output and classifies the response as `TOOL_CALL`, `ANSWER`, or `ERROR_PARSE`. |
| `_execute(oxy_request)`                          | Yes              | `OxyResponse` | Runs the ReAct loop: build terminal context, call LLM, execute shell commands via `ssh_tool`, repeat until done.  |

## Inherited
 Please refer to the [ReActAgent](./react_agent.md) class for inherited parameters and methods.

## Usage

A simple usage of `ShellUseAgent` is like:

```python
    oxy.ShellUseAgent(
        name="shell_agent",
        desc="An agent that operates a remote Linux machine",
        llm_model="default_llm",
        prompt=SHELL_SYSTEM_PROMPT,
        auth_info={
            "hostname": "192.168.1.100",
            "username": "admin",
            "password": "password",
        },
        tools=["ssh_tool"],
    ),
```
