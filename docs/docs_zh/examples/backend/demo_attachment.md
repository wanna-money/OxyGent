# 向聊天智能体发送附件

**源文件:** `examples/backend/demo_attachment.py`

## 概述

本示例演示如何在向支持多模态的聊天智能体发送查询时附带文件附件。示例展示了编程 API 调用方式（`mas.chat_with_agent`）和 Web 服务模式两种用法。当你需要让 LLM 分析或总结文档、图片或代码等文件内容时，此模式非常实用。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- LLM 端点必须支持多模态输入（示例中设置了 `is_multimodal_supported=True`）
- 工作目录中必须存在 `README.md` 文件（作为附件引用）

## 运行方式

```bash
python -m examples.backend.demo_attachment
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `is_multimodal_supported=True` -- 启用文件/图片附件处理 |
| `qa_agent` | `ChatAgent` | 关联多模态 LLM 的简单聊天智能体 |

### 入口函数

示例分两个阶段运行：

**阶段 1 -- 编程调用：**

```python
payload = {
    "query": "Introduce the content of the file",
    "attachments": ["README.md"],
}
oxy_response = await mas.chat_with_agent(payload=payload)
print("LLM: ", oxy_response.output)
```

payload 中的 `attachments` 字段接受文件路径列表。框架会读取文件内容并将其包含在 LLM 请求上下文中。

**阶段 2 -- Web 服务：**

```python
await mas.start_web_service(first_query="Introduce the content of the file")
```

启动 Web UI，用户可以在其中交互式地发送带有附件的查询。

## 核心概念

- **多模态 LLM 支持**：在 `HttpLLM` 上设置 `is_multimodal_supported=True` 可使模型在处理文本查询的同时处理文件附件。
- **payload 中的附件**：payload 字典中的 `attachments` 键接受文件路径列表，这些文件将被打包到 LLM 上下文中。
- **ChatAgent**：基础对话智能体，将用户查询（及任何附件）转发给 LLM 并返回响应。

## 预期行为

1. 智能体读取 `README.md` 文件，并将其内容与查询一起发送给 LLM。
2. LLM 返回文件内容的摘要或介绍，并打印到控制台。
3. Web 服务启动并自动发送相同的初始查询，在浏览器中显示结果。
