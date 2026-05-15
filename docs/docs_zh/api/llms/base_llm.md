# BaseLLM
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

`BaseLLM` 是 OxyGent 系统中所有大语言模型实现的抽象基类。它提供了通用功能，包括多模态输入处理、思考消息的提取与转发、媒体 URL 的 Base64 转换、Token 用量跟踪以及带有用户友好提示的错误处理。

## 参数

| 参数                       | 类型 / 允许值          | 默认值                                                               | 描述                                                   |
| -------------------------- | ---------------------- | -------------------------------------------------------------------- | ------------------------------------------------------ |
| `category`                 | `str`                  | `"llm"`                                                              | 标识该对象为 LLM 的类别标志。                            |
| `semaphore`                | `int`                  | `Config.get_llm_semaphore()`                                         | 并行 LLM 调用的并发限制。                                |
| `timeout`                  | `float`                | `Config.get_llm_timeout()`                                           | 最大执行时间（秒）。                                     |
| `llm_params`               | `dict`                 | `{}`                                                                 | 额外的供应商特定 LLM 参数。                              |
| `is_send_think`            | `bool`                 | `Config.get_message_is_send_think()`                                 | 是否将思考消息发送到前端。                                |
| `friendly_error_text`      | `Optional[str]`        | `"Sorry, I seem to have encountered a problem. Please try again."`   | 发生异常时显示的用户友好错误消息。                        |
| `is_multimodal_supported`  | `bool`                 | `False`                                                              | 是否支持多模态输入。                                     |
| `is_convert_url_to_base64` | `bool`                 | `False`                                                              | 是否将图片/视频 URL 转换为 Base64 格式。                  |
| `max_image_pixels`         | `int`                  | `10000000`                                                           | 每张图片允许的最大像素数。                                |
| `max_video_size`           | `int`                  | `12582912`（12 MB）                                                   | 视频文件的最大大小（字节）。                              |
| `max_file_size_bytes`      | `int`                  | `2097152`（2 MB）                                                     | 非媒体文件用于 Base64 嵌入的最大大小。                    |
| `base64_image_prefix`      | `str`                  | `"data:image"`                                                       | 用于检测 Base64 编码图片数据 URI 的前缀。                 |
| `base64_video_prefix`      | `str`                  | `"data:video"`                                                       | 用于检测 Base64 编码视频数据 URI 的前缀。                 |
| `is_disable_system_prompt` | `bool`                 | `False`                                                              | 是否在 LLM 调用中省略系统提示词。                         |

## 方法

| 方法                                             | 协程 (async) | 返回值        | 用途（简述）                                                             |
| ------------------------------------------------ | ------------ | ------------- | ----------------------------------------------------------------------- |
| `_get_messages(oxy_request)`                     | 是           | `list`        | 预处理消息以支持多模态输入；如已启用则将 URL 转换为 Base64。               |
| `_execute(oxy_request)`                          | 是           | `OxyResponse` | **抽象方法** -- 必须由子类实现。                                          |
| `_post_send_message(oxy_response)`               | 是           | `None`        | 提取思考过程消息并转发到前端。                                            |
| `_after_execute(oxy_response)`                   | 是           | `OxyResponse` | 汇总 Token 用量并序列化为字典。                                          |
| `_build_payload(oxy_request, payload)`           | 否           | `dict`        | 将全局 LLM 配置、实例参数和请求参数合并到 payload 中。                    |
| `_build_token_usage(usage_data, messages, output)` | 否         | `TokenUsage`  | 构建 Token 用量，支持回退到估算值。                                       |

## 继承
 请参阅 [Oxy](../agent/base_oxy.md) 类了解继承的参数和方法。

## 用法

`BaseLLM` 类必须被继承使用。
