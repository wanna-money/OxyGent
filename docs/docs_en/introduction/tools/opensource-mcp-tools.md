# How to Use Open-Source MCP Tools?

When using MCP, you may want to use external tools. OxyGent supports integrating external open-source tools just like local tools. You can use `oxy.StdioMCPClient`, which is based on the MCP protocol, to import external tools.

## What is MCP?

MCP (Model Context Protocol) is an open standard protocol for connecting AI agents to external tools and data sources. With MCP, you can enable agents to use file systems, databases, search engines, browsers, and various other external capabilities without writing tool code yourself.

OxyGent natively supports the MCP protocol and provides three MCP clients:
- `oxy.StdioMCPClient` — Connects to a local MCP server via standard input/output (most common)
- `oxy.SSEMCPClient` — Connects to a remote MCP server via SSE
- `oxy.StreamableMCPClient` — Connects to a remote MCP server via Streamable HTTP

## Prerequisites: Install uv

The examples in this document use the `uvx` command to run MCP tools. `uvx` is a command provided by the `uv` package manager that can run Python packages directly without global installation.

Install uv:
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Where to Find MCP Tools?

- [MCP Servers Official List](https://github.com/modelcontextprotocol/servers) — Officially maintained collection of MCP tools
- [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) — Community-maintained list of MCP tools
- Search for `mcp-server-*` on NPM / PyPI — A large number of third-party MCP tool packages are available

For example, if you want to use a tool to get the current time, you can use the `mcp-server-time` tool:

```python
oxy.StdioMCPClient(
    name="time_tools",
    params={
        "command": "uvx",
        "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
    },
),
```

## Complete Runnable Example

Below is a complete runnable code example:

```python
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
    preset_tools.file_tools,
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        tools=["file_tools","time_tools"],
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

[Previous: Registering a Tool](./register-tool.md)
[Next: Using Custom MCP Tools](./custom-mcp-tools.md)
[Back to Home](../readme.md)

---

## Related Examples

- [MCP Tool Usage Example](../../examples/tools/demo_mcp.md) -- Demonstrates how to use open-source MCP tools in OxyGent
- [Browser MCP Tool Example](../../examples/mcp_tools/browser_demo.md) -- Demonstrates integration of browser-based MCP tools
