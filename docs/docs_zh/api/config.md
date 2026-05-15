# Config
---
类所在位置:

```
oxygent/config.py
```

---

## 简介

`Config` 是 OxyGent 框架的集中式配置管理类。它提供了一套分层配置体系，支持按环境区分设置、加载 JSON 文件以及环境变量替换。该类管理所有配置方面，包括应用设置、日志、LLM 参数、数据库连接、服务器设置等。

## 参数

| 参数 | 类型 / 允许值 | 默认值 | 描述 |
| --------- | -------------------- | ------- | ----------- |
| `_env` | `str` | `"default"` | 当前环境名称 |
| `_config` | `dict` | `{}` | 包含所有设置的主配置字典 |

## 配置模块

| 模块 | 描述 |
| ------ | ----------- |
| `app` | 应用名称和版本设置 |
| `env` | 环境文件路径和覆盖设置 |
| `log` | 日志配置，包括级别、颜色和输出设置 |
| `llm` | 大语言模型配置 |
| `cache` | 缓存目录设置 |
| `message` | 消息处理和存储配置 |
| `vearch` | 向量搜索数据库配置 |
| `es` | Elasticsearch 配置 |
| `redis` | Redis 配置 |
| `schema` | 数据模式配置 |
| `server` | Web 服务器配置 |
| `agent` | Agent 相关配置 |

## 方法

| 方法 | 协程 (async) | 返回值 | 用途 |
| ------ | ----------------- | ------------ | ------- |
| `load_from_json()` | 否 | `None` | 类方法，从 JSON 文件加载配置 |
| `set_module_config()` | 否 | `None` | 设置指定模块的配置 |
| `get_module_config()` | 否 | `Any` | 获取指定模块的配置 |
| `set_app_config()` | 否 | `None` | 设置应用配置 |
| `get_app_config()` | 否 | `dict` | 获取应用配置 |
| `set_app_name()` | 否 | `None` | 设置应用名称 |
| `get_app_name()` | 否 | `str` | 获取应用名称 |
| `set_app_version()` | 否 | `None` | 设置应用版本 |
| `get_app_version()` | 否 | `str` | 获取应用版本 |
| `set_env_config()` | 否 | `None` | 设置环境配置 |
| `get_env_config()` | 否 | `dict` | 获取环境配置 |
| `set_env_path()` | 否 | `None` | 设置环境文件路径 |
| `get_env_path()` | 否 | `str` | 获取环境文件路径 |
| `set_env_is_override()` | 否 | `None` | 设置环境覆盖标志 |
| `get_env_is_override()` | 否 | `bool` | 获取环境覆盖标志 |
| `set_log_config()` | 否 | `None` | 设置日志配置 |
| `get_log_config()` | 否 | `dict` | 获取日志配置 |
| `set_log_path()` | 否 | `None` | 设置日志文件路径 |
| `get_log_path()` | 否 | `str` | 获取日志文件路径 |
| `set_log_level_root()` | 否 | `None` | 设置根日志级别 |
| `get_log_level_root()` | 否 | `str` | 获取根日志级别 |
| `set_log_level_terminal()` | 否 | `None` | 设置终端日志级别 |
| `get_log_level_terminal()` | 否 | `str` | 获取终端日志级别 |
| `set_log_level_file()` | 否 | `None` | 设置文件日志级别 |
| `get_log_level_file()` | 否 | `str` | 获取文件日志级别 |
| `set_log_color_is_on_background()` | 否 | `None` | 设置背景颜色标志 |
| `get_log_color_is_on_background()` | 否 | `bool` | 获取背景颜色标志 |
| `set_log_is_bright()` | 否 | `None` | 设置亮色标志 |
| `get_log_is_bright()` | 否 | `bool` | 获取亮色标志 |
| `set_log_only_message_color()` | 否 | `None` | 设置仅消息着色标志 |
| `get_log_only_message_color()` | 否 | `bool` | 获取仅消息着色标志 |
| `set_log_color_tool_call()` | 否 | `None` | 设置工具调用颜色 |
| `get_log_color_tool_call()` | 否 | `str` | 获取工具调用颜色 |
| `set_log_color_observation()` | 否 | `None` | 设置观测结果颜色 |
| `get_log_color_observation()` | 否 | `str` | 获取观测结果颜色 |
| `set_log_is_detailed_tool_call()` | 否 | `None` | 设置详细工具调用标志 |
| `get_log_is_detailed_tool_call()` | 否 | `bool` | 获取详细工具调用标志 |
| `set_log_is_detailed_observation()` | 否 | `None` | 设置详细观测结果标志 |
| `get_log_is_detailed_observation()` | 否 | `bool` | 获取详细观测结果标志 |
| `set_llm_config()` | 否 | `None` | 设置 LLM 配置 |
| `get_llm_config()` | 否 | `dict` | 获取 LLM 配置 |
| `set_cache_config()` | 否 | `None` | 设置缓存配置 |
| `get_cache_config()` | 否 | `dict` | 获取缓存配置 |
| `set_cache_save_dir()` | 否 | `None` | 设置缓存保存目录 |
| `get_cache_save_dir()` | 否 | `str` | 获取缓存保存目录 |
| `set_message_config()` | 否 | `None` | 设置消息配置 |
| `get_message_config()` | 否 | `dict` | 获取消息配置 |
| `set_message_is_send_tool_call()` | 否 | `None` | 设置发送工具调用标志 |
| `get_message_is_send_tool_call()` | 否 | `bool` | 获取发送工具调用标志 |
| `set_message_is_send_observation()` | 否 | `None` | 设置发送观测结果标志 |
| `get_message_is_send_observation()` | 否 | `bool` | 获取发送观测结果标志 |
| `set_message_is_send_think()` | 否 | `None` | 设置发送思考过程标志 |
| `get_message_is_send_think()` | 否 | `bool` | 获取发送思考过程标志 |
| `set_message_is_send_answer()` | 否 | `None` | 设置发送回答标志 |
| `get_message_is_send_answer()` | 否 | `bool` | 获取发送回答标志 |
| `set_message_is_stored()` | 否 | `None` | 设置消息存储标志 |
| `get_message_is_stored()` | 否 | `bool` | 获取消息存储标志 |
| `set_es_config()` | 否 | `None` | 设置 Elasticsearch 配置 |
| `get_es_config()` | 否 | `dict` | 获取 Elasticsearch 配置 |
| `set_vearch_config()` | 否 | `None` | 设置 Vearch 配置 |
| `get_vearch_config()` | 否 | `dict` | 获取 Vearch 配置 |
| `get_vearch_embedding_model_url()` | 否 | `str` | 获取 Vearch 嵌入模型 URL |
| `set_redis_config()` | 否 | `None` | 设置 Redis 配置 |
| `get_redis_config()` | 否 | `dict` | 获取 Redis 配置 |
| `set_server_config()` | 否 | `None` | 设置服务器配置 |
| `get_server_config()` | 否 | `dict` | 获取服务器配置 |
| `set_server_host()` | 否 | `None` | 设置服务器主机地址 |
| `get_server_host()` | 否 | `str` | 获取服务器主机地址 |
| `set_server_port()` | 否 | `None` | 设置服务器端口 |
| `get_server_port()` | 否 | `int` | 获取服务器端口 |
| `set_server_auto_open_webpage()` | 否 | `None` | 设置自动打开网页标志 |
| `get_server_auto_open_webpage()` | 否 | `bool` | 获取自动打开网页标志 |
| `set_server_on_latest_webpage()` | 否 | `None` | 设置使用最新网页标志 |
| `get_server_on_latest_webpage()` | 否 | `bool` | 获取使用最新网页标志 |
| `set_server_log_level()` | 否 | `None` | 设置服务器日志级别 |
| `get_server_log_level()` | 否 | `str` | 获取服务器日志级别 |
| `set_agent_config()` | 否 | `None` | 设置 Agent 配置 |
| `get_agent_config()` | 否 | `dict` | 获取 Agent 配置 |
| `set_agent_prompt()` | 否 | `None` | 设置 Agent 提示词 |
| `get_agent_prompt()` | 否 | `str` | 获取 Agent 提示词 |
| `set_agent_llm_model()` | 否 | `None` | 设置 Agent LLM 模型 |
| `get_agent_llm_model()` | 否 | `str` | 获取 Agent LLM 模型 |
| `set_agent_input_schema()` | 否 | `None` | 设置 Agent 输入模式 |
| `get_agent_input_schema()` | 否 | `dict` | 获取 Agent 输入模式 |
| `set_schema_config()` | 否 | `None` | 设置数据模式配置 |
| `get_schema_config()` | 否 | `dict` | 获取数据模式配置 |
| `get_shared_data_schema()` | 否 | `dict` | 获取共享数据模式 |

## 函数

| 函数 | 协程 (async) | 返回值 | 用途 |
| -------- | ----------------- | ------------ | ------- |
| `deep_update()` | 否 | `None` | 递归地用另一个字典更新目标字典 |
| `replace_env_var()` | 否 | `Any` | 替换配置值中的环境变量 |

## 用法

```python
from oxygent import Config

# 从 JSON 文件加载配置，支持环境分层
Config.load_from_json("config.json", env="prod")

# 编程式配置
Config.set_server_host("0.0.0.0")
Config.set_server_port(9090)
Config.set_server_auto_open_webpage(False)
Config.set_log_path("./logs/app.log")
Config.set_cache_save_dir("./cache")
Config.set_agent_llm_model("my_llm")
```
