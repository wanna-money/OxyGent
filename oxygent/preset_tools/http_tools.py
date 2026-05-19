"""HTTP utility tools for OxyGent agents."""

import asyncio
import json
from typing import Any, Optional

import httpx

from oxygent.oxy import FunctionHub

http_tools = FunctionHub(name="http_tools")


@http_tools.tool(
    description="Make a GET request to a specified URL with optional headers and parameters"
)
def http_get(
    url: str,
    headers: Optional[dict[str, str]] = None,
    params: Optional[dict[str, Any]] = None,
) -> str:
    """Send an HTTP GET request."""
    try:
        # Use synchronous client
        with httpx.Client() as client:
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return json.dumps(
                {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content": response.text,
                },
                ensure_ascii=False,
            )
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@http_tools.tool(
    description="Make a POST request to a specified URL with optional headers and JSON data"
)
def http_post(
    url: str,
    data: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
) -> str:
    """Send an HTTP POST request."""
    try:
        # Ensure Content-Type is set to application/json
        if headers is None:
            headers = {}
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        # Use synchronous client
        with httpx.Client() as client:
            response = client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return json.dumps(
                {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content": response.text,
                },
                ensure_ascii=False,
            )
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def main() -> None:
    # GET request example
    result = await http_get("https://www.json.cn/", params={"key": "value"})
    print("GET Result:", result)

    # POST request example
    data = {"name": "test", "value": 123}
    result = await http_post("https://httpbin.org/post", data=data)
    print("POST Result:", result)


if __name__ == "__main__":
    asyncio.run(main())
