# LocalLLM

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

`LocalLLM` 从磁盘加载 HuggingFace Transformer 模型并在本地运行推理。它需要安装 `torch` 和 `transformers`。模型和分词器在 `init()` 阶段加载，并在后续请求中复用。

## 参数

| 参数         | 类型 / 允许值        | 默认值       | 描述                                                         |
| ------------ | -------------------- | ----------- | ------------------------------------------------------------ |
| `model_path` | `str`                | `""`        | HuggingFace 模型目录的路径。                                   |
| `device_map` | `str`                | `"auto"`    | 模型部署的设备映射策略。                                       |
| `dtype`      | `str`                | `"bfloat16"` | 模型权重的数据类型（例如 `"bfloat16"`、`"float16"`）。         |

## 方法

| 方法                    | 协程 (async) | 返回值        | 用途（简述）                                              |
| ----------------------- | ------------ | ------------- | -------------------------------------------------------- |
| `init()`                | 是           | `None`        | 从 `model_path` 加载模型和分词器。                         |
| `_execute(oxy_request)` | 是           | `OxyResponse` | 构建 payload、分词、生成文本并返回结果。                    |

## 继承

请参阅 [BaseLLM](./base_llm.md) 类了解继承的参数和方法。

## 用法

```python
oxy.LocalLLM(
    name="local_llm",
    model_path="/path/to/huggingface/model",
    device_map="auto",
    dtype="bfloat16",
)
```
