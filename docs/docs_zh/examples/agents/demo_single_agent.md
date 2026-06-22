# 单聊天代理与自定义钩子函数

**源文件:** `examples/agents/demo_single_agent.py`

## 概述

本示例展示了最简单的 OxyGent 配置：一个 `ChatAgent` 搭配一个 `HttpLLM`，并通过自定义输入处理和输出格式化钩子函数进行增强。这是理解 Oxy 生命周期以及如何在代理执行前后注入自定义逻辑的理想起点。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包

## 运行方式

```bash
python -m examples.agents.demo_single_agent
```

## 代码详解

### 配置

```python
Config.set_agent_short_memory_size(7)
```

将对话短期记忆窗口设置为 7 轮。该参数控制代理在调用 LLM 时保留多少轮最近的用户/助手消息对作为上下文。

### 钩子函数

#### `update_query(oxy_request: OxyRequest) -> OxyRequest`

通过 `func_process_input` 注册的**预处理**钩子。在代理处理之前，它会在每个传入的用户查询末尾追加 `" Please answer in detail."`。这演示了如何透明地修改用户输入。

#### `format_output(oxy_response: OxyResponse) -> OxyResponse`

通过 `func_format_output` 注册的**后处理**钩子。它在代理的输出字符串前添加 `"Answer: "` 前缀。这演示了如何统一格式化所有响应后再返回给用户。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量；`llm_params={"temperature": 0.01}`；`semaphore=4`（最大并发请求数 4）；`timeout=300`（5 分钟超时）；`retries=3` |
| `master_agent` | `ChatAgent` | `llm_model="default_llm"`；`prompt="You are a helpful assistant."`；`func_process_input=update_query`；`func_format_output=format_output` |

### 入口函数

`main()` 使用 `oxy_space` 列表创建 `MAS` 实例并启动 Web 服务：

```python
await mas.start_web_service(
    first_query="Hello",
    welcome_message="Hi, I'm OxyGent. How can I assist you?",
)
```

- `first_query="Hello"` -- 在 Web UI 加载时自动发送初始查询。
- `welcome_message` -- 在交互开始前显示在 Web UI 中的欢迎消息。

## 核心概念

- **`func_process_input`** -- 在 Oxy 生命周期的 `_format_input` 阶段调用的回调，允许在执行前修改 `OxyRequest`。
- **`func_format_output`** -- 在 `_format_output` 阶段调用的回调，允许在执行后修改 `OxyResponse`。
- **`semaphore`** -- 限制并发 LLM API 调用数量，防止触发速率限制或资源耗尽。
- **`short_memory_size`** -- 控制发送给 LLM 的对话历史滑动窗口大小。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 聊天 UI 中显示欢迎消息 "Hi, I'm OxyGent. How can I assist you?"。
3. 首个查询 "Hello" 被自动发送，但代理内部实际处理的是 "Hello Please answer in detail."（因为 `update_query` 钩子的作用）。
4. 代理的响应会被加上 "Answer: " 前缀（因为 `format_output` 钩子的作用）。
5. 后续用户消息同样会经过两个钩子函数处理。
