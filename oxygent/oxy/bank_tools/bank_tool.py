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
    """A single tool exposed by a BankClient/bank server."""

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
        """Invoke this tool through its parent BankClient."""
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
