# 多模态跨 Agent 传递

**源文件:** `examples/advanced/demo_multimodal_transfer.py`

## 概述

本示例演示了如何在多 Agent 系统中将视觉语言模型(VLM)Agent 与图像生成工具相结合。主 Agent 可以将图像理解任务委派给视觉 Agent,将图像创建任务委派给图像生成工具,从而构建一个从图像分析到图像生成的完整工作流。

## 前置条件

- 环境变量: `DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- VLM 环境变量: `DEFAULT_VLM_API_KEY`、`DEFAULT_VLM_BASE_URL`、`DEFAULT_VLM_MODEL_NAME`
- VLM 端点必须支持多模态(图像 + 文本)输入

## 运行方式

```bash
python -m examples.advanced.demo_multimodal_transfer
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_vlm` | `HttpLLM` | `api_key`、`base_url`、`model_name`(来自 VLM 环境变量);`is_multimodal_supported=True`、`is_convert_url_to_base64=True` |
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name`(来自标准 LLM 环境变量) |
| `image_gen_tools` | `preset_tools.image_gen_tools` | 内置预设图像生成工具集 |
| `vision_agent` | `ChatAgent` | `desc="一个图片理解工具"`、`llm_model="default_vlm"` |
| `master_agent` | `ReActAgent` | `is_master=True`、`sub_agents=["vision_agent"]`、`tools=["image_gen_tools"]`、`llm_model="default_llm"` |

**VLM 配置说明:**

- `is_multimodal_supported=True` -- 告知框架该 LLM 可以同时接受图像和文本输入。
- `is_convert_url_to_base64=True` -- 在发送给模型之前,自动将图像 URL 转换为 base64 编码数据。

### 入口函数

`main()` 创建 `MAS` 上下文并以 `first_query="这是什么，生成一张卡通的"` 启动 Web 服务。用户需要通过 Web UI 上传一张图片。主 Agent 会将图像理解任务委派给 `vision_agent`,然后使用 `image_gen_tools` 生成对应的卡通版本。

## 核心概念

- **多模态 LLM** -- 配置了 `is_multimodal_supported=True` 的 LLM,能够同时处理文本和图像输入。
- **Base64 转换** -- `is_convert_url_to_base64=True` 自动将图像 URL 转换为内联 base64 数据,适配需要此格式的模型。
- **Agent 协作** -- 主 Agent(纯文本 LLM)在视觉子 Agent(VLM)和图像生成工具之间进行编排,形成从图像理解到图像创建的流水线。
- **preset_tools.image_gen_tools** -- 内置的 FunctionHub,提供图像生成能力。

## 预期行为

1. Web 服务在 `127.0.0.1:8080` 启动。
2. 用户通过 Web UI 上传一张图片。
3. 主 Agent 将图像委派给 `vision_agent` 进行内容理解。
4. 主 Agent 根据描述使用 `image_gen_tools` 生成卡通版本。
5. 生成的卡通图片返回给用户。
