# RAG（检索增强生成）代理

**源文件:** `examples/agents/demo_rag_agent.py`

## 概述

本示例演示如何使用 OxyGent 的 `RAGAgent` 构建检索增强生成（RAG）代理。它使用自定义知识检索函数，在 LLM 生成答案之前将外部知识注入代理的提示词中。这种模式非常适合需要基于特定检索数据（如数据库、向量存储或 API）来生成回答的问答系统。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包

## 运行方式

```bash
python -m examples.agents.demo_rag_agent
```

## 代码详解

### 钩子函数

#### `func_retrieve_knowledge(oxy_request: OxyRequest) -> str`

通过 `func_retrieve_knowledge` 注册的异步检索函数。在 LLM 调用之前被调用以获取相关知识：

1. 通过 `oxy_request.get_query()` 提取用户查询。
2. 打印查询用于调试。
3. 返回硬编码字符串：`"Pi is 3.141592653589793238462643383279502."`。

在生产系统中，此函数会查询向量数据库、搜索引擎或知识库以检索上下文相关信息。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量 |
| `qa_agent` | `RAGAgent` | `llm_model="default_llm"`；带 `${knowledge}` 占位符的 `prompt`；`knowledge_placeholder="knowledge"`；`func_retrieve_knowledge=func_retrieve_knowledge` |

`RAGAgent` 的提示词包含模板变量 `${knowledge}`：

```
You are a helpful assistant! You can refer to the following knowledge to answer the questions:
${knowledge}
```

在运行时，`RAGAgent` 调用 `func_retrieve_knowledge`，返回的字符串会替换提示词中的 `${knowledge}` 占位符，然后发送给 LLM。

### 入口函数

```python
await mas.start_web_service(
    first_query="Please calculate the 20 positions of Pi",
)
```

启动 Web 服务，初始查询为圆周率相关问题。

## 核心概念

- **RAG 模式** -- 检索增强生成将知识检索与生成分离。检索函数提供上下文，LLM 基于该上下文生成响应。
- **`knowledge_placeholder`** -- 提示词中模板变量的名称（此处为 `"knowledge"`），将被检索到的内容替换。
- **`func_retrieve_knowledge`** -- 执行实际检索的异步函数。它接收完整的 `OxyRequest`，因此可以访问查询、记忆和其他上下文。
- **提示词模板化** -- 提示词中的 `${knowledge}` 语法在运行时被替换，允许动态上下文注入。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 初始查询 "Please calculate the 20 positions of Pi" 被发送。
3. `RAGAgent` 调用 `func_retrieve_knowledge`，返回硬编码的圆周率值。
4. 提示词组装完成，Pi 知识被注入到 `${knowledge}` 占位符中。
5. LLM 参考检索到的圆周率数字生成答案。
6. 响应显示在 Web UI 中，展示基于提供的知识得出的圆周率前 20 位小数。
