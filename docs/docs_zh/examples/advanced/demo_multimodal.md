# 多模态 Agent

**源文件:** `examples/advanced/demo_multimodal.py`

## 概述

本示例演示了如何配置视觉语言模型(VLM)以支持多模态输入,使 ChatAgent 能够同时处理文本和图像输入。示例展示了两种使用方式:通过 Web 服务让用户在 UI 上传图片,以及通过编程方式直接构造多模态消息。

## 前置条件

- VLM 环境变量: `DEFAULT_VLM_API_KEY`、`DEFAULT_VLM_BASE_URL`、`DEFAULT_VLM_MODEL_NAME`
- VLM 端点必须支持多模态(图像 + 文本)输入
- 若使用 `test()` 函数:工作目录下需要一个名为 `test_pic.png` 的文件

## 运行方式

```bash
python -m examples.advanced.demo_multimodal
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_vlm` | `HttpLLM` | `api_key`、`base_url`、`model_name`(来自 VLM 环境变量);`is_multimodal_supported=True`、`is_convert_url_to_base64=True`、`base64_image_prefix="data:image/jpeg"` |
| `vision_agent` | `ChatAgent` | `llm_model="default_vlm"` |

**VLM 配置详解:**

- `is_multimodal_supported=True` -- 启用框架的图像内容处理能力。
- `is_convert_url_to_base64=True` -- 将图像 URL(包括本地文件路径)转换为 base64 编码数据。
- `base64_image_prefix="data:image/jpeg"` -- 设置 base64 编码图像的 MIME 类型前缀,部分模型 API 需要此配置。

### 入口函数(Web 模式)

`main()` 创建 `MAS` 上下文并以 `first_query="What is this?"` 启动 Web 服务。用户通过 Web UI 上传图片,视觉 Agent 对其进行分析。

### 测试函数(编程模式)

`test()` 演示了如何通过编程方式构造多模态消息:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": "./test_pic.png"}},
        {"type": "text", "text": "What is this?"},
    ]},
]
await mas.call(callee="default_vlm", arguments={"messages": messages})
```

这会直接调用 VLM(而非通过 Agent),传入一个包含图像和文本提示的结构化多模态消息。

## 核心概念

- **多模态 LLM 配置** -- 三个标志(`is_multimodal_supported`、`is_convert_url_to_base64`、`base64_image_prefix`)协同工作,在 LLM 中启用图像理解能力。
- **ChatAgent** -- 一种简单的 Agent,直接将对话转发给 LLM,不涉及工具调用或 ReAct 推理,适合简单的问答或图像理解场景。
- **直接 LLM 调用** -- `mas.call(callee="default_vlm", ...)` 可以直接调用 LLM 组件,绕过 Agent 层,适用于需要低级别消息格式控制的场景。

## 预期行为

1. Web 服务在 `127.0.0.1:8080` 启动。
2. 用户通过 Web UI 上传图片。
3. 视觉 Agent 将图片和问题 "What is this?" 传递给 VLM。
4. VLM 分析图片并返回文本描述。
