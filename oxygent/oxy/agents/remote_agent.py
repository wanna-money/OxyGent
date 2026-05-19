import copy
from typing import Any

from pydantic import AnyUrl, Field, field_validator

from ...schemas import OxyRequest, OxyResponse
from .base_agent import BaseAgent


class RemoteAgent(BaseAgent):
    """Base class for agents that communicate with remote systems.

    This agent provides the foundation for connecting to and interacting with
    remote agent systems over HTTP/HTTPS.

    Attributes:
        server_url (AnyUrl): The URL of the remote agent server.
        org (dict): Organization structure from the remote system.
    """

    server_url: AnyUrl = Field()
    org: dict[str, Any] = Field(default_factory=dict)

    @field_validator("server_url")
    def check_protocol(cls, v: Any) -> Any:
        """Pydantic field validator that ensures the protocol is supported."""
        if v.scheme not in ("http", "https"):
            raise ValueError("server_url must start with http:// or https://")
        return v

    def get_org(self) -> dict[str, Any]:
        """Return the organization tree for this remote agent."""

        # Mark child nodes as remote
        def update_children(children: list[dict[str, Any]]) -> list[dict[str, Any]]:
            """Recursively mark all child nodes as remote."""
            for node in children:
                node["is_remote"] = True
                if "children" in node and isinstance(node["children"], list):
                    update_children(node["children"])
            return children

        # Create deep copy and mark as remote
        children_copy = copy.deepcopy(self.org["children"])
        return update_children(children_copy)

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Execute by forwarding the request to the remote agent."""
        raise NotImplementedError("This method is not yet implemented")
