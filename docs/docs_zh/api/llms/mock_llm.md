# MockLLM

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
│   └── [MockLLM](./mock_llm.md)
└── [BaseTool](../tools/base_tools.md)
```

---

## 简介

`MockLLM` 是用于单元测试的确定性 LLM 桩模块。它返回可配置的模拟响应，无需调用任何真实模型，非常适合需要可预测 LLM 行为的测试场景。

## 参数

| 参数                | 类型 / 允许值  | 默认值   | 描述                                                                   |
| ------------------- | -------------- | ------- | ---------------------------------------------------------------------- |
| `func_mock_process` | `Callable`     | `None`  | 用户提供的异步模拟函数。默认使用内部的 `_mock_process`。                  |

## 方法

| 方法                          | 协程 (async) | 返回值        | 用途（简述）                                                    |
| ----------------------------- | ------------ | ------------- | -------------------------------------------------------------- |
| `_mock_process(oxy_request)`  | 是           | `str`         | 默认模拟：等待 1 秒后返回字符串字面量 `"output"`。                |
| `_execute(oxy_request)`       | 是           | `OxyResponse` | 调用 `func_mock_process` 并将结果封装为 `OxyResponse`。          |

## 继承

请参阅 [BaseLLM](./base_llm.md) 类了解继承的参数和方法。

## 用法

```python
# 默认模拟 -- 始终返回 "output"
oxy.MockLLM(name="mock_llm")

# 自定义模拟
async def my_mock(oxy_request):
    return "custom response"

oxy.MockLLM(name="mock_llm", func_mock_process=my_mock)
```
