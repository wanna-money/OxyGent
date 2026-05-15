# How to Get the Raw Output of an Agent?

OxyGent provides a rich set of parameters for customizing how agents work.

If you want to get the raw output of an agent, simply set `trust_mode` to `True`. When trust mode is enabled, the agent directly returns the tool's execution result without performing any additional processing or parsing.

```python
    oxy.ReActAgent(
        name="trust_agent",
        desc="a time query agent with trust mode enabled",
        tools=["time_tools"],
        llm_model="default_llm",
        trust_mode=True,  # enable trust mode
        is_master=True,
    ),
```

For example, when trust mode is enabled, the raw output returned may look like this:

```
trust mode output: Tool [get_current_time] execution result: {
  "timezone": "Asia/Shanghai",
  "datetime": "2025-07-24T20:26:19+08:00",
  "is_dst": false
} 
```

If `trust_mode` is enabled, the framework can catch exceptions and perform error retries; otherwise, the `ReActAgent` will report the error upstream.

## Complete Runnable Example

Here is a complete runnable code example:

```python
import asyncio
from oxygent import MAS, oxy
import os

oxy_space = [
    # LLM configuration
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.01},
        semaphore=4,
    ),
    # time tool
    oxy.StdioMCPClient(
        name="time_tools",
        params={
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
        },
    ),
    # normal mode ReActAgent
    oxy.ReActAgent(
        name="normal_agent",
        desc="a time query agent with trust mode disabled",
        tools=["time_tools"],
        llm_model="default_llm",
        trust_mode=False,  # disable trust mode
    ),
    # trust mode ReActAgent
    oxy.ReActAgent(
        name="trust_agent",
        desc="a time query agent with trust mode enabled",
        tools=["time_tools"],
        llm_model="default_llm",
        trust_mode=True,  # enable trust mode
        is_master=True,
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        query = "What is the current time"

        print("=== normal mode test ===")
        normal_result = await mas.call("normal_agent", {"query": query})
        print(f"normal mode output: {normal_result}")

        print("\n=== trust mode test ===")
        trust_result = await mas.call("trust_agent", {"query": query})
        print(f"trust mode output: {trust_result}")


if __name__ == "__main__":
    asyncio.run(main())

```

[Previous: Parallel Execution](../multi-agent/parallel.md)
[Next: Processing Queries and Prompts](./process-input.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Trust Mode Example](../../examples/advanced/demo_trust_mode.md) -- Demonstrates how to enable trust mode to get the raw output of an agent
