# How to Use Open-Source MCP Tools?

When using MCP, you may want to use external tools. OxyGent supports integrating external open-source tools just like local tools. You can use `oxy.StdioMCPClient`, which is based on the MCP protocol, to import external tools.

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
import prompts
import tools

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
    tools.file_tools,
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
