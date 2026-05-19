"""Configuration settings for the MAS."""

import json
import logging
import os
import re
from typing import Any, Optional


def deep_update(d: dict[str, Any], u: dict[str, Any]) -> None:
    """Recursively merge source dict into target dict, modifying target in place."""
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            deep_update(d[k], v)
        else:
            d[k] = v


def replace_env_var(val: Any) -> Any:
    """Convert ${VAR} in strings to environment variables recursively."""
    pattern = re.compile(r"\$\{(\w+)\}")
    if isinstance(val, str):

        def replacer(match: re.Match[str]) -> str:
            var_name = match.group(1)
            return os.environ.get(var_name, "")

        return pattern.sub(replacer, val)
    elif isinstance(val, dict):
        return {k: replace_env_var(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [replace_env_var(v) for v in val]
    else:
        return val


class Config:
    """Singleton configuration manager.

    Loads settings from config.json with environment layering and supports
    ${VAR} env-var substitution.
    """

    _env: str = "default"
    _config: dict[str, Any] = {
        "app": {
            "name": "app",
            "version": "1.0.0",
        },
        "log": {
            "path": "./cache_dir/app.log",
            "level_root": "INFO",
            "level_terminal": "INFO",
            "level_file": "INFO",
            "color_is_on_background": False,
            "is_bright": False,
            "only_message_color": True,
            "color_tool_call": "YELLOW",
            "color_observation": "CYAN",
            "is_detailed_tool_call": True,
            "is_detailed_observation": True,
        },
        "llm": {
            "temperature": 0.1,
            "max_tokens": 4096,
            "top_p": 1,
            "semaphore": 16,
            "timeout": 300,
        },
        "cache": {
            "save_dir": "./cache_dir",
        },
        "message": {
            "is_send_tool_call": True,
            "is_send_observation": True,
            "is_send_think": True,
            "is_send_answer": True,
            "is_stored": False,
            "stream_batch_size": 256,
            "is_show_in_terminal": False,
            "is_send_full_arguments": False,
        },
        "vearch": {},
        "es": {},
        "es_schema": {
            "shared_data": {"type": "text"},
            "group_data": {"type": "text"},
        },
        "es_settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1,
        },
        "storage": {
            "es_engine": "LocalEs",  # JesEs/LocalEs/MemoryEs
        },
        "redis": {},
        "redis_param": {
            "expire_time": 86400,  # 24 hours 60 * 60 * 24
            "max_size": 1024,
            "max_length": 20480,  # 20MB
        },
        "server": {
            "host": "127.0.0.1",
            "port": 8080,
            "auto_open_webpage": True,
            "log_level": "INFO",
            "workers": 1,
            "allow_origins": ["*"],
        },
        "oxy": {
            "semaphore": 1024,
            "timeout": 3600,
            "retries": 2,
            "delay": 1.0,
        },
        "agent": {
            "prompt": "",
            "llm_model": "default_llm",
            "input_schema": {
                "properties": {"query": {"description": "Query question"}},
                "required": ["query"],
            },
            "short_memory_size": 10,
            "welcome_message": "Hi, I’m OxyGent. How can I assist you?",
        },
        "tool": {
            "mcp_is_keep_alive": True,
            "is_concurrent_init": True,
            "semaphore": 1024,
            "timeout": 60,
        },
        "live_prompt": {
            "is_active": False,
            "es_polling_interval": 2,  # ES polling interval in seconds for version sync
        },
        "token_tracking": {
            "enabled": True,
            "encoding_map": {"<Your Model Name>": "<Your Encoding Name>"},
            "default_encoding": "o200k_base",
        },
        "oxy_request": {
            "is_save_history": True,
            "is_send_message": True,
            "is_async_storage": True,
        },
    }

    @classmethod
    def load_from_json(
        cls, path: str = "./config.json", env: Optional[str] = None
    ) -> None:
        with open(path, "r", encoding="utf-8") as f:
            all_cfg = json.load(f)
        if not env:
            env = os.environ.get("APP_ENV", "default")
        cls._env = env
        # Merge default
        if "default" in all_cfg:
            cfg = replace_env_var(all_cfg["default"])
            deep_update(cls._config, cfg)
        # Merge assigned env
        if env in all_cfg:
            cfg = replace_env_var(all_cfg[env])
            deep_update(cls._config, cfg)

    @classmethod
    def set_module_config(cls, module: str, key: Any, value: Any = None) -> None:
        if module not in cls._config:
            cls._config[module] = {}
        if value is None:
            cls._config[module] = key
        else:
            cls._config[module][key] = value

    @classmethod
    def get_module_config(
        cls, module: str, key: Optional[str] = None, default: Any = None
    ) -> Any:
        mod_cfg = cls._config.get(module, {})
        if key is None:
            return mod_cfg
        return mod_cfg.get(key, default)

    # --- app ---

    @classmethod
    def set_app_config(cls, app_config: dict[str, Any]) -> None:
        return cls.set_module_config("app", app_config)

    @classmethod
    def get_app_config(cls) -> dict[str, Any]:
        return cls.get_module_config("app")

    @classmethod
    def set_app_name(cls, name: str) -> None:
        cls.set_module_config("app", "name", name)

    @classmethod
    def get_app_name(cls) -> str:
        return cls.get_module_config("app", "name")

    @classmethod
    def set_app_version(cls, version: str) -> None:
        cls.set_module_config("app", "version", version)

    @classmethod
    def get_app_version(cls) -> str:
        return cls.get_module_config("app", "version")

    # --- log ---

    @classmethod
    def set_log_config(cls, log_config: dict[str, Any]) -> None:
        return cls.set_module_config("log", log_config)

    @classmethod
    def get_log_config(cls) -> dict[str, Any]:
        return cls.get_module_config("log")

    @classmethod
    def set_log_path(cls, path: str) -> None:
        cls.set_module_config("log", "path", path)

    @classmethod
    def get_log_path(cls) -> str:
        return cls.get_module_config("log", "path")

    @classmethod
    def set_log_level_root(cls, level_root: str) -> None:
        cls.set_module_config("log", "level_root", level_root)
        logger = logging.getLogger()
        logger.setLevel(level_root)

    @classmethod
    def get_log_level_root(cls) -> str:
        return cls.get_module_config("log", "level_root")

    @classmethod
    def set_log_level_terminal(cls, level_terminal: str) -> None:
        cls.set_module_config("log", "level_terminal", level_terminal)
        logger = logging.getLogger()
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(level_terminal)

    @classmethod
    def get_log_level_terminal(cls) -> str:
        return cls.get_module_config("log", "level_terminal")

    @classmethod
    def set_log_level_file(cls, level_file: str) -> None:
        cls.set_module_config("log", "level_file", level_file)
        logger = logging.getLogger()
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.setLevel(level_file)

    @classmethod
    def get_log_level_file(cls) -> str:
        return cls.get_module_config("log", "level_file")

    @classmethod
    def set_log_color_is_on_background(
        cls, color_is_on_background: bool = True
    ) -> None:
        cls.set_module_config("log", "color_is_on_background", color_is_on_background)

    @classmethod
    def get_log_color_is_on_background(cls) -> bool:
        return cls.get_module_config("log", "color_is_on_background")

    @classmethod
    def set_log_is_bright(cls, is_bright: bool = True) -> None:
        cls.set_module_config("log", "is_bright", is_bright)

    @classmethod
    def get_log_is_bright(cls) -> bool:
        return cls.get_module_config("log", "is_bright")

    @classmethod
    def set_log_only_message_color(cls, only_message_color: bool = True) -> None:
        cls.set_module_config("log", "only_message_color", only_message_color)

    @classmethod
    def get_log_only_message_color(cls) -> bool:
        return cls.get_module_config("log", "only_message_color")

    @classmethod
    def set_log_color_tool_call(cls, color_tool_call: Any = True) -> None:
        cls.set_module_config("log", "color_tool_call", color_tool_call)

    @classmethod
    def get_log_color_tool_call(cls) -> str:
        return cls.get_module_config("log", "color_tool_call")

    @classmethod
    def set_log_color_observation(cls, color_observation: Any = True) -> None:
        cls.set_module_config("log", "color_observation", color_observation)

    @classmethod
    def get_log_color_observation(cls) -> str:
        return cls.get_module_config("log", "color_observation")

    @classmethod
    def set_log_is_detailed_tool_call(cls, is_detailed_tool_call: bool = True) -> None:
        cls.set_module_config("log", "is_detailed_tool_call", is_detailed_tool_call)

    @classmethod
    def get_log_is_detailed_tool_call(cls) -> bool:
        return cls.get_module_config("log", "is_detailed_tool_call")

    @classmethod
    def set_log_is_detailed_observation(
        cls, is_detailed_observation: bool = True
    ) -> None:
        cls.set_module_config("log", "is_detailed_observation", is_detailed_observation)

    @classmethod
    def get_log_is_detailed_observation(cls) -> bool:
        return cls.get_module_config("log", "is_detailed_observation")

    # --- llm ---

    @classmethod
    def set_llm_config(cls, llm_config: dict[str, Any]) -> None:
        return cls.set_module_config("llm", llm_config)

    @classmethod
    def get_llm_config(cls, exclude: Optional[list[str]] = None) -> dict[str, Any]:
        if exclude is None:
            exclude = []
        return {
            k: v for k, v in cls.get_module_config("llm").items() if k not in exclude
        }

    @classmethod
    def set_llm_semaphore(cls, semaphore: int) -> None:
        cls.set_module_config("llm", "semaphore", semaphore)

    @classmethod
    def get_llm_semaphore(cls) -> int:
        return cls.get_module_config("llm", "semaphore")

    @classmethod
    def set_llm_timeout(cls, timeout: int) -> None:
        cls.set_module_config("llm", "timeout", timeout)

    @classmethod
    def get_llm_timeout(cls) -> int:
        return cls.get_module_config("llm", "timeout")

    # --- cache ---

    @classmethod
    def set_cache_config(cls, cache_config: dict[str, Any]) -> None:
        return cls.set_module_config("cache", cache_config)

    @classmethod
    def get_cache_config(cls) -> dict[str, Any]:
        return cls.get_module_config("cache")

    @classmethod
    def set_cache_save_dir(cls, save_dir: str) -> None:
        cls.set_module_config("cache", "save_dir", save_dir)

    @classmethod
    def get_cache_save_dir(cls) -> str:
        save_dir = cls.get_module_config("cache", "save_dir")
        import os

        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        return save_dir

    # --- message ---

    @classmethod
    def set_message_config(cls, message_config: dict[str, Any]) -> None:
        return cls.set_module_config("message", message_config)

    @classmethod
    def get_message_config(cls) -> dict[str, Any]:
        return cls.get_module_config("message")

    @classmethod
    def set_message_is_send_tool_call(cls, is_send_tool_call: bool) -> None:
        cls.set_module_config("message", "is_send_tool_call", is_send_tool_call)

    @classmethod
    def get_message_is_send_tool_call(cls) -> bool:
        return cls.get_module_config("message", "is_send_tool_call")

    @classmethod
    def set_message_is_send_observation(cls, is_send_observation: bool) -> None:
        cls.set_module_config("message", "is_send_observation", is_send_observation)

    @classmethod
    def get_message_is_send_observation(cls) -> bool:
        return cls.get_module_config("message", "is_send_observation")

    @classmethod
    def set_message_is_send_think(cls, is_send_think: bool) -> None:
        cls.set_module_config("message", "is_send_think", is_send_think)

    @classmethod
    def get_message_is_send_think(cls) -> bool:
        return cls.get_module_config("message", "is_send_think")

    @classmethod
    def set_message_is_send_answer(cls, is_send_answer: bool) -> None:
        cls.set_module_config("message", "is_send_answer", is_send_answer)

    @classmethod
    def get_message_is_send_answer(cls) -> bool:
        return cls.get_module_config("message", "is_send_answer")

    @classmethod
    def set_message_is_stored(cls, is_stored: bool = True) -> None:
        cls.set_module_config("message", "is_stored", is_stored)

    @classmethod
    def get_message_is_stored(cls) -> bool:
        return cls.get_module_config("message", "is_stored")

    @classmethod
    def set_message_stream_batch_size(cls, stream_batch_size: int = 128) -> None:
        cls.set_module_config("message", "stream_batch_size", stream_batch_size)

    @classmethod
    def get_message_stream_batch_size(cls) -> int:
        return cls.get_module_config("message", "stream_batch_size")

    @classmethod
    def set_message_is_show_in_terminal(cls, is_show_in_terminal: bool = True) -> None:
        cls.set_module_config("message", "is_show_in_terminal", is_show_in_terminal)

    @classmethod
    def get_message_is_show_in_terminal(cls) -> bool:
        return cls.get_module_config("message", "is_show_in_terminal")

    @classmethod
    def set_message_is_send_full_arguments(
        cls, is_send_full_arguments: bool = True
    ) -> None:
        cls.set_module_config(
            "message", "is_send_full_arguments", is_send_full_arguments
        )

    @classmethod
    def get_message_is_send_full_arguments(cls) -> bool:
        return cls.get_module_config("message", "is_send_full_arguments")

    # --- es ---

    @classmethod
    def set_es_config(cls, es_config: dict[str, Any]) -> None:
        cls.set_module_config("es", es_config)

    @classmethod
    def get_es_config(cls) -> dict[str, Any]:
        return cls.get_module_config("es")

    # --- es_schema ---

    @classmethod
    def set_es_schema_config(cls, es_schema_config: dict[str, Any]) -> None:
        cls.set_module_config("es_schema", es_schema_config)

    @classmethod
    def get_es_schema_config(cls) -> dict[str, Any]:
        return cls.get_module_config("es_schema")

    @classmethod
    def set_es_schema_shared_data(cls, es_schema_config: dict[str, Any]) -> None:
        return cls.set_module_config("es_schema", "shared_data", es_schema_config)

    @classmethod
    def get_es_schema_shared_data(cls) -> dict[str, Any]:
        shared_data_schema = cls.get_module_config("es_schema", "shared_data")
        if "properties" in shared_data_schema and "type" in shared_data_schema:
            del shared_data_schema["type"]
        return shared_data_schema

    @classmethod
    def set_es_schema_group_data(cls, es_schema_config: dict[str, Any]) -> None:
        return cls.set_module_config("es_schema", "group_data", es_schema_config)

    @classmethod
    def get_es_schema_group_data(cls) -> dict[str, Any]:
        group_data_schema = cls.get_module_config("es_schema", "group_data")
        if "properties" in group_data_schema and "type" in group_data_schema:
            del group_data_schema["type"]
        return group_data_schema

    # --- es_settings ---

    @classmethod
    def set_es_settings_config(cls, es_settings_config: dict[str, Any]) -> None:
        cls.set_module_config("es_settings", es_settings_config)

    @classmethod
    def get_es_settings_config(cls) -> dict[str, Any]:
        return cls.get_module_config("es_settings")

    # --- storage ---

    @classmethod
    def set_storage_config(cls, storage_config: dict[str, Any]) -> None:
        cls.set_module_config("storage", storage_config)

    @classmethod
    def get_storage_config(cls) -> dict[str, Any]:
        return cls.get_module_config("storage")

    @classmethod
    def set_storage_es_engine(cls, es_engine: str) -> None:
        cls.set_module_config("storage", "es_engine", es_engine)

    @classmethod
    def get_storage_es_engine(cls) -> str:
        return cls.get_module_config("storage", "es_engine")

    # --- vearch ---

    @classmethod
    def set_vearch_config(cls, vearch_config: dict[str, Any]) -> None:
        cls.set_module_config("vearch", vearch_config)

    @classmethod
    def get_vearch_config(cls) -> dict[str, Any]:
        return cls.get_module_config("vearch")

    @classmethod
    def get_vearch_embedding_model_url(cls) -> str:
        return cls.get_module_config("vearch", "embedding_model_url")

    # --- redis ---

    @classmethod
    def set_redis_config(cls, redis_config: dict[str, Any]) -> None:
        cls.set_module_config("redis", redis_config)

    @classmethod
    def get_redis_config(cls) -> dict[str, Any]:
        return cls.get_module_config("redis")

    # --- redis_param ---

    @classmethod
    def set_redis_expire_time(cls, expire_time: int) -> None:
        cls.set_module_config("redis_param", "expire_time", expire_time)

    @classmethod
    def get_redis_expire_time(cls) -> int:
        return cls.get_module_config("redis_param", "expire_time")

    @classmethod
    def set_redis_max_size(cls, max_size: int) -> None:
        cls.set_module_config("redis_param", "max_size", max_size)

    @classmethod
    def get_redis_max_size(cls) -> int:
        return cls.get_module_config("redis_param", "max_size")

    @classmethod
    def set_redis_max_length(cls, max_length: int) -> None:
        cls.set_module_config("redis_param", "max_length", max_length)

    @classmethod
    def get_redis_max_length(cls) -> int:
        return cls.get_module_config("redis_param", "max_length")

    # --- server ---

    @classmethod
    def set_server_config(cls, server_config: dict[str, Any]) -> None:
        cls.set_module_config("server", server_config)

    @classmethod
    def get_server_config(cls) -> dict[str, Any]:
        return cls.get_module_config("server")

    @classmethod
    def set_server_host(cls, host: str) -> None:
        cls.set_module_config("server", "host", host)

    @classmethod
    def get_server_host(cls) -> str:
        return cls.get_module_config("server", "host")

    @classmethod
    def set_server_port(cls, port: int) -> None:
        cls.set_module_config("server", "port", port)

    @classmethod
    def get_server_port(cls) -> int:
        return cls.get_module_config("server", "port")

    @classmethod
    def set_server_auto_open_webpage(cls, auto_open_webpage: bool = True) -> None:
        cls.set_module_config("server", "auto_open_webpage", auto_open_webpage)

    @classmethod
    def get_server_auto_open_webpage(cls) -> bool:
        return cls.get_module_config("server", "auto_open_webpage")

    @classmethod
    def set_server_log_level(cls, log_level: str) -> None:
        cls.set_module_config("server", "log_level", log_level)

    @classmethod
    def get_server_log_level(cls) -> str:
        return cls.get_module_config("server", "log_level")

    @classmethod
    def set_server_workers(cls, workers: Optional[int] = None) -> None:
        if workers is None:
            workers = os.cpu_count() * 2 + 1
        cls.set_module_config("server", "workers", workers)

    @classmethod
    def get_server_workers(cls) -> int:
        return cls.get_module_config("server", "workers")

    @classmethod
    def set_server_allow_origins(
        cls, allow_origins: Optional[list[str]] = None
    ) -> None:
        if allow_origins is None:
            allow_origins = ["*"]
        cls.set_module_config("server", "allow_origins", allow_origins)

    @classmethod
    def get_server_allow_origins(cls) -> list[str]:
        return cls.get_module_config("server", "allow_origins")

    # --- oxy ---

    @classmethod
    def set_oxy_config(cls, oxy_config: dict[str, Any]) -> None:
        cls.set_module_config("oxy", oxy_config)

    @classmethod
    def get_oxy_config(cls) -> dict[str, Any]:
        return cls.get_module_config("oxy")

    @classmethod
    def set_oxy_semaphore(cls, semaphore: int) -> None:
        cls.set_module_config("oxy", "semaphore", semaphore)

    @classmethod
    def get_oxy_semaphore(cls) -> int:
        return cls.get_module_config("oxy", "semaphore")

    @classmethod
    def set_oxy_timeout(cls, timeout: int) -> None:
        cls.set_module_config("oxy", "timeout", timeout)

    @classmethod
    def get_oxy_timeout(cls) -> int:
        return cls.get_module_config("oxy", "timeout")

    @classmethod
    def set_oxy_retries(cls, retries: int) -> None:
        cls.set_module_config("oxy", "retries", retries)

    @classmethod
    def get_oxy_retries(cls) -> int:
        return cls.get_module_config("oxy", "retries")

    @classmethod
    def set_oxy_delay(cls, delay: float) -> None:
        cls.set_module_config("oxy", "delay", delay)

    @classmethod
    def get_oxy_delay(cls) -> float:
        return cls.get_module_config("oxy", "delay")

    # --- agent ---

    @classmethod
    def set_agent_config(cls, agent_config: dict[str, Any]) -> None:
        cls.set_module_config("agent", agent_config)

    @classmethod
    def get_agent_config(cls) -> dict[str, Any]:
        return cls.get_module_config("agent")

    @classmethod
    def set_agent_prompt(cls, prompt: str) -> None:
        cls.set_module_config("agent", "prompt", prompt)

    @classmethod
    def get_agent_prompt(cls) -> str:
        return cls.get_module_config("agent", "prompt")

    @classmethod
    def set_agent_llm_model(cls, llm_model: str) -> None:
        cls.set_module_config("agent", "llm_model", llm_model)

    @classmethod
    def get_agent_llm_model(cls) -> str:
        return cls.get_module_config("agent", "llm_model")

    @classmethod
    def set_agent_input_schema(cls, input_schema: dict[str, Any]) -> None:
        cls.set_module_config("agent", "input_schema", input_schema)

    @classmethod
    def get_agent_input_schema(cls) -> dict[str, Any]:
        return cls.get_module_config("agent", "input_schema")

    @classmethod
    def set_agent_short_memory_size(cls, short_memory_size: int) -> None:
        cls.set_module_config("agent", "short_memory_size", short_memory_size)

    @classmethod
    def get_agent_short_memory_size(cls) -> int:
        return cls.get_module_config("agent", "short_memory_size")

    @classmethod
    def set_agent_welcome_message(cls, welcome_message: str) -> None:
        cls.set_module_config("agent", "welcome_message", welcome_message)

    @classmethod
    def get_agent_welcome_message(cls) -> str:
        return cls.get_module_config("agent", "welcome_message")

    # --- tool ---

    @classmethod
    def set_tool_config(cls, tool_config: dict[str, Any]) -> None:
        cls.set_module_config("tool", tool_config)

    @classmethod
    def get_tool_config(cls) -> dict[str, Any]:
        return cls.get_module_config("tool")

    @classmethod
    def set_tool_mcp_is_keep_alive(cls, mcp_is_keep_alive: bool) -> None:
        cls.set_module_config("tool", "mcp_is_keep_alive", mcp_is_keep_alive)

    @classmethod
    def get_tool_mcp_is_keep_alive(cls) -> bool:
        return cls.get_module_config("tool", "mcp_is_keep_alive")

    @classmethod
    def set_tool_is_concurrent_init(cls, is_concurrent_init: bool) -> None:
        cls.set_module_config("tool", "is_concurrent_init", is_concurrent_init)

    @classmethod
    def get_tool_is_concurrent_init(cls) -> bool:
        return cls.get_module_config("tool", "is_concurrent_init")

    @classmethod
    def set_tool_semaphore(cls, semaphore: int) -> None:
        cls.set_module_config("tool", "semaphore", semaphore)

    @classmethod
    def get_tool_semaphore(cls) -> int:
        return cls.get_module_config("tool", "semaphore")

    @classmethod
    def set_tool_timeout(cls, timeout: int) -> None:
        cls.set_module_config("tool", "timeout", timeout)

    @classmethod
    def get_tool_timeout(cls) -> int:
        return cls.get_module_config("tool", "timeout")

    # --- live_prompt ---

    @classmethod
    def set_live_prompt_config(cls, live_prompt_config: dict[str, Any]) -> None:
        cls.set_module_config("live_prompt", live_prompt_config)

    @classmethod
    def get_live_prompt_config(cls) -> dict[str, Any]:
        return cls.get_module_config("live_prompt")

    @classmethod
    def set_live_prompt_is_active(cls, is_active: bool) -> None:
        cls.set_module_config("live_prompt", "is_active", is_active)

    @classmethod
    def get_live_prompt_is_active(cls) -> bool:
        return cls.get_module_config("live_prompt", "is_active")

    @classmethod
    def set_live_prompt_es_polling_interval(cls, es_polling_interval: int) -> None:
        cls.set_module_config("live_prompt", "es_polling_interval", es_polling_interval)

    @classmethod
    def get_live_prompt_es_polling_interval(cls) -> int:
        return cls.get_module_config("live_prompt", "es_polling_interval")

    # token_tracking

    @classmethod
    def get_token_tracking_enabled(cls) -> bool:
        """Whether token tracking is enabled (default: True)."""
        return cls.get_module_config("token_tracking", "enabled", True)

    @classmethod
    def set_token_tracking_enabled(cls, enabled: bool) -> None:
        cls.set_module_config("token_tracking", "enabled", enabled)

    @classmethod
    def get_token_encoding_map(cls) -> dict[str, str]:
        """Get model-to-encoding mapping for tiktoken.

        Returns empty dict by default, which means all models use the
        default encoding returned by ``get_token_default_encoding()``.
        """
        return cls.get_module_config("token_tracking", "encoding_map", {})

    @classmethod
    def set_token_encoding_map(cls, mapping: dict[str, str]) -> None:
        cls.set_module_config("token_tracking", "encoding_map", mapping)

    @classmethod
    def get_token_default_encoding(cls) -> str:
        """Default tiktoken encoding name when no model-specific match.

        Defaults to ``o200k_base`` (used by GPT-4o and later models).
        """
        return cls.get_module_config("token_tracking", "default_encoding", "o200k_base")

    # --- oxy_request ---

    @classmethod
    def set_oxy_request_config(cls, oxy_request_config: dict[str, Any]) -> None:
        cls.set_module_config("oxy_request", oxy_request_config)

    @classmethod
    def get_oxy_request_config(cls) -> dict[str, Any]:
        return cls.get_module_config("oxy_request")

    @classmethod
    def set_oxy_request_is_save_history(cls, is_save_history: bool) -> None:
        cls.set_module_config("oxy_request", "is_save_history", is_save_history)

    @classmethod
    def get_oxy_request_is_save_history(cls) -> bool:
        return cls.get_module_config("oxy_request", "is_save_history")

    @classmethod
    def set_oxy_request_is_send_message(cls, is_send_message: bool) -> None:
        cls.set_module_config("oxy_request", "is_send_message", is_send_message)

    @classmethod
    def get_oxy_request_is_send_message(cls) -> bool:
        return cls.get_module_config("oxy_request", "is_send_message")

    @classmethod
    def set_oxy_request_is_async_storage(cls, is_async_storage: bool) -> None:
        cls.set_module_config("oxy_request", "is_async_storage", is_async_storage)

    @classmethod
    def get_oxy_request_is_async_storage(cls) -> bool:
        return cls.get_module_config("oxy_request", "is_async_storage")
