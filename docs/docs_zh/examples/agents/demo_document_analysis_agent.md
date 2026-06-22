# 文档分析代理

**源文件:** `examples/agents/demo_document_analysis_agent.py`

## 概述

本示例展示了一个配备预置文档处理工具的 `ReActAgent`，用于分析各种文档格式（PDF、Word、Excel 等）。它将流式 LLM 输出与 OxyGent 内置的 `preset_tools.document_tools` 相结合，提供开箱即用的文档分析能力。这种模式适用于需要解析、提取和推理结构化文档内容的代理。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包
- 根据文档类型可能需要额外的文档处理库（如 `pypdf`、`python-docx`、`openpyxl`）

## 运行方式

```bash
python -m examples.agents.demo_document_analysis_agent
```

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
```

为所有代理设置全局默认 LLM 模型，因此 `document_agent` 无需显式指定 `llm_model`。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量；`llm_params={"stream": True}` |
| `document_tools` | `preset_tools.document_tools` | OxyGent 内置的文档处理 FunctionHub（支持 PDF、Word、Excel 等） |
| `document_agent` | `ReActAgent` | `desc="A tool that can process and analyze documents (PDF, Word, Excel, etc.)"`；`tools=["document_tools"]` |

`preset_tools.document_tools` 是一个预构建的 `FunctionHub`，提供文档读取和解析函数。它直接包含在 `oxy_space` 列表中，无需手动配置。

### 入口函数

```python
await mas.start_web_service(first_query="hello")
```

启动 Web 服务，初始查询为简单的问候语。用户随后可以上传或引用文档进行分析。

## 核心概念

- **`preset_tools`** -- OxyGent 提供了一组内置的工具集合（FunctionHub 实例），可直接使用。`preset_tools.document_tools` 包含用于读取和解析各种文档格式的函数。
- **配备工具的 ReActAgent** -- 代理使用 ReAct 模式，根据用户查询决定何时以及如何使用文档工具。
- **流式输出 + 工具调用** -- 将 `stream: True` 与工具调用代理结合，在利用工具能力的同时提供响应式输出。
- **`Config.set_agent_llm_model()`** -- 消除了对每个代理单独设置 `llm_model` 的需要。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 初始查询 "hello" 触发一般性的问候响应。
3. 当用户提供文档相关查询时（例如 "读取并总结这个 PDF" 加上文件路径），代理使用文档工具解析文件并生成分析。
4. 由于设置了 `stream: True`，LLM 响应逐 token 流式传输到 Web UI。
5. 代理可以处理多种文档类型，包括 PDF、Word (.docx) 和 Excel (.xlsx) 文件。
