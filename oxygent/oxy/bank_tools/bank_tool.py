"""Bank tool module for OxyGent.

Defines BankTool, an individual tool entry registered from a bank server.
"""

import logging
from typing import Literal

import httpx
from pydantic import AnyUrl, Field

from ...schemas import OxyRequest, OxyResponse, OxyState
from .base_bank import BaseBank

logger = logging.getLogger(__name__)


class BankTool(BaseBank):
    """A single tool exposed by a BankClient/bank server.

    Invokes its endpoint over HTTP (GET or POST) and returns the raw
    response text.

    Attributes:
        server_url: URL of the bank server endpoint for this tool.
        method: HTTP method used when invoking this tool.
        is_permission_required: Whether permission is required before execution.
        headers: Extra HTTP headers sent with the request.
        is_retrievable: Whether this tool can be discovered via vector search.
    """

    server_url: AnyUrl = Field(
        "", description="URL of the bank server endpoint for this tool"
    )
    method: Literal["GET", "POST"] = Field(
        "POST", description="HTTP method used when invoking this tool"
    )
    is_permission_required: bool = Field(
        True, description="Whether permission is required for execution"
    )
    headers: dict[str, str] = Field(
        default_factory=dict, description="Extra HTTP headers"
    )
    is_retrievable: bool = Field(
        False,
        description="Whether this tool can be discovered via vector search retrieval",
    )

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Invoke this tool's HTTP endpoint on the bank server.

        Args:
            oxy_request: The request whose arguments are sent as query
                params (GET) or JSON body (POST).

        Returns:
            An OxyResponse containing the HTTP response text.

        Raises:
            httpx.HTTPStatusError: If the response status code indicates an error.
        """
        async with httpx.AsyncClient() as client:
            kwargs = {"headers": self.headers, "timeout": self.timeout}
            if self.method.upper() == "GET":
                kwargs["params"] = oxy_request.arguments
            else:
                kwargs["json"] = oxy_request.arguments
            response = await client.request(self.method, str(self.server_url), **kwargs)
            response.raise_for_status()
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=response.text,
            )
