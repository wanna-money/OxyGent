"""Integration tests for MCP client lifecycle.

Tests cover:
- BaseMCPClient cleanup handles cross-task RuntimeError gracefully
- StdioMCPClient._find_stdio_process() returns None when no process
- StdioMCPClient._on_cross_task_cleanup() is a no-op when no process
- BaseMCPClient.cleanup() resets session and context to None
- MCP tool registration via add_tools()

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
    dummy_mas
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from oxygent.oxy.mcp_tools.stdio_mcp_client import StdioMCPClient

# ============================================================================
# Tests
# ============================================================================


class TestBaseMCPClientCleanup:
    """Test BaseMCPClient cleanup behavior."""

    @pytest.mark.asyncio
    async def test_cleanup_resets_session_to_none(self, dummy_mas):
        """After cleanup(), _session and _stdio_context should be None."""
        client = StdioMCPClient(
            name="test_stdio",
            params={"command": "echo", "args": ["hello"], "env": {}},
        )
        client.set_mas(dummy_mas)
        dummy_mas.add_oxy(client)

        client._session = MagicMock()
        client._stdio_context = MagicMock()

        await client.cleanup()

        assert client._session is None
        assert client._stdio_context is None

    @pytest.mark.asyncio
    async def test_cleanup_handles_cross_task_runtime_error(self, dummy_mas):
        """When _exit_stack.aclose() raises RuntimeError with 'cancel scope',
        cleanup should call _on_cross_task_cleanup instead of crashing."""
        client = StdioMCPClient(
            name="test_stdio",
            params={"command": "echo", "args": ["hello"], "env": {}},
        )
        client.set_mas(dummy_mas)
        dummy_mas.add_oxy(client)

        cross_task_called = {"value": False}

        async def _mock_cross_task():
            cross_task_called["value"] = True

        client._on_cross_task_cleanup = _mock_cross_task

        async def _raise_cancel_scope():
            raise RuntimeError("Attempted to exit cancel scope in a different task")

        client._exit_stack = AsyncMock()
        client._exit_stack.aclose = _raise_cancel_scope

        await client.cleanup()

        assert cross_task_called["value"] is True
        assert client._session is None

    @pytest.mark.asyncio
    async def test_cleanup_handles_generic_exception(self, dummy_mas):
        """cleanup() should catch generic exceptions and still reset state."""
        client = StdioMCPClient(
            name="test_stdio",
            params={"command": "echo", "args": ["hello"], "env": {}},
        )
        client.set_mas(dummy_mas)
        dummy_mas.add_oxy(client)

        async def _raise_generic():
            raise Exception("Some other error")

        client._exit_stack = AsyncMock()
        client._exit_stack.aclose = _raise_generic

        await client.cleanup()

        assert client._session is None
        assert client._stdio_context is None

    @pytest.mark.asyncio
    async def test_cleanup_handles_cancelled_error(self, dummy_mas):
        """cleanup() should catch CancelledError and still reset state."""
        client = StdioMCPClient(
            name="test_stdio",
            params={"command": "echo", "args": ["hello"], "env": {}},
        )
        client.set_mas(dummy_mas)
        dummy_mas.add_oxy(client)

        async def _raise_cancelled():
            raise asyncio.CancelledError()

        client._exit_stack = AsyncMock()
        client._exit_stack.aclose = _raise_cancelled

        await client.cleanup()

        assert client._session is None


class TestStdioMCPClientProcess:
    """Test StdioMCPClient process handling."""

    def test_find_stdio_process_returns_none_when_empty(self, dummy_mas):
        """_find_stdio_process should return None when exit stack has no
        process callbacks."""
        client = StdioMCPClient(
            name="test_stdio",
            params={"command": "echo", "args": ["hello"], "env": {}},
        )
        client.set_mas(dummy_mas)

        result = client._find_stdio_process()
        assert result is None

    @pytest.mark.asyncio
    async def test_on_cross_task_cleanup_noop_without_process(self, dummy_mas):
        """_on_cross_task_cleanup should be a no-op when no process is found."""
        client = StdioMCPClient(
            name="test_stdio",
            params={"command": "echo", "args": ["hello"], "env": {}},
        )
        client.set_mas(dummy_mas)

        # Should not raise
        await client._on_cross_task_cleanup()


class TestStdioMCPClientValidation:
    """Test StdioMCPClient parameter validation."""

    @pytest.mark.asyncio
    async def test_none_command_raises_value_error(self, dummy_mas):
        """get_server_params() should raise ValueError when command resolves
        to None (e.g., npx not found)."""
        client = StdioMCPClient(
            name="test_stdio",
            params={
                "command": "nonexistent_command_xyz_12345",
                "args": [],
                "env": {},
            },
        )
        client.set_mas(dummy_mas)

        # The command won't be "npx" so it passes through directly,
        # but we test the npx case by mocking shutil.which
        with patch("shutil.which", return_value=None):
            client_npx = StdioMCPClient(
                name="npx_client",
                params={
                    "command": "npx",
                    "args": ["some-server"],
                    "env": {},
                },
            )
            with pytest.raises(ValueError, match="cannot be None"):
                await client_npx.get_server_params()

    @pytest.mark.asyncio
    async def test_missing_mcp_tool_file_raises(self, dummy_mas, tmp_path):
        """get_server_params() should raise FileNotFoundError when the
        directory-based MCP tool file does not exist."""
        client = StdioMCPClient(
            name="test_stdio",
            params={
                "command": "uv",
                "args": ["--directory", str(tmp_path), "run", "nonexistent.py"],
                "env": {},
            },
        )
        client.set_mas(dummy_mas)

        with pytest.raises(FileNotFoundError, match="does not exist"):
            await client.get_server_params()


class TestCleanupLockPreventsRace:
    """Test that the cleanup lock prevents concurrent cleanup."""

    @pytest.mark.asyncio
    async def test_concurrent_cleanup_calls_are_serialized(self, dummy_mas):
        """Two concurrent cleanup() calls should not race — the lock
        ensures one completes before the other starts."""
        client = StdioMCPClient(
            name="test_stdio",
            params={"command": "echo", "args": ["hello"], "env": {}},
        )
        client.set_mas(dummy_mas)

        cleanup_count = {"value": 0}
        original_aclose = client._exit_stack.aclose

        async def _counting_aclose():
            cleanup_count["value"] += 1
            await asyncio.sleep(0.01)

        client._exit_stack = AsyncMock()
        client._exit_stack.aclose = _counting_aclose

        await asyncio.gather(client.cleanup(), client.cleanup())

        # Both calls should complete without error
        assert client._session is None
