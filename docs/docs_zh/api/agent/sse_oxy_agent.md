# SSEOxyGent
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

`SSEOxyGent` 是通过 SSE（Server-Sent Events）与远程多 Agent 系统通信的 Agent。

## 参数


| 参数                    | 类型 / 允许的值        | 默认值    | 描述                                                                                                                           |
| --------------------- | -------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `is_share_call_stack` | `bool`               | `True`  | 是否将调用者的 `call_stack`/`node_id_stack` 转发给远程 Agent，以便工具调用链在上游保持可见。 |


## 方法


| 方法                      | 协程（async）        | 返回值          | 用途（简要）                                                                                                                                                                        |
| ----------------------- | ----------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `init()`                | 是                | `None`        | 调用父类 `init`，然后在 `server_url` 上查询 `GET /get_organization` 以将远程组织结构树缓存到 `self.org` 中。                                                              |
| `_execute(oxy_request)` | 是                | `OxyResponse` | 打开到 `POST /sse/chat` 的 **SSE** 连接，将 tool-call / observation 事件流式回传给 MAS，累积最终回答，并将其封装在 `OxyResponse (COMPLETED)` 中返回。 |

## 继承
 请参阅 [RemoteAgent](./remote_agent.md) 类以了解继承的参数和方法。

## 使用方式

`SSEOxyGent` 的简单用法如下：

```python
    oxy.SSEOxyGent(
        name="time_agent",
        desc="An tool for time query",
        server_url="http://127.0.0.1:8082",
    ),
```
