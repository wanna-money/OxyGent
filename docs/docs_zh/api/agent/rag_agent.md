# RAGAgent
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

`RAGAgent` 是一个检索增强生成 Agent，在 LLM 生成之前获取相关上下文。它扩展了 `ChatAgent`，在 LLM 调用之前将检索到的知识注入提示词中，从而基于外部数据源生成有据可依的回复。

## 参数


| 参数                        | 类型 / 允许的值        | 默认值          | 描述                                                                                          |
| ------------------------- | -------------------- | ------------- | ------------------------------------------------------------------------------------------------------- |
| `knowledge_placeholder`   | `str`                | `"knowledge"` | 提示词模板中用于注入检索知识的占位符键名。                                                         |
| `func_retrieve_knowledge` | `Callable`           | 必须赋值        | 一个异步可调用对象，接收 `OxyRequest` 并返回检索到的知识字符串。                                    |

## 方法


| 方法                          | 协程（async）        | 返回值          | 用途（简要）                                                                                  |
| ----------------------------- | ----------------- | ------------- | --------------------------------------------------------------------------------------------------- |
| `set_default_prompt()`        | 否                | `self`        | Pydantic 模型验证器，在未提供提示词时注入默认的 RAG 提示词。                                      |
| `_pre_process(oxy_request)`   | 是                | `OxyRequest`  | 调用父类预处理，然后调用 `func_retrieve_knowledge` 并注入结果。                                  |

## 继承
 请参阅 [ChatAgent](./chat_agent.md) 类以了解继承的参数和方法。

## 使用方式

`RAGAgent` 的简单用法如下：

```python
    async def retrieve_knowledge(oxy_request):
        query = oxy_request.get_query()
        # Your retrieval logic here (e.g., vector DB search)
        return "Retrieved context: ..."

    oxy.RAGAgent(
        name="rag_agent",
        desc="A RAG-powered assistant",
        llm_model="default_llm",
        func_retrieve_knowledge=retrieve_knowledge,
    ),
```
