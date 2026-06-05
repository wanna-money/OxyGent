"""HTTP tool module for making HTTP requests.

This module provides the HttpTool class, which enables making HTTP requests to external
APIs and services. It supports configurable methods, headers, and parameters with proper
timeout handling.
"""

import httpx
from pydantic import Field

from ...schemas import OxyRequest, OxyResponse, OxyState
from ..base_tool import BaseTool


class HttpTool(BaseTool):
    """Tool for making HTTP requests to external APIs and services.

    Attributes:
        method (str): HTTP method to use. Defaults to "GET".
        url (str): Target URL for the HTTP request.
        headers (dict): HTTP headers to include in the request.
        default_params (dict): Default parameters that will be merged with
            request arguments.
    """

    method: str = Field("GET", description="HTTP method to use")
    url: str = Field("", description="Target URL for the HTTP request")
    headers: dict = Field(default_factory=dict, description="HTTP headers to include")
    default_params: dict = Field(
        default_factory=dict, description="Default request parameters"
    )

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Execute the HTTP request using the configured method.

        Merges ``default_params`` with the request arguments and dispatches
        the appropriate HTTP verb (GET, POST, PUT, DELETE, PATCH, or custom).

        Args:
            oxy_request: The request whose arguments are used as query
                parameters or JSON body.

        Returns:
            An OxyResponse containing the HTTP response text.

        Raises:
            httpx.HTTPStatusError: If the response status code indicates an error.
        """
        # Merge default parameters with request arguments
        params = self.default_params.copy()
        params.update(oxy_request.arguments)

        # Make HTTP request with timeout handling
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            method = self.method.upper()
            if method == "GET":
                http_response = await client.get(
                    self.url, params=params, headers=self.headers
                )
            elif method == "POST":
                http_response = await client.post(
                    self.url, json=params, headers=self.headers
                )
            elif method == "PUT":
                http_response = await client.put(
                    self.url, json=params, headers=self.headers
                )
            elif method == "DELETE":
                http_response = await client.delete(
                    self.url, params=params, headers=self.headers
                )
            elif method == "PATCH":
                http_response = await client.patch(
                    self.url, json=params, headers=self.headers
                )
            else:
                http_response = await client.request(
                    method, self.url, params=params, headers=self.headers
                )
            http_response.raise_for_status()
            return OxyResponse(state=OxyState.COMPLETED, output=http_response.text)
