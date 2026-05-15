# How to Build a Simple Multi-Agent System?

If you find that a single agent cannot meet your business needs, using a multi-agent system can effectively solve this problem.

In the simple example below, we manage functionally related tools using subagents. We recommend new users use `oxy.ReActAgent` to invoke these tools:

```python
    oxy.ReActAgent(
        name="file_agent",
        desc="A tool that can operate the file system",
        tools=["file_tools"],
    ),
    oxy.ReActAgent(
        name="time_agent",
        desc="A tool that can get current time",
        tools=["time_tools"],
    ),
    oxy.ReActAgent(
        name="math_agent",
        desc="A tool that can do math calculates",
        tools=["math_tools"],
    ),
```

Next, you need to register a **master_agent**, which is responsible for orchestrating other agents within the MAS. Declare the other subagents as the **master_agent**'s `sub_agents`:
```python
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        sub_agents=["file_agent","time_agent","math_agent"],
    ),
```

OxyGent's agent system structure is very flexible, meaning you can register multi-level subagents without manually managing the collaboration relationships between them.

## Complete Runnable Example

Below is a complete runnable code example:

```python
"""Demo for using OxyGent with multiple LLMs and an agent."""

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
    oxy.StdioMCPClient(
        name="math_tools",
        params={
            "command": "uv",
            "args": ["--directory", "./mcp_servers", "run", "math_tools.py"],
        },
    ),
    tools.file_tools,
    oxy.ReActAgent(
        name="file_agent",
        desc="A tool that can operate the file system",
        tools=["file_tools"],
    ),
    oxy.ReActAgent(
        name="time_agent",
        desc="A tool that can get current time",
        tools=["time_tools"],
    ),
    oxy.ReActAgent(
        name="math_agent",
        desc="A tool that can do math calculates",
        tools=["math_tools"],
    ),
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        sub_agents=["file_agent","time_agent","math_agent"],
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

[Previous: Document Tools Guide](../tools/document-tools.md)
[Next: Mixture of Agents](./mixture-of-agents.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Hierarchical Agent Example](../../examples/agents/demo_hierarchical_agents.md) -- Demonstrates collaboration among multi-level subagents
- [Heterogeneous Agent Example](../../examples/agents/demo_heterogeneous_agents.md) -- Demonstrates combining different types of agents
- [Single Agent Example](../../examples/agents/demo_single_agent.md) -- For comparison, demonstrates basic single agent usage
