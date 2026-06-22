# 禁用系统提示词示例

**源文件:** `examples/llms/demo_disable_system_prompt.py`

## 概述

本示例展示如何在使用不支持 `system` 角色消息格式的 LLM 时禁用系统提示词。部分模型（尤其是某些专有或微调模型）会拒绝或忽略系统提示词。`HttpLLM` 上的 `is_disable_system_prompt` 标志会在发送请求前移除系统消息，以兼容此类模型。

## 前置条件

- 环境变量（在 `.env` 或终端中设置）：
  - `CHATRHINO_750B_API_KEY` -- ChatRhino 750B 模型的 API 密钥
  - `CHATRHINO_750B_BASE_URL` -- ChatRhino API 的基础 URL
  - `CHATRHINO_750B_MODEL_NAME` -- ChatRhino 750B 的模型名称
- Python 3.10+ 且已安装项目依赖

**注意:** 本示例使用特定模型的环境变量（`CHATRHINO_750B_*`）而非默认的 `DEFAULT_LLM_*` 变量，因为它针对的是不支持系统提示词的特定模型。

## 运行方式

```bash
python -m examples.llms.demo_disable_system_prompt
```

## 代码详解

### 配置

```python
oxy.HttpLLM(
    name="default_llm",
    api_key=os.getenv("CHATRHINO_750B_API_KEY"),
    base_url=os.getenv("CHATRHINO_750B_BASE_URL"),
    model_name=os.getenv("CHATRHINO_750B_MODEL_NAME"),
    is_disable_system_prompt=True,
)
```

关键参数是 `is_disable_system_prompt=True`。启用后，框架会在发送到 LLM API 之前自动移除对话中所有 system 角色的消息，确保与不支持系统提示词的模型兼容。

### 组件（`oxy_space`）

1. **`HttpLLM("default_llm")`** -- 禁用了系统提示词的 HTTP LLM。
2. **`ChatAgent("master_agent")`** -- 使用默认 LLM 的简单聊天智能体。与 `ReActAgent` 不同，`ChatAgent` 不执行工具调用——它只是将消息传递给 LLM 并返回响应。

### 入口点

`main()` 协程创建 MAS 并以初始查询 `"hello"` 启动 Web 服务。智能体将在不发送系统提示词的情况下进行对话式回复。

## 核心概念

- **`is_disable_system_prompt`** -- `HttpLLM` 上的布尔标志，在 API 调用前移除 system 角色消息。对于收到系统提示词后返回错误或输出质量下降的模型而言，此选项至关重要。
- **ChatAgent** -- OxyGent 中最简单的智能体类型。它将用户消息转发给 LLM 并返回响应，不涉及推理循环或工具调用。
- **模型兼容性** -- 不同的 LLM 服务商支持不同的消息格式。OxyGent 提供 `is_disable_system_prompt` 等标志来适配这些差异，无需更改智能体逻辑。

## 预期行为

1. Web 服务器在 `http://127.0.0.1:8080` 启动。
2. 智能体收到查询"hello"。
3. LLM 接收到不包含系统提示词的对话消息。
4. 模型生成对话式响应，显示在 Web UI 中。
