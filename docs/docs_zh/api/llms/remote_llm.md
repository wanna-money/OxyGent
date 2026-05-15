# RemoteLLM
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

`RemoteLLM` 扩展了 `BaseLLM`，用于与远程大语言模型 API 进行通信。它提供了连接远程 LLM 服务的标准化接口，处理 API 认证、请求格式化以及兼容 OpenAI API 标准的响应解析。

## 参数


| 参数         | 类型 / 允许值                                              | 默认值         | 描述                                                             |
| ------------ | ---------------------------------------------------------- | ------------- | ---------------------------------------------------------------- |
| `api_key`    | `Optional[str]`                                            | `None`        | 用于远程 LLM 服务认证的 API 密钥。                                |
| `base_url`   | `Optional[str]`                                            | `""`          | 远程 LLM API 的基础 URL 端点（必填）。                            |
| `model_name` | `Optional[str]`                                            | `""`          | 用于请求的模型标识符（必填）。                                     |
| `headers`    | `Dict[str, str] \| Callable[[OxyRequest], Dict[str, str]]` | `lambda: {}`  | 额外的 HTTP 请求头，或按请求返回请求头的可调用对象。                |

## 方法


| 方法                    | 协程 (async) | 返回值        | 用途（简述）                                                       |
| ----------------------- | ------------ | ------------- | ----------------------------------------------------------------- |
| `_execute(oxy_request)` | 是           | `OxyResponse` | **抽象方法** -- 子类实现实际的远程 API 调用。                        |

## 继承
 请参阅 [BaseLLM](./base_llm.md) 类了解继承的参数和方法。

## 用法

`RemoteLLM` 类必须被继承使用。
