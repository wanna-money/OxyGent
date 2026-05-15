# Live Prompt

---
The position of the modules is:

```
oxygent/live_prompt/
├── manager.py      → PromptManager
├── optimizer.py    → PromptOptimizer
├── version.py      → VersionSyncCoordinator
└── wrapper.py      → DynamicAgentManager
```

---

## Introduction

The Live Prompt system provides hot-reloadable prompt management backed by Elasticsearch (or LocalEs fallback). It allows runtime prompt updates without process restart, maintains version history for all prompt changes, and supports multi-instance cache synchronization via ES polling. The system also includes an LLM-based prompt optimizer and automatic agent prompt hot-reload.

---

## PromptManager

`PromptManager` (`manager.py`) is the core class providing prompt CRUD operations, versioning, caching, and full-text search.

### Parameters

| Parameter              | Type   | Default                         | Description                                      |
| ---------------------- | ------ | ------------------------------- | ------------------------------------------------ |
| `index_name`           | `str`  | `"{app_name}_prompt"`           | ES index name for storing prompts.               |
| `use_local_es`         | `bool` | `False`                         | Whether currently using LocalEs as backend.      |
| `db_client`            | -      | auto-detected (JesEs or LocalEs)| The database client instance.                    |

### Methods

| Method                                                          | Coroutine (async) | Return Value          | Purpose (concise)                                              |
| --------------------------------------------------------------- | ----------------- | --------------------- | -------------------------------------------------------------- |
| `save_prompt(prompt_key, prompt_content, ...)`                  | Yes               | `bool`                | Save or update a prompt with version history and optimistic locking. |
| `get_prompt(prompt_key, use_cache=True)`                        | Yes               | `Optional[dict]`      | Retrieve a prompt by key (cache-first).                        |
| `get_prompt_content(prompt_key, fallback_content, use_cache)`   | Yes               | `str`                 | Get prompt content with fallback support.                      |
| `get_prompt_history(prompt_key)`                                | Yes               | `List[dict]`          | Get prompt version history sorted by version descending.       |
| `revert_to_version(prompt_key, target_version)`                 | Yes               | `bool`                | Revert prompt to a specific version from history.              |
| `list_prompts(category, agent_type, is_active, tags)`           | Yes               | `List[dict]`          | List prompts with optional filtering.                          |
| `delete_prompt(prompt_key)`                                     | Yes               | `bool`                | Delete a prompt from database and cache.                       |
| `search_prompts(keyword, category)`                             | Yes               | `List[dict]`          | Full-text search across prompt fields.                         |
| `clear_cache(prompt_key=None)`                                  | Yes               | `None`                | Clear cache for specific key or all keys.                      |
| `start_version_sync()`                                          | Yes               | `None`                | Start version synchronization for multi-instance consistency.  |
| `stop_version_sync()`                                           | Yes               | `None`                | Stop version synchronization.                                  |
| `close()`                                                       | Yes               | `None`                | Close the database connection and stop version sync.           |

### Module-level Convenience Functions

| Function                                                | Coroutine (async) | Return Value     | Purpose (concise)                                    |
| ------------------------------------------------------- | ----------------- | ---------------- | ---------------------------------------------------- |
| `get_prompt_manager()`                                  | Yes               | `PromptManager`  | Get the global singleton `PromptManager` instance.   |
| `close_prompt_manager()`                                | Yes               | `None`           | Close the global manager and clean up resources.     |
| `get_dynamic_prompt(prompt_key, fallback, use_cache)`   | Yes               | `str`            | Get dynamic prompt content with fallback.            |
| `resolve_prompt_from_es(prompt_key, default, use_cache)`| Yes               | `str`            | Resolve prompt from ES using exact key.              |

---

## PromptOptimizer

`PromptOptimizer` (`optimizer.py`) provides LLM-based prompt analysis and improvement with framework-specific constraint validation.

### Parameters

| Parameter   | Type  | Default       | Description                                                |
| ----------- | ----- | ------------- | ---------------------------------------------------------- |
| `llm_model` | `str` | (auto-detect) | LLM instance name to use for optimization.                 |

### Methods

| Method                                                          | Coroutine (async) | Return Value   | Purpose (concise)                                             |
| --------------------------------------------------------------- | ----------------- | -------------- | ------------------------------------------------------------- |
| `optimize(current_prompt, agent_type, strategy, requirements, context)` | Yes     | `dict`         | Optimize a prompt based on strategy and constraints.          |
| `get_available_strategies()`                                    | No                | `List[str]`    | List available optimization strategies.                       |
| `get_supported_agent_types()`                                   | No                | `List[str]`    | List supported agent types (react, general).                  |

### Module-level Function

| Function                                    | Return Value      | Purpose                                   |
| ------------------------------------------- | ----------------- | ----------------------------------------- |
| `get_prompt_optimizer(llm_model, force_new)` | `PromptOptimizer` | Get or create the singleton optimizer.    |

---

## VersionSyncCoordinator

`VersionSyncCoordinator` (`version.py`) coordinates cache synchronization across multiple instances using ES polling.

### Parameters

| Parameter          | Type   | Default                     | Description                                          |
| ------------------ | ------ | --------------------------- | ---------------------------------------------------- |
| `prompt_manager`   | -      | (required)                  | The `PromptManager` instance to synchronize.         |
| `polling_interval` | `int`  | from config or `2`          | Interval in seconds for ES polling.                  |
| `use_es_polling`   | `bool` | auto-detected               | Whether ES polling is enabled (remote ES only).      |

### Methods

| Method                                | Coroutine (async) | Return Value | Purpose (concise)                                          |
| ------------------------------------- | ----------------- | ------------ | ---------------------------------------------------------- |
| `start()`                             | Yes               | `None`       | Start the sync coordinator and ES polling.                 |
| `stop()`                              | Yes               | `None`       | Stop the sync coordinator.                                 |
| `update_local_version(prompt_key, version)` | No          | `None`       | Update local version tracker after saving.                 |

---

## DynamicAgentManager

`DynamicAgentManager` (`wrapper.py`) manages hot-reload of agent prompts from the Live Prompt system.

### Methods

| Method                                    | Coroutine (async) | Return Value      | Purpose (concise)                                          |
| ----------------------------------------- | ----------------- | ----------------- | ---------------------------------------------------------- |
| `register_agents_from_mas(mas_instance)`  | No                | `bool`            | Auto-register agents that use live prompts from MAS.       |
| `update_agent_prompt(agent_name)`         | Yes               | `bool`            | Update prompt for a specific agent.                        |
| `update_all_prompts()`                    | Yes               | `Dict[str, bool]` | Update prompts for all registered agents.                  |
| `update_prompt_by_key(prompt_key)`        | Yes               | `Dict[str, bool]` | Update all agents using a specific prompt key.             |
| `get_agent_prompt_mapping()`              | No                | `Dict[str, str]`  | Get the agent-to-prompt-key mapping.                       |

### Module-level Convenience Functions

| Function                             | Coroutine (async) | Return Value | Purpose (concise)                                 |
| ------------------------------------ | ----------------- | ------------ | ------------------------------------------------- |
| `setup_dynamic_agents(mas_instance)` | Yes               | `None`       | Setup dynamic prompt functionality for MAS agents.|
| `hot_reload_prompt(prompt_key)`      | Yes               | `bool`       | Hot reload a specific prompt by key.              |
| `hot_reload_all_prompts()`           | Yes               | `bool`       | Hot reload all prompts.                           |
| `hot_reload_agent(agent_name)`       | Yes               | `bool`       | Hot reload prompt for a specific agent.           |
