"""Standard I/O MCP client implementation.

This module provides the StdioMCPClient class, which implements MCP communication over
standard input/output streams. This transport method is ideal for local process
communication, allowing MCP servers to run as separate processes that communicate
through stdin/stdout pipes.
"""

import asyncio
import logging
import os
import shutil
import signal
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import Field

from .base_mcp_client import BaseMCPClient

logger = logging.getLogger(__name__)

_TERMINATE_TIMEOUT = 2.0


class StdioMCPClient(BaseMCPClient):
    """MCP client implementation using standard I/O transport.

    This class extends BaseMCPClient to provide MCP communication over stdio.
    It spawns and manages external processes (like Node.js scripts) that act
    as MCP servers, communicating through standard input/output streams.

    Attributes:
        params: Configuration parameters including command, arguments, and environment variables.
    """

    params: dict[str, Any] = Field(
        default_factory=dict, description="Stdio server parameters (command, args, env)"
    )

    async def _ensure_directories_exist(self, args: list[str]) -> None:
        """Ensure required directories exist before starting MCP server."""
        if len(args) >= 2 and "server-filesystem" in " ".join(args):
            target_dir = args[-1]
            if not os.path.exists(target_dir):
                try:
                    os.makedirs(target_dir, exist_ok=True)
                    logger.info(f"Created directory: {target_dir}")
                except Exception as e:
                    logger.warning(f"Could not create directory {target_dir}: {e}", exc_info=True)

        if args[0] == "--directory" and args[2] == "run":
            mcp_tool_file = os.path.join(args[1], args[3])
            if not os.path.exists(mcp_tool_file):
                raise FileNotFoundError(f"{mcp_tool_file} does not exist.")

    async def init(self, is_fetch_tools: bool = True) -> None:
        """Initialize the stdio connection to the MCP server process.

        Spawns an external process (such as a Node.js script) that acts as an MCP server,
        establishes stdio communication channels, creates a client session, and discovers
        available tools from the server.

        The method performs several validation steps:
        1. Resolves the command path (with special handling for 'npx')
        2. Validates that required files exist for directory-based commands
        3. Sets up environment variables
        4. Establishes stdio transport and session
        """

        try:
            server_params = await self.get_server_params()
            stdio_transport = await self._exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            self._session = await self._exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await self._session.initialize()
            if is_fetch_tools:
                await self.list_tools()
        except FileNotFoundError as e:
            # Re-raise specific validation errors without wrapping
            logger.error(f"Validation error for stdio server '{self.name}' (command={self.params.get('command')}): {e}", exc_info=True)
            await self.cleanup()
            raise
        except Exception as e:
            logger.error(f"Error initializing stdio server '{self.name}' (command={self.params.get('command')}): {e}", exc_info=True)
            await self.cleanup()
            raise Exception(f"Server {self.name} error")

    async def _on_cross_task_cleanup(self) -> None:
        """Terminate the MCP subprocess directly via signals.

        Used as a fallback when the exit-stack teardown cannot run in the
        original task.
        """
        process = self._find_stdio_process()
        if process is None:
            return

        pid = process.pid
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OSError):
            pass

        try:
            await asyncio.wait_for(process.wait(), timeout=_TERMINATE_TIMEOUT)
        except asyncio.TimeoutError:
            try:
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                pass
        except ProcessLookupError:
            pass

    def _find_stdio_process(self) -> Any:
        """Walk the exit-stack callbacks to locate the anyio Process handle."""
        for cb in reversed(self._exit_stack._exit_callbacks):
            wrapper = getattr(cb[1], "__self__", None)
            if wrapper is None:
                continue
            gen = getattr(wrapper, "gen", None)
            if gen is None:
                continue
            frame = getattr(gen, "ag_frame", None) or getattr(gen, "gi_frame", None)
            if frame and "process" in frame.f_locals:
                proc = frame.f_locals["process"]
                if hasattr(proc, "pid"):
                    return proc
        return None

    async def call_tool(self, tool_name: str, arguments: dict[str, Any], headers: Optional[dict[str, str]] = None) -> Any:
        server_params = await self.get_server_params()
        async with stdio_client(server_params) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                return await session.call_tool(tool_name, arguments)

    async def get_server_params(self) -> StdioServerParameters:
        command = (
            shutil.which("npx")
            if self.params["command"] == "npx"
            else self.params["command"]
        )
        if command is None:
            raise ValueError("The command must be a valid string and cannot be None.")

        args = self.params["args"]
        await self._ensure_directories_exist(args)
        if args[0] == "--directory" and args[2] == "run":
            mcp_tool_file = os.path.join(args[1], args[3])
            if not os.path.exists(mcp_tool_file):
                raise FileNotFoundError(f"{mcp_tool_file} does not exist.")
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env={**os.environ, **self.params["env"]}
            if self.params.get("env")
            else {**os.environ},
        )
        return server_params
