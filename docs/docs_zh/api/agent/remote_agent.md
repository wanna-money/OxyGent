# RemoteAgent
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

`RemoteAgent` 是与远程系统通信的 Agent 基类。

该 Agent 为通过 HTTP/HTTPS 连接远程 Agent 系统并与之交互提供了基础能力。

## 参数


| 参数           | 类型 / 允许的值        | 默认值             | 描述                                                                   |
| ------------ | -------------------- | ---------------- | ------------------------------------------------------------------------ |
| `server_url` | `AnyUrl`             | 必须赋值           | 远程 Agent 服务器的 URL；必须以 `http://` 或 `https://` 开头              |
| `org`        | `dict`               | `{}`             | 从远程系统获取的缓存组织结构树                                             |


## 方法


| 方法                          | 协程（async）        | 返回值          | 用途（简要）                                                                                       |
| ----------------------------- | ----------------- | ------------- | ---------------------------------------------------------------------------------------------------------- |
| `check_protocol(cls, v)`      | 否                | `AnyUrl`      | 字段验证器，拒绝协议不是 HTTP/HTTPS 的 URL                                                           |
| `get_org(self)`               | 否                | `list[dict]`  | 深拷贝 `self.org["children"]`，将每个节点标记为 `is_remote = True`，并返回更新后的列表                   |
| `_execute(self, oxy_request)` | 是                | `OxyResponse` | 远程调用的抽象占位符；当前会抛出 `NotImplementedError`                                                 |

## 继承
 请参阅 [BaseAgent](./base_agent.md) 类以了解继承的参数和方法。
 
## 使用方式

`RemoteAgent` 类必须被继承使用。
