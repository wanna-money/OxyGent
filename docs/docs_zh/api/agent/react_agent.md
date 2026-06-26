# ReActAgent
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

`ReActAgent` 是实现 ReAct（推理与行动）范式的 Agent。

## 参数


| 参数                        | 类型 / 允许的值                                    | 默认值          | 描述                                               |
| ------------------------- | -------------------------------------------- | ------------- | -------------------------------------------------------- |
| `max_react_rounds`        | `int`                                        | `16`          | 每个请求的最大推理-行动循环次数                           |
| `is_discard_react_memory` | `bool`                                       | `True`        | 丢弃详细的 ReAct 记忆，仅保留问答对                       |
| `func_map_memory_order`   | `Callable[[int], int]`                       | `lambda x: x` | 将问答对的时间顺序映射为评分                              |
| `memory_max_tokens`       | `int`                                        | `24800`       | 记忆裁剪的 Token 预算                                   |
| `weight_short_memory`     | `int`                                        | `5`           | 短期记忆的重要性权重                                     |
| `weight_react_memory`     | `int`                                        | `1`           | ReAct 记忆片段的重要性权重                               |
| `trust_mode`              | `bool`                                       | `False`       | 为 `True` 时，将工具结果直接返回给用户                    |
| `func_parse_llm_response` | `Optional[Callable[[str], LLMResponse]]`     | `None`        | 自定义的原始 LLM 输出解析器                              |
| `func_reflexion`          | `Optional[Callable[[str, OxyRequest], str]]` | `None`        | 对 LLM 回答进行批判并要求修正的回调函数                    |

> 所有 `func_*` 钩子参数（包括 `func_parse_llm_response`、`func_reflexion`、`func_map_memory_order`）均支持同步和异步函数。

## 方法

| 方法                                                            | 协程（async）        | 返回值            | 用途（简要）                                                                                                    |
| ------------------------------------------------------------- | ----------------- | --------------- | ----------------------------------------------------------------------------------------------------------------- |
| `__init__(**kwargs)`                                          | 否                | `None`          | 初始化提示词、响应解析器、反思函数，并在配置向量搜索时附加 `retrieve_tools`                                           |
| `_default_reflexion(response, oxy_request)`                   | 否                | `Optional[str]` | 基本质量检查 - 如果 LLM 回复为空则返回反馈                                                                         |
| `_get_history(oxy_request, is_get_user_master_session=False)` | 是                | `Memory`        | 检索并智能裁剪对话历史（评分和 Token 限制）                                                                         |
| `_parse_llm_response(ori_response, oxy_request=None)`         | 是                | `LLMResponse`   | 检测 *tool call*、*answer* 或 *format error* 并结构化结果                                                          |
| `_execute(oxy_request)`                                       | 是                | `OxyResponse`   | 实现 ReAct 循环：思考 -> 调用工具 -> 观察 -> 重复直到得到答案或达到最大轮数                                            |

## 继承
 请参阅 [LocalAgent](./local_agent.md) 类以了解继承的参数和方法。

## 使用方式

`ReActAgent` 的简单用法如下：

```python
oxy.ReActAgent(
    name="time_agent",
    desc="A tool that can query the time",
    tools=["time_tools"],
    llm_model="default_llm",
    prompt=SYSTEM_PROMPT,
    timeout=30,
    is_multimodal_supported=False,
    semaphore=2
),
```
