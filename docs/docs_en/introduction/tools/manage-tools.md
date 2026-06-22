# How to Manage Agent Tool Usage Behavior?

In OxyGent, agents specify the tools they can use through the `tools` parameter. Tools are referenced by name -- `tools=["time_tools"]` means the agent can use the tool component named `time_tools` in the `oxy_space`.

## Basic Tool Assignment

```python
oxy.ReActAgent(
    name="time_agent",
    desc="An agent that can query the current time",
    tools=["time_tools"],           # Allow usage of time_tools
    except_tools=["dangerous_tool"], # Forbid usage of dangerous_tool
    llm_model="default_llm",
)
```

> The tool name corresponds to the `name` attribute of a tool component in the `oxy_space` list. At runtime, MAS automatically looks up and associates the tools.

## Parameter Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tools` | `list[str]` | `[]` | List of allowed tool names |
| `except_tools` | `list[str]` | `[]` | List of forbidden tool names |
| `sub_agents` | `list[str]` | `[]` | List of sub-agent names (can be invoked as tools) |
| `is_sourcing_tools` | `bool` | `False` | Whether to enable semantic tool retrieval (requires vector DB configuration) |
| `top_k_tools` | `int` | `10` | Number of tools returned by semantic retrieval |
| `is_retain_subagent_in_toolset` | `bool` | `False` | Whether to include sub-agents in the tool list |
| `is_retrieve_even_if_tools_scarce` | `bool` | `True` | Whether to still perform retrieval when the number of tools is small |

## Tool Resolution Flow

When an agent runs, OxyGent determines the available tools using the following logic:

1. From the `tools` list, look up the corresponding tool components by name in the `oxy_space`
2. From the `sub_agents` list, look up sub-agents (sub-agents can also be invoked as tools)
3. If `except_tools` is set, remove the corresponding tools from the available tool set
4. If `is_sourcing_tools=True`, use the vector database to perform semantic retrieval on tools, returning the `top_k_tools` most relevant tools

## Complete Example

```python
import asyncio, os
from oxygent import MAS, oxy, preset_tools

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    preset_tools.time_tools,
    preset_tools.math_tools,
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        tools=["time_tools", "math_tools"],
        llm_model="default_llm",
    ),
]

async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="What time is it now?")

if __name__ == "__main__":
    asyncio.run(main())
```

[Previous: Using Custom MCP Tools](./custom-mcp-tools.md)
[Next: Setting Up OxyGent Config](../getting-started/config.md)
[Back to Home](../readme.md)

---

## Related Examples

- [FunctionHub Tool Registration Example](../../examples/tools/demo_functionhub.md) -- Demonstrates tool registration and management
- [ReAct Agent Example](../../examples/agents/demo_react_agent.md) -- Demonstrates how agents automatically invoke tools
