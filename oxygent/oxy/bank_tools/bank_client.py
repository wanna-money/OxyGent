"""Bank client module for OxyGent.

Defines BankClient which connects to a bank server and registers its tools dynamically.
"""

from typing import Dict

import httpx
from pydantic import AnyUrl, Field

from ...schemas import OxyRequest, OxyResponse
from ...utils.common_utils import build_url
from .bank_tool import BankTool
from .base_bank import BaseBank


class BankClient(BaseBank):
    """Client that connects to a remote BankRouter and registers its tools as BankTool instances."""

    server_url: AnyUrl = Field("", description="URL of the remote bank server")
    included_bank_name_list: list = Field(
        default_factory=list,
        description="Names of bank tools discovered from the server",
    )
    headers: Dict[str, str] = Field(
        default_factory=dict, description="Extra HTTP headers"
    )

    async def init(self):
        """Connect to the bank server and fetch the tool list."""
        await super().init()
        url = build_url(self.server_url, "list_banks")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=self.timeout)
            self.add_tools(response.json())

    def add_tools(self, tools_response) -> None:
        """Register BankTool instances dynamically from the bank server's tools_response."""
        params = self.model_dump(
            exclude={
                "sse_url",
                "server_url",
                "included_bank_name_list",
                "name",
                "desc",
                "server_name",
                "input_schema",
            }
        )
        for item in tools_response:
            self.included_bank_name_list.append(item["name"])

            bank_tool = BankTool(
                name=item["name"],
                desc=item["description"],
                server_name=self.name,
                server_url=build_url(self.server_url, item["endpoint"]),
                input_schema=item["inputSchema"],
                is_retrievable=item.get("type", "retrieve") == "retrieve",
                func_process_input=self.func_process_input,
                func_process_output=self.func_process_output,
                func_format_input=self.func_format_input,
                func_format_output=self.func_format_output,
                func_execute=self.func_execute,
                func_interceptor=self.func_interceptor,
                **params,
            )
            bank_tool.set_mas(self.mas)
            self.mas.add_oxy(bank_tool)

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Forward the request to the appropriate tool on the bank server."""
        raise NotImplementedError("This method is not yet implemented")
