"""Integration tests for Config behavior and runtime effects.

Tests cover:
- Config.set_agent_llm_model() changes the default LLM for agents
- Config.set_module_config() and get_module_config() round-trip
- Config isolation between tests (via autouse reset_config fixture)
- Multiple Config changes within a session are independent

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
"""

from oxygent.config import Config

# ============================================================================
# Tests
# ============================================================================


class TestConfigSetAndGet:
    """Test Config set/get methods."""

    def test_set_agent_llm_model(self):
        """set_agent_llm_model should update the agent.llm_model config."""
        Config.set_agent_llm_model("test_model")
        assert Config.get_agent_llm_model() == "test_model"

    def test_set_module_config_key_value(self):
        """set_module_config with key/value should store correctly."""
        Config.set_module_config("test_module", "test_key", "test_value")
        assert Config.get_module_config("test_module", "test_key") == "test_value"

    def test_set_module_config_bulk(self):
        """set_module_config with a dict (value=None) should replace the
        entire module config."""
        Config.set_module_config("bulk_module", {"a": 1, "b": 2})
        assert Config.get_module_config("bulk_module", "a") == 1
        assert Config.get_module_config("bulk_module", "b") == 2

    def test_get_module_config_default(self):
        """get_module_config should return the default when key is missing."""
        result = Config.get_module_config("nonexistent", "missing_key", "fallback")
        assert result == "fallback"

    def test_get_module_config_entire_module(self):
        """get_module_config with key=None should return the entire module dict."""
        Config.set_module_config("mod", "x", 10)
        Config.set_module_config("mod", "y", 20)
        mod_config = Config.get_module_config("mod")
        assert isinstance(mod_config, dict)
        assert mod_config.get("x") == 10
        assert mod_config.get("y") == 20


class TestConfigDefaults:
    """Test Config default values."""

    def test_default_llm_temperature(self):
        """Default LLM temperature should be 0.1."""
        assert Config.get_module_config("llm", "temperature") == 0.1

    def test_default_llm_max_tokens(self):
        """Default LLM max_tokens should be 4096."""
        assert Config.get_module_config("llm", "max_tokens") == 4096

    def test_default_oxy_retries(self):
        """Default oxy retries should be 2."""
        assert Config.get_oxy_retries() == 2

    def test_default_oxy_delay(self):
        """Default oxy delay should be 1.0."""
        assert Config.get_oxy_delay() == 1.0

    def test_default_agent_short_memory_size(self):
        """Default short_memory_size should be 10."""
        assert Config.get_agent_short_memory_size() == 10

    def test_default_tool_mcp_is_keep_alive(self):
        """Default MCP keep_alive should be True."""
        assert Config.get_tool_mcp_is_keep_alive() is True

    def test_default_token_tracking_enabled(self):
        """Default token tracking should be True."""
        assert Config.get_token_tracking_enabled() is True


class TestConfigIsolation:
    """Test that Config changes in one test do not affect another."""

    def test_config_change_step_1(self):
        """Change a config value in this test."""
        Config.set_agent_llm_model("isolated_model_1")
        assert Config.get_agent_llm_model() == "isolated_model_1"

    def test_config_change_step_2(self):
        """Verify the change from step_1 is NOT visible here due to
        the autouse reset_config fixture."""
        assert Config.get_agent_llm_model() != "isolated_model_1"


class TestConfigMultipleChanges:
    """Test multiple Config changes within a single test."""

    def test_sequential_config_changes(self):
        """Multiple set calls should each be independently effective."""
        Config.set_agent_llm_model("model_a")
        assert Config.get_agent_llm_model() == "model_a"

        Config.set_agent_llm_model("model_b")
        assert Config.get_agent_llm_model() == "model_b"

        Config.set_module_config("llm", "temperature", 0.5)
        assert Config.get_module_config("llm", "temperature") == 0.5

        Config.set_module_config("llm", "max_tokens", 2048)
        assert Config.get_module_config("llm", "max_tokens") == 2048

    def test_different_modules_are_independent(self):
        """Changes to one module should not affect another."""
        Config.set_module_config("agent", "llm_model", "agent_model")
        Config.set_module_config("llm", "temperature", 0.9)

        assert Config.get_agent_llm_model() == "agent_model"
        assert Config.get_module_config("llm", "temperature") == 0.9

        Config.set_module_config("agent", "llm_model", "changed_model")
        assert Config.get_agent_llm_model() == "changed_model"
        assert Config.get_module_config("llm", "temperature") == 0.9
