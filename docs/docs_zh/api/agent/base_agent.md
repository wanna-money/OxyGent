# BaseAgent
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

`BaseAgent` 是所有 Agent 的基类。

Agent 是应用程序的核心构建模块。典型的 Agent 使用大语言模型（LLM）进行思考，并可以调用其他 Agent 或工具来执行功能。

## 参数


| 参数             | 类型 / 允许的值        | 默认值                              | 描述                                                                      |
| -------------- | -------------------- | --------------------------------- | ------------------------------------------------------------------------------- |
| `category`     | `str`                | `"agent"`                         | 类别标志，标识该对象为 *agent* 而非工具或流程。                                  |
| `input_schema` | `dict[str, Any]`     | `Config.get_agent_input_schema()` | 该 Agent 接受的输入参数的 JSON Schema 风格定义。                                |

## 方法


| 方法                                    | 协程（async）        | 返回值         | 用途（简要）                                                                                                          |
| ------------------------------------- | ----------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `_pre_process(self, oxy_request)`     | 是                | `OxyRequest` | 解析 trace 栈，当调用者是用户时加载父级 trace 元数据，然后委托给父类的预处理器。                                             |
| `_pre_save_data(self, oxy_request)`   | 是                | `None`       | 在执行开始前将初始 trace 记录持久化到 Elasticsearch。                                                                      |
| `_post_save_data(self, oxy_response)` | 是                | `None`       | 执行完成后用最终输出更新 trace，并（可选地）记录对话历史。                                                                   |

## 继承关系

`BaseAgent` 类继承自 `Oxy`，所有 Agent 都必须继承该类。


## 继承
 请参阅 [Oxy](./base_oxy.md) 类以了解继承的参数和方法。
## 使用方式

`BaseAgent` 类必须被继承使用。
