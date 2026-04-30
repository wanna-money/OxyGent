"""Bank tool module for OxyGent.

Defines BankTool, an individual tool entry registered from a bank server.
"""

import logging
from typing import Dict, Literal

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
        "GET", description="HTTP method used when invoking this tool"
    )
    is_permission_required: bool = Field(
        True, description="Whether permission is required for execution"
    )
    headers: Dict[str, str] = Field(
        default_factory=dict, description="Extra HTTP headers"
    )
    is_retrievable: bool = Field(
        False,
        description="Whether this tool can be discovered via vector search retrieval",
    )

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Invoke this tool through its parent BankClient."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                str(self.server_url),
                headers=self.headers,
                timeout=self.timeout,
                json=oxy_request.arguments,
            )
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=response.text,
            )
