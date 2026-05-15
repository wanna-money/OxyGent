"""Unit tests for oxygent.config (deep_update, replace_env_var, Config)."""

import copy
import json
import os
import tempfile

import pytest

from oxygent.config import Config, deep_update, replace_env_var


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def reset_config():
    """Save and restore Config class state between tests."""
    orig_config = copy.deepcopy(Config._config)
    orig_env = Config._env
    yield
    Config._config = orig_config
    Config._env = orig_env


# ──────────────────────────────────────────────────────────────────────────────
# deep_update
# ──────────────────────────────────────────────────────────────────────────────
def test_deep_update_flat():
    d = {"a": 1, "b": 2}
    deep_update(d, {"b": 3, "c": 4})
    assert d == {"a": 1, "b": 3, "c": 4}


def test_deep_update_nested():
    d = {"x": {"a": 1, "b": 2}, "y": 10}
    deep_update(d, {"x": {"b": 99, "c": 100}})
    assert d == {"x": {"a": 1, "b": 99, "c": 100}, "y": 10}


def test_deep_update_empty_source():
    d = {"a": 1}
    deep_update(d, {})
    assert d == {"a": 1}


def test_deep_update_overwrite_non_dict():
    d = {"a": {"nested": 1}}
    deep_update(d, {"a": "overwritten"})
    assert d == {"a": "overwritten"}


# ──────────────────────────────────────────────────────────────────────────────
# replace_env_var
# ──────────────────────────────────────────────────────────────────────────────
def test_replace_env_var_string(monkeypatch):
    monkeypatch.setenv("MY_VAR", "hello")
    assert replace_env_var("prefix_${MY_VAR}_suffix") == "prefix_hello_suffix"


def test_replace_env_var_missing_var(monkeypatch):
    monkeypatch.delenv("NONEXISTENT_VAR_XYZ", raising=False)
    assert replace_env_var("${NONEXISTENT_VAR_XYZ}") == ""


def test_replace_env_var_no_match():
    assert replace_env_var("no variables here") == "no variables here"


def test_replace_env_var_dict(monkeypatch):
    monkeypatch.setenv("HOST", "localhost")
    result = replace_env_var({"url": "http://${HOST}:8080", "port": 8080})
    assert result == {"url": "http://localhost:8080", "port": 8080}


def test_replace_env_var_list(monkeypatch):
    monkeypatch.setenv("ITEM", "x")
    result = replace_env_var(["${ITEM}", "static"])
    assert result == ["x", "static"]


def test_replace_env_var_non_string():
    assert replace_env_var(42) == 42
    assert replace_env_var(None) is None


# ──────────────────────────────────────────────────────────────────────────────
# Config.load_from_json
# ──────────────────────────────────────────────────────────────────────────────
def test_load_from_json_default():
    cfg_data = {
        "default": {"app": {"name": "test_app", "custom_key": "custom_val"}}
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(cfg_data, f)
        f.flush()
        Config.load_from_json(path=f.name, env="default")

    assert Config.get_app_name() == "test_app"
    assert Config.get_module_config("app", "custom_key") == "custom_val"
    os.unlink(f.name)


def test_load_from_json_env_overlay():
    cfg_data = {
        "default": {"app": {"name": "base_app"}},
        "staging": {"app": {"name": "staging_app"}},
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(cfg_data, f)
        f.flush()
        Config.load_from_json(path=f.name, env="staging")

    assert Config.get_app_name() == "staging_app"
    os.unlink(f.name)


def test_load_from_json_with_env_vars(monkeypatch):
    monkeypatch.setenv("APP_PORT", "9090")
    cfg_data = {"default": {"server": {"port": "${APP_PORT}"}}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(cfg_data, f)
        f.flush()
        Config.load_from_json(path=f.name, env="default")

    assert Config.get_module_config("server", "port") == "9090"
    os.unlink(f.name)


# ──────────────────────────────────────────────────────────────────────────────
# Config.get_module_config / set_module_config
# ──────────────────────────────────────────────────────────────────────────────
def test_get_module_config_default():
    assert Config.get_module_config("nonexistent", "key", "fallback") == "fallback"


def test_get_module_config_whole_module():
    app_cfg = Config.get_module_config("app")
    assert isinstance(app_cfg, dict)
    assert "name" in app_cfg


def test_set_module_config():
    Config.set_module_config("app", "custom_field", "custom_value")
    assert Config.get_module_config("app", "custom_field") == "custom_value"


def test_set_module_config_replace_whole():
    Config.set_module_config("app", {"name": "replaced"})
    assert Config.get_module_config("app") == {"name": "replaced"}


def test_set_module_config_new_module():
    Config.set_module_config("new_module", "key1", "val1")
    assert Config.get_module_config("new_module", "key1") == "val1"


# ──────────────────────────────────────────────────────────────────────────────
# Config convenience methods
# ──────────────────────────────────────────────────────────────────────────────
def test_get_cache_save_dir(tmp_path, monkeypatch):
    Config.set_module_config("cache", "save_dir", str(tmp_path / "new_cache"))
    result = Config.get_cache_save_dir()
    assert result == str(tmp_path / "new_cache")
    assert os.path.isdir(result)


def test_set_server_workers():
    Config.set_server_workers(4)
    assert Config.get_server_workers() == 4


def test_set_server_workers_default():
    Config.set_server_workers(None)
    expected = os.cpu_count() * 2 + 1
    assert Config.get_server_workers() == expected


def test_get_set_app_name():
    Config.set_app_name("my_app")
    assert Config.get_app_name() == "my_app"


def test_get_set_app_version():
    Config.set_app_version("2.0.0")
    assert Config.get_app_version() == "2.0.0"


def test_get_llm_defaults():
    assert Config.get_module_config("llm", "temperature") == 0.1
    assert Config.get_module_config("llm", "semaphore") == 16
    assert Config.get_module_config("llm", "timeout") == 300
