# RAGAgent
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

`RAGAgent` is a retrieval-augmented generation agent that fetches relevant context before LLM generation. It extends `ChatAgent` by injecting retrieved knowledge into the prompt before the LLM call, enabling grounded responses based on external data sources.

## Parameters


| Parameter                 | Type / Allowed value | Default       | Description                                                                                             |
| ------------------------- | -------------------- | ------------- | ------------------------------------------------------------------------------------------------------- |
| `knowledge_placeholder`   | `str`                | `"knowledge"` | Placeholder key in the prompt template where retrieved knowledge will be injected.                       |
| `func_retrieve_knowledge` | `Callable`           | must be assigned | An async callable that takes an `OxyRequest` and returns the retrieved knowledge string.              |

## Methods


| Method                        | Coroutine (async) | Return Value  | Purpose (concise)                                                                                   |
| ----------------------------- | ----------------- | ------------- | --------------------------------------------------------------------------------------------------- |
| `set_default_prompt()`        | No                | `self`        | Pydantic model validator that injects a default RAG prompt if none was provided.                    |
| `_pre_process(oxy_request)`   | Yes               | `OxyRequest`  | Calls the parent pre-process, then invokes `func_retrieve_knowledge` and injects the result.        |

## Inherited
 Please refer to the [ChatAgent](./chat_agent.md) class for inherited parameters and methods.

## Usage

A simple usage of `RAGAgent` is like:

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
