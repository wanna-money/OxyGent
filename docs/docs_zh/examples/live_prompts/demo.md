# 动态提示词模式：静态 vs 动态提示词

**源文件:** `examples/live_prompts/demo.py`

## 概述

本示例展示了 OxyGent 代理可用的三种提示词模式：系统默认提示词、代码中定义的静态提示词，以及可在运行时热更新的动态（live）提示词。示例构建了一个多代理系统，由主代理协调时间、文件和数学三个子代理，每个子代理配置了不同的提示词策略。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包
- Elasticsearch 后端（或本地回退）用于 `use_live_prompt=True` 时的动态提示词存储

## 运行方式

```bash
python -m examples.live_prompts.demo
```

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
```

设置全局默认 LLM 模型名称，未显式指定 `llm_model` 参数的代理将使用 `"default_llm"`。

### 组件 (`oxy_space`)

| 组件 | 类型 | 提示词模式 | 关键参数 |
|------|------|-----------|----------|
| `default_llm` | `HttpLLM` | 不适用 | `api_key`、`base_url`、`model_name` 来自环境变量 |
| `time_tools` | 预设工具 | 不适用 | `oxygent.preset_tools` 中的内置时间查询工具 |
| `time_agent` | `ReActAgent` | 静态（`use_live_prompt=False`） | `prompt="You are a time management assistant..."`，`tools=["time_tools"]` |
| `file_tools` | 预设工具 | 不适用 | `oxygent.preset_tools` 中的内置文件操作工具 |
| `file_agent` | `ReActAgent` | 静态（`use_live_prompt=False`） | `prompt="You are a file system assistant..."`，`tools=["file_tools"]` |
| `math_tools` | 预设工具 | 不适用 | `oxygent.preset_tools` 中的内置数学工具 |
| `math_agent` | `ReActAgent` | 动态（默认） | `prompt="You are a math assistant..."`，`tools=["math_tools"]` |
| `master_agent` | `ReActAgent` | 动态（默认） | `is_master=True`，`sub_agents=["time_agent", "file_agent", "math_agent"]` |

### 提示词模式详解

1. **`time_agent`** -- 设置了 `use_live_prompt=False` 并指定了 `prompt` 值。由于禁用了动态提示词，代理使用代码中定义的 `prompt` 字符串。如果 `prompt` 为空，则会回退到系统默认提示词。

2. **`file_agent`** -- 同样设置了 `use_live_prompt=False` 并指定了 `prompt` 值。行为相同：直接使用代码级别的 `prompt`，不应用来自提示词存储的运行时更新。

3. **`math_agent`** -- 未设置 `use_live_prompt`（默认为 `True`）。代码级别的 `prompt` 作为初始值，但可在运行时通过基于 Elasticsearch 的动态提示词管理系统进行覆盖。

4. **`master_agent`** -- 同样默认使用动态提示词。其提示词可以在不重启服务的情况下进行热更新。

### 入口函数

```python
await mas.start_web_service(
    first_query="What time is it now? Please save it into time.txt."
)
```

启动 Web 服务并自动发送一个初始查询，该查询需要时间代理（获取当前时间）和文件代理（保存到文件）的协作完成。

## 核心概念

- **动态提示词（`use_live_prompt`）** -- 当设为 `True`（默认值）时，代理的提示词由动态提示词系统（`oxygent/live_prompt/`）管理。提示词可通过 ES 支持的提示词存储在运行时更新，无需重启应用。
- **静态提示词** -- 当 `use_live_prompt=False` 时，代理使用代码中定义的 `prompt` 参数。该提示词是确定性的，运行时不会改变。
- **系统默认提示词** -- 当 `use_live_prompt=False` 且 `prompt` 为空时，代理回退到框架内置的默认提示词。
- **预设工具（Preset Tools）** -- OxyGent 在 `oxygent/preset_tools/` 中提供了内置工具集合（`time_tools`、`file_tools`、`math_tools`），封装了常见操作。
- **主代理路由** -- 主代理（`is_master=True`）接收用户查询并根据任务类型委派给相应的子代理。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 首个查询 "What time is it now? Please save it into time.txt." 被自动发送。
3. 主代理将时间相关部分路由给 `time_agent`，后者使用预设时间工具查询当前时间。
4. 主代理随后将文件保存任务路由给 `file_agent`，后者使用预设文件工具将时间写入 `time.txt`。
5. `math_agent` 和 `master_agent` 启用了动态提示词 -- 其提示词可通过动态提示词管理系统在运行时更新。
6. `time_agent` 和 `file_agent` 禁用了动态提示词 -- 其提示词保持代码中定义的固定值。
