# ActorLLM

---
该类在类层次结构中的位置：

```markdown
[Oxy](../agent/base_oxy.md)
├── [BaseFlow](../agent/base_flow.md)
├── [BaseLLM](./base_llm.md)
│   ├── [RemoteLLM](./remote_llm.md)
│   │   ├── [HttpLLM](./http_llm.md)
│   │   └── [OpenAILLM](./openai_llm.md)
│   ├── [LocalLLM](./local_llm.md)
│   ├── [ActorLLM](./actor_llm.md)
│   ├── [LiteLLM](./lite_llm.md)
│   └── [MockLLM](./mock_llm.md)
└── [BaseTool](../tools/base_tools.md)
```

---

## 简介

`ActorLLM` 通过 Ray actor（或在未安装 Ray 时通过 `ray_adapter` 适配层）在本地 Transformer 模型上运行推理。它从标准消息格式中提取 system/user 消息，并将生成任务委托给 actor 执行。

## 参数

| 参数                  | 类型 / 允许值        | 默认值   | 描述                                                                                           |
| -------------------- | -------------------- | ------- | ---------------------------------------------------------------------------------------------- |
| `name`               | `str`                | `"llm"` | LLM 实例的标识符。                                                                                 |
| `actor_llm`          | `Any`                | `None`  | Ray actor 句柄（或兼容对象），需暴露 `agent_generate_one_step` 方法。                              |
| `actor_llm_timeout`  | `float`              | `0.0`   | actor 调用的超时时间（秒）。`0` 表示无超时。可通过环境变量 `OXYGENT_ACTOR_LLM_TIMEOUT` 覆盖。       |
| `raise_on_error`     | `bool`               | `True`  | 生成失败时是否抛出 `RuntimeError`。设为 `False` 时，返回状态为 `FAILED` 的 `OxyResponse`。          |

## 方法

| 方法                    | 协程 (async) | 返回值        | 用途（简述）                                                                  |
| ----------------------- | ------------ | ------------- | ---------------------------------------------------------------------------- |
| `_execute(oxy_request)` | 是           | `OxyResponse` | 提取 system/user 消息，调用 actor 的 `agent_generate_one_step` 方法并返回结果。  |

## 继承

请参阅 [BaseLLM](./base_llm.md) 类了解继承的参数和方法。

## 用法

```python
oxy.ActorLLM(
    name="actor_llm",
    actor_llm=your_ray_actor_handle,
    actor_llm_timeout=120,
)
```
