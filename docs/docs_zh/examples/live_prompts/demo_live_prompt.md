# 使用共享 Prompt Key 的动态提示词

**源文件:** `examples/live_prompts/demo_live_prompt.py`

## 概述

本示例展示了多个代理如何通过共同的 `prompt_key` 共享同一个动态提示词，以及单个代理如何完全退出动态提示词系统。示例设置了三个 `ChatAgent` 实例来演示提示词键共享和 `use_live_prompt` 开关的使用。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包
- Elasticsearch 后端（或本地回退）用于动态提示词存储

## 运行方式

```bash
python -m examples.live_prompts.demo_live_prompt
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | `prompt_key` | `use_live_prompt` | 行为 |
|------|------|-------------|-------------------|------|
| `default_llm` | `HttpLLM` | 不适用 | 不适用 | 使用环境变量配置的 LLM |
| `chat_agent1` | `ChatAgent` | `"my_prompt"` | `True`（默认） | 使用以 `"my_prompt"` 为键的动态提示词 |
| `chat_agent2` | `ChatAgent` | `"my_prompt"` | `True`（默认） | 与 `chat_agent1` 共享同一个动态提示词 |
| `chat_agent3` | `ChatAgent` | 无 | `False` | 仅使用代码中的静态提示词 |

### 提示词键共享

`chat_agent1` 和 `chat_agent2` 都设置了 `prompt_key="my_prompt"`。这意味着：

- 它们在动态提示词存储（Elasticsearch）中共享同一个提示词条目。
- 当键 `"my_prompt"` 对应的提示词在运行时被更新时，**两个**代理会同时接收到更新后的提示词。
- 它们的初始代码级提示词（`"You are a helpful assistant."`）在尚未配置动态提示词时作为默认值使用。

### 退出动态提示词

`chat_agent3` 设置了 `use_live_prompt=False`：

- 无论动态提示词存储中发生任何更改，它始终使用其代码级提示词（`"You are a helpful assistant."`）。
- 它完全不参与动态提示词系统。

### 入口函数

```python
await mas.start_web_service(first_query="hello")
```

启动 Web 服务，初始查询为 "hello"。

## 核心概念

- **`prompt_key`** -- 一个共享标识符，将多个代理映射到动态提示词存储中的同一个提示词条目。具有相同 `prompt_key` 的代理将全部使用（并被同步更新）相同的提示词内容。
- **动态提示词系统** -- 由 Elasticsearch（或 `LocalEs` 回退）支持，动态提示词系统（`oxygent/live_prompt/`）允许运行时更新提示词。更改会传播到共享同一 `prompt_key` 的所有代理，无需重启服务。
- **`use_live_prompt=False`** -- 为特定代理禁用动态提示词系统。该代理的提示词固定为代码中定义的值。
- **`ChatAgent`** -- 一种维护聊天上下文的对话代理类型。与 `ReActAgent` 不同，它不遵循推理-行动循环，也不使用工具。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 初始查询 "hello" 被发送到系统。
3. `chat_agent1` 和 `chat_agent2` 都使用相同的提示词进行回复。如果通过提示词管理 API 更新了键 `"my_prompt"` 对应的动态提示词，两个代理在后续查询中都会反映该更改。
4. `chat_agent3` 始终使用其静态提示词 `"You are a helpful assistant."` 进行回复，不受任何运行时提示词更改的影响。
