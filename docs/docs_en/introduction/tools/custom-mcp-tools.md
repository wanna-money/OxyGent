# How to Use Custom MCP Tools?

In OxyGent, you can register custom MCP tools using either local mode or SSE mode.

## 1. Local MCP Tools

First, create an `mcp_servers` folder, and declare an MCP instance using `FastMCP` in the `/mcp_servers/math_tools.py` file:

```python
# mcp_servers/math_tools.py
import math
from decimal import Decimal, getcontext

from mcp.server.fastmcp import FastMCP
from pydantic import Field

# Initialize FastMCP server instance
mcp = FastMCP()
```

Next, you can register tools in a manner similar to `FunctionHub`:

```python
# mcp_servers/math_tools.py
@mcp.tool(description="Power calculator tool")
def power(
    n: int = Field(description="base"), m: int = Field(description="index", default=2)
) -> int:
    return math.pow(n, m)
# other tools...
```

Then, you can invoke these tools in `oxy_space`:

```python
    oxy.StdioMCPClient(
        name="math_tools",
        params={
            "command": "uv",
            "args": ["--directory", "./mcp_servers", "run", "math_tools.py"],
        },
    ),
```
## Complete Runnable Example

Below is a complete code example showing how to use multiple LLMs and an Agent in OxyGent, along with custom MCP tools:
```python
"""Demo for using OxyGent with multiple LLMs and an agent."""

import asyncio

from oxygent import MAS, oxy, Config
import os
from oxygent import preset_tools

Config.set_agent_llm_model("default_llm")

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.01},
        semaphore=4,
        timeout=240,
    ),
    oxy.StdioMCPClient(
        name="time_tools",
        params={
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
        },
    ),
    oxy.StdioMCPClient(
        name="math_tools",
        params={
            "command": "uv",
            "args": ["--directory", "./mcp_servers", "run", "math_tools.py"],
        },
    ),
    preset_tools.file_tools,
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        tools=["file_tools","time_tools","math_tools"],
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello!"
        )


if __name__ == "__main__":
    asyncio.run(main())
```

```python
#mcp_servers/math_tools.py
import math
from decimal import Decimal, getcontext

from mcp.server.fastmcp import FastMCP
from pydantic import Field

# Initialize FastMCP server instance
mcp = FastMCP()


@mcp.tool(description="Power calculator tool")
def power(
    n: int = Field(description="base"), m: int = Field(description="index", default=2)
) -> int:
    return math.pow(n, m)


@mcp.tool(description="Pi tool")
def calc_pi(prec: int = Field(description="How many digits after the dot")) -> float:
    """
    Calculate pi using the Chudnovsky algorithm for high precision.

    This implementation uses the Chudnovsky algorithm, which converges very rapidly.
    Each term in the series provides approximately 8 decimal digits of precision.

    Args:
        prec: The number of decimal places to calculate

    Returns:
        float: The value of pi with the specified precision
    """
    getcontext().prec = prec
    x = 0
    for k in range(
        int(prec / 8) + 1
    ):  # Calculate the series: each iteration provides ~8 decimal digits of precision
        a = 2 * Decimal.sqrt(Decimal(2)) / 9801
        b = math.factorial(4 * k) * (1103 + 26390 * k)
        c = pow(math.factorial(k), 4) * pow(396, 4 * k)
        x = x + a * b / c
    return 1 / x

# ---------------------------------------------------------------

# Entry point: run the MCP server when script is executed directly
if __name__ == "__main__":
    mcp.run()
```

## 2. SSE MCP Tools

If you need to use SSE MCP tools, you can add a port parameter when declaring the `FastMCP` object:

```python
mcp = FastMCP("math_tools", port=8000)
```

Then you can register the tools in OxyGent by passing the port in `sse_url`:

```python
oxy.SSEMCPClient(
    name="math_tools",
    sse_url="http://127.0.0.1:8000/sse"
),
```

## 3. Using StreamableMCPClient

`StreamableMCPClient` connects to remote MCP servers using the newer Streamable HTTP transport protocol. This is the recommended approach for remote connections in the MCP specification:

```python
    oxy.StreamableMCPClient(
        name="remote_tools",
        server_url="http://127.0.0.1:8000/mcp",
    ),
```

> `StreamableMCPClient` and `SSEMCPClient` are used in a similar way. The main difference is the underlying transport protocol. If your MCP server supports Streamable HTTP, prefer using `StreamableMCPClient`.

[Previous: Using Open-Source MCP Tools](./opensource-mcp-tools.md)
[Next: Managing Tool Invocation](./manage-tools.md)
[Back to Home](../readme.md)

---

## Related Examples

- [MCP Tool Usage Example](../../examples/tools/demo_mcp.md) -- Demonstrates basic usage of MCP tools
- [MCP with Headers Example](../../examples/tools/demo_mcp_with_headers.md) -- Demonstrates how to configure custom request headers for MCP tools
- [Train Ticket MCP Example](../../examples/mcp_tools/demo_train_ticket.md) -- A complete custom MCP tool application example
