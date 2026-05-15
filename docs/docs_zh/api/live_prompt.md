# Live Prompt

---
模块所在位置:

```
oxygent/live_prompt/
├── manager.py      → PromptManager
├── optimizer.py    → PromptOptimizer
├── version.py      → VersionSyncCoordinator
└── wrapper.py      → DynamicAgentManager
```

---

## 简介

Live Prompt 系统提供基于 Elasticsearch（或 LocalEs 回退方案）的热更新提示词管理。它支持在不重启进程的情况下实时更新提示词，维护所有提示词变更的版本历史，并通过 ES 轮询支持多实例间的缓存同步。该系统还包含基于 LLM 的提示词优化器和自动化的 Agent 提示词热更新功能。

---

## PromptManager

`PromptManager`（`manager.py`）是核心类，提供提示词的增删改查操作、版本管理、缓存和全文搜索功能。

### 参数

| 参数              | 类型   | 默认值                         | 描述                                      |
| ---------------------- | ------ | ------------------------------- | ------------------------------------------------ |
| `index_name`           | `str`  | `"{app_name}_prompt"`           | 存储提示词的 ES 索引名称。               |
| `use_local_es`         | `bool` | `False`                         | 当前是否使用 LocalEs 作为后端。      |
| `db_client`            | -      | 自动检测 (JesEs 或 LocalEs)| 数据库客户端实例。                    |

### 方法

| 方法                                                          | 协程 (async) | 返回值          | 用途                                              |
| --------------------------------------------------------------- | ----------------- | --------------------- | -------------------------------------------------------------- |
| `save_prompt(prompt_key, prompt_content, ...)`                  | 是               | `bool`                | 保存或更新提示词，包含版本历史和乐观锁。 |
| `get_prompt(prompt_key, use_cache=True)`                        | 是               | `Optional[dict]`      | 按键获取提示词（优先使用缓存）。                        |
| `get_prompt_content(prompt_key, fallback_content, use_cache)`   | 是               | `str`                 | 获取提示词内容，支持回退值。                      |
| `get_prompt_history(prompt_key)`                                | 是               | `List[dict]`          | 获取按版本降序排列的提示词版本历史。       |
| `revert_to_version(prompt_key, target_version)`                 | 是               | `bool`                | 将提示词回退到历史中的指定版本。              |
| `list_prompts(category, agent_type, is_active, tags)`           | 是               | `List[dict]`          | 列出提示词，支持可选过滤条件。                          |
| `delete_prompt(prompt_key)`                                     | 是               | `bool`                | 从数据库和缓存中删除提示词。                       |
| `search_prompts(keyword, category)`                             | 是               | `List[dict]`          | 跨提示词字段进行全文搜索。                         |
| `clear_cache(prompt_key=None)`                                  | 是               | `None`                | 清除指定键或所有键的缓存。                      |
| `start_version_sync()`                                          | 是               | `None`                | 启动版本同步，确保多实例一致性。  |
| `stop_version_sync()`                                           | 是               | `None`                | 停止版本同步。                                  |
| `close()`                                                       | 是               | `None`                | 关闭数据库连接并停止版本同步。           |

### 模块级便捷函数

| 函数                                                | 协程 (async) | 返回值     | 用途                                    |
| ------------------------------------------------------- | ----------------- | ---------------- | ---------------------------------------------------- |
| `get_prompt_manager()`                                  | 是               | `PromptManager`  | 获取全局单例 `PromptManager` 实例。   |
| `close_prompt_manager()`                                | 是               | `None`           | 关闭全局管理器并清理资源。     |
| `get_dynamic_prompt(prompt_key, fallback, use_cache)`   | 是               | `str`            | 获取动态提示词内容，支持回退值。            |
| `resolve_prompt_from_es(prompt_key, default, use_cache)`| 是               | `str`            | 通过精确键从 ES 解析提示词。              |

---

## PromptOptimizer

`PromptOptimizer`（`optimizer.py`）提供基于 LLM 的提示词分析和改进功能，支持框架特定的约束验证。

### 参数

| 参数   | 类型  | 默认值       | 描述                                                |
| ----------- | ----- | ------------- | ---------------------------------------------------------- |
| `llm_model` | `str` | （自动检测） | 用于优化的 LLM 实例名称。                 |

### 方法

| 方法                                                          | 协程 (async) | 返回值   | 用途                                             |
| --------------------------------------------------------------- | ----------------- | -------------- | ------------------------------------------------------------- |
| `optimize(current_prompt, agent_type, strategy, requirements, context)` | 是     | `dict`         | 根据策略和约束优化提示词。          |
| `get_available_strategies()`                                    | 否                | `List[str]`    | 列出可用的优化策略。                       |
| `get_supported_agent_types()`                                   | 否                | `List[str]`    | 列出支持的 Agent 类型（react、general）。                  |

### 模块级函数

| 函数                                    | 返回值      | 用途                                   |
| ------------------------------------------- | ----------------- | ----------------------------------------- |
| `get_prompt_optimizer(llm_model, force_new)` | `PromptOptimizer` | 获取或创建单例优化器。    |

---

## VersionSyncCoordinator

`VersionSyncCoordinator`（`version.py`）通过 ES 轮询协调多实例间的缓存同步。

### 参数

| 参数          | 类型   | 默认值                     | 描述                                          |
| ------------------ | ------ | --------------------------- | ---------------------------------------------------- |
| `prompt_manager`   | -      | （必需）                  | 需要同步的 `PromptManager` 实例。         |
| `polling_interval` | `int`  | 来自配置或 `2`          | ES 轮询的时间间隔（秒）。                  |
| `use_es_polling`   | `bool` | 自动检测               | 是否启用 ES 轮询（仅限远程 ES）。      |

### 方法

| 方法                                | 协程 (async) | 返回值 | 用途                                          |
| ------------------------------------- | ----------------- | ------------ | ---------------------------------------------------------- |
| `start()`                             | 是               | `None`       | 启动同步协调器和 ES 轮询。                 |
| `stop()`                              | 是               | `None`       | 停止同步协调器。                                 |
| `update_local_version(prompt_key, version)` | 否          | `None`       | 保存后更新本地版本追踪器。                 |

---

## DynamicAgentManager

`DynamicAgentManager`（`wrapper.py`）管理 Agent 提示词从 Live Prompt 系统的热更新。

### 方法

| 方法                                    | 协程 (async) | 返回值      | 用途                                          |
| ----------------------------------------- | ----------------- | ----------------- | ---------------------------------------------------------- |
| `register_agents_from_mas(mas_instance)`  | 否                | `bool`            | 从 MAS 中自动注册使用 Live Prompt 的 Agent。       |
| `update_agent_prompt(agent_name)`         | 是               | `bool`            | 更新指定 Agent 的提示词。                        |
| `update_all_prompts()`                    | 是               | `Dict[str, bool]` | 更新所有已注册 Agent 的提示词。                  |
| `update_prompt_by_key(prompt_key)`        | 是               | `Dict[str, bool]` | 更新使用指定提示词键的所有 Agent。             |
| `get_agent_prompt_mapping()`              | 否                | `Dict[str, str]`  | 获取 Agent 到提示词键的映射。                       |

### 模块级便捷函数

| 函数                             | 协程 (async) | 返回值 | 用途                                 |
| ------------------------------------ | ----------------- | ------------ | ------------------------------------------------- |
| `setup_dynamic_agents(mas_instance)` | 是               | `None`       | 为 MAS Agent 设置动态提示词功能。|
| `hot_reload_prompt(prompt_key)`      | 是               | `bool`       | 按键热更新指定提示词。              |
| `hot_reload_all_prompts()`           | 是               | `bool`       | 热更新所有提示词。                           |
| `hot_reload_agent(agent_name)`       | 是               | `bool`       | 热更新指定 Agent 的提示词。           |
