# ShellUseAgent
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

`ShellUseAgent` 是一个 ReAct 风格的 Agent，使用 SSH Shell 工具在远程机器上完成任务。它在初始化阶段建立 SSH 连接，然后通过 ReAct 循环迭代发送 Shell 命令并观察输出，直到任务完成。

## 参数


| 参数          | 类型 / 允许的值        | 默认值    | 描述                                                                           |
| ----------- | -------------------- | ------- | ------------------------------------------------------------------------------ |
| `auth_info` | `dict`               | `{}`    | 传递给 `paramiko.SSHClient.connect()` 的 SSH 连接参数（例如 `hostname`、`username`、`password`）。 |

## 方法


| 方法                                              | 协程（async）        | 返回值          | 用途（简要）                                                                                                  |
| ----------------------------------------------- | ----------------- | ------------- | ------------------------------------------------------------------------------------------------------------- |
| `init()`                                        | 是                | `None`        | 调用父类 init，然后通过 `paramiko` 打开 SSH 通道并存储在 `mas.global_data` 中。                                  |
| `_parse_llm_response(ori_response, oxy_request)` | 否               | `LLMResponse` | 从 LLM 输出中提取 Shell 代码块，并将响应分类为 `TOOL_CALL`、`ANSWER` 或 `ERROR_PARSE`。                          |
| `_execute(oxy_request)`                          | 是               | `OxyResponse` | 运行 ReAct 循环：构建终端上下文、调用 LLM、通过 `ssh_tool` 执行 Shell 命令、重复直到完成。                          |

## 继承
 请参阅 [ReActAgent](./react_agent.md) 类以了解继承的参数和方法。

## 使用方式

`ShellUseAgent` 的简单用法如下：

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
