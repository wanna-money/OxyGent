# 从 JSON 文件加载配置

**源文件:** `examples/backend/demo_config.py`

## 概述

本示例演示如何使用 `Config.load_from_json()` 从 JSON 文件加载 OxyGent 配置。配置系统支持基于环境的配置文件分层 -- `"default"` 配置文件与环境特定的覆盖层（如 `"dev"`、`"prod"`）合并。此模式对于在开发、预发布和生产环境之间管理不同配置而无需更改代码至关重要。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- 工作目录中需要一个 `config.json` 文件（至少包含 `"default"` 配置）

## 运行方式

```bash
python -m examples.backend.demo_config
```

## 代码详解

### 配置

```python
Config.load_from_json("./config.json", env="default")
Config.set_agent_llm_model("default_llm")
```

- `Config.load_from_json("./config.json", env="default")`：从指定的 JSON 文件加载配置。`env` 参数选择使用哪个配置文件。系统将 `"default"` 配置与指定的环境配置合并。部署时，可以设置 `APP_ENV` 环境变量来自动切换配置文件。
- `Config.set_agent_llm_model("default_llm")`：为所有智能体全局设置默认 LLM 模型名称，使各个智能体无需单独指定 `llm_model`。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | 从环境变量获取的标准 LLM 凭证 |
| `master_agent` | `ReActAgent` | 未显式指定 `llm_model` -- 使用全局配置的默认值 |

注意 `master_agent` 未指定 `llm_model`，因为已通过 `Config.set_agent_llm_model()` 全局设置。

### 入口函数

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="hello")
```

## 核心概念

- **Config.load_from_json()**：从 JSON 文件加载配置，支持基于环境的配置文件分层。JSON 文件应包含 `"default"` 键和可选的环境键（如 `"dev"`、`"prod"`）。
- **环境配置文件**：配置系统将 `"default"` 设置与所选环境的设置合并。环境配置中的值会覆盖 `"default"` 中的值。
- **APP_ENV**：设置此环境变量后，会自动选择要使用的配置文件。
- **${VAR} 替换**：配置系统支持在配置值中使用 `${VAR_NAME}` 语法进行环境变量替换。
- **Config.set_agent_llm_model()**：便捷方法，为所有智能体全局设置默认 LLM 模型名称。

## 预期行为

1. 从 `./config.json` 加载 `"default"` 配置文件中的配置。
2. 默认 LLM 模型全局设置为 `"default_llm"`。
3. `ReActAgent` 创建时未显式指定 `llm_model`，使用全局默认值。
4. Web 服务启动，使用配置的 LLM 处理初始查询 `"hello"`。
