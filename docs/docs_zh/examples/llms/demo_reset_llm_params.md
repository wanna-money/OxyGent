# 重置 LLM 参数示例

**源文件:** `examples/llms/demo_reset_llm_params.py`

## 概述

本示例演示如何重置全局 LLM 默认参数，并在单个 LLM 实例上覆盖自定义值。当集成的模型（如 GPT-5 或其他新模型）对默认参数有不同要求时，这一功能非常有用。示例中清除了全局 LLM 配置，并设置了禁用思考模式和流式输出等特定参数。

## 前置条件

- 环境变量（在 `.env` 或终端中设置）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥
  - `DEFAULT_LLM_BASE_URL` -- LLM API 的基础 URL
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符
- Python 3.10+ 且已安装项目依赖

## 运行方式

```bash
python -m examples.llms.demo_reset_llm_params
```

## 代码详解

### 配置

```python
Config.set_llm_config({})
```

此行将全局 LLM 默认参数重置为空字典。默认情况下，OxyGent 的 `Config` 可能包含 `temperature`、`top_p`、`stream` 等参数。清除它们可确保不会向可能不支持这些参数的模型发送意外的默认值。

```python
oxy.HttpLLM(
    name="default_llm",
    ...,
    llm_params={"thinking": False, "stream": False},
)
```

清除全局配置后，在实例级别显式设置 `llm_params`。此处禁用了 `thinking`（扩展思考/思维链模式）并关闭了流式输出。

### 组件（`oxy_space`）

仅包含一个组件：

1. **`HttpLLM("default_llm")`** -- 带有自定义参数且已清除全局默认值的 HTTP LLM。

注意本示例未定义任何智能体，直接调用 LLM。

### 入口点

`main()` 协程创建 MAS，然后通过 `mas.call()` 直接调用 LLM：

```python
await mas.call(
    callee="default_llm",
    arguments={"messages": [{"role": "user", "content": "hello"}]},
)
```

这完全绕过了智能体层，直接向 LLM 发送原始消息列表，表明 OxyGent 中的 LLM 是可独立调用的 Oxy 组件。

## 核心概念

- **`Config.set_llm_config({})`** -- 将全局 LLM 配置重置为空状态。当框架的默认参数与特定模型的 API 要求冲突时非常有用。
- **`llm_params`** -- 传递给 LLM API 的模型特定参数字典。这些参数会与全局配置合并（并覆盖之）。常见参数包括 `temperature`、`top_p`、`stream`、`thinking`、`max_tokens` 等。
- **`mas.call()`** -- 直接调用任何指定名称的 Oxy 组件（LLM、工具或智能体），不经过智能体的推理循环。`callee` 参数指定组件名称，`arguments` 包含调用负载。
- **LLM 作为 Oxy 组件** -- 在 OxyGent 中，LLM 是一等公民 Oxy 对象，可以直接调用，不仅限于通过智能体使用。这使得测试、调试和脚本化工作流成为可能。

## 预期行为

1. 全局 LLM 配置被清除。
2. MAS 以单个 `HttpLLM` 初始化。
3. LLM 以 `thinking=False` 和 `stream=False` 参数接收消息 `"hello"`。
4. 响应直接返回（非流式），由框架打印或记录。
