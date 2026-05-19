"""Streamable-HTTP MCP client implementation."""

import logging
from typing import Any, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pydantic import AnyUrl, Field

from ...utils.common_utils import build_url
from .base_mcp_client import BaseMCPClient

logger = logging.getLogger(__name__)


class StreamableMCPClient(BaseMCPClient):
    """MCP client implementation using Streamable-HTTP transport."""

    server_url: AnyUrl = Field(
        "", description="URL of the MCP server's streamable-HTTP endpoint"
    )
    middlewares: list[Any] = Field(
        default_factory=list, description="Client-side MCP middlewares"
    )

    async def init(self, is_fetch_tools: bool = True) -> None:
        """Initialize the HTTP streaming connection to the MCP server.

        Args:
            is_fetch_tools (bool): If True, fetch the tool list after connecting.
        """
        try:
            if not self.is_dynamic_headers and self.is_keep_alive:
                self._http_transport = await self._exit_stack.enter_async_context(
                    streamablehttp_client(
                        build_url(self.server_url),
                        headers=self.headers,
                        timeout=self.timeout,
                    )
                )
                read, write, _ = self._http_transport

                self._session = await self._exit_stack.enter_async_context(
                    ClientSession(read, write)
                )

                for mw in self.middlewares:
                    if hasattr(self._session, "add_middleware"):
                        self._session.add_middleware(mw)
                    else:
                        logger.warning("middleware %s is ignored", mw)

                await self._session.initialize()
                if is_fetch_tools:
                    await self.list_tools()
            else:
                async with streamablehttp_client(
                    build_url(self.server_url),
                    headers=self.headers,
                    timeout=self.timeout,
                ) as (read, write, _):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools_response = await session.list_tools()
                        self.add_tools(tools_response)
        except Exception as e:
            logger.error("Error initializing server %s: %s", self.name, e)
            await self.cleanup()
            raise Exception(f"Server {self.name} error") from e

    async def call_tool(self, tool_name: str, arguments: dict[str, Any], headers: Optional[dict[str, str]] = None) -> Any:
        """Open a fresh streamable-HTTP connection and invoke the named tool with arguments."""
        async with streamablehttp_client(
            build_url(self.server_url), headers=headers, timeout=self.timeout
        ) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool(tool_name, arguments)
