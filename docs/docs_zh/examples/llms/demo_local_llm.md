# 本地 LLM 示例

**源文件:** `examples/llms/demo_local_llm.py`

## 概述

本示例演示如何通过 `LocalLLM` 类在 OxyGent 中使用本地部署的语言模型。`LocalLLM` 从本地文件路径（如 Hugging Face 模型目录）加载模型，而非连接远程 API。适用于离线部署、数据隐私敏感的应用场景或使用自定义微调模型。

## 前置条件

- 在 `model_path` 指定的路径下存在本地模型目录（如 Hugging Face Transformers 兼容的模型）
- 已安装相应的模型加载依赖（如 `transformers`、`torch`）
- Python 3.10+ 且已安装项目依赖
- 足够的系统资源（GPU/内存）用于模型推理

**注意:** 由于模型在本地运行，不需要 API 密钥或环境变量。

## 运行方式

运行前，请将源代码中的 `model_path` 修改为您实际的本地模型目录路径：

```python
oxy.LocalLLM(
    name="default_llm",
    model_path="/path/to/your_model",  # <-- 修改此处
)
```

然后运行：

```bash
python -m examples.llms.demo_local_llm
```

## 代码详解

### 配置

```python
oxy.LocalLLM(
    name="default_llm",
    model_path="/path/to/your_model",
)
```

`LocalLLM` 接收一个 `model_path` 参数，指向本地模型目录。框架内部处理模型加载和推理。无需 API 密钥或基础 URL。

### 组件（`oxy_space`）

1. **`LocalLLM("default_llm")`** -- 本地加载的语言模型。
2. **`ChatAgent("master_agent")`** -- 使用本地 LLM 生成响应的聊天智能体。智能体通过名称 `"default_llm"` 引用该 LLM。

### 入口点

`main()` 协程创建 MAS 并以初始查询 `"hello"` 启动 Web 服务。聊天智能体使用本地加载的模型处理查询。

## 核心概念

- **LocalLLM** -- 在本地加载和运行模型的 LLM 实现，而非调用远程 API。支持 Hugging Face Transformers 兼容的模型目录。
- **离线运行** -- 由于模型在本地运行，模型文件下载完成后不再需要网络连接或 API 密钥。
- **资源要求** -- 本地模型需要大量系统资源。请确保您所选模型有足够的 GPU 显存（GPU 推理）或内存（CPU 推理）。
- **模型路径** -- 路径应指向包含模型权重、分词器配置和其他必要文件的目录（如标准的 Hugging Face 模型目录）。

## 预期行为

1. 框架从指定的本地路径加载模型（根据模型大小可能需要一些时间）。
2. Web 服务器在 `http://127.0.0.1:8080` 启动。
3. 智能体收到查询"hello"。
4. 本地模型生成响应，显示在 Web UI 中。
5. 后续查询完全在本地处理，不涉及任何外部 API 调用。
