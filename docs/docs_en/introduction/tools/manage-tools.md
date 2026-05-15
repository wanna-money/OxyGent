# How to Manage Agent Tool Usage Behavior?

By default, tool invocation by an agent is handled by its internal LLM. However, OxyGent provides a set of parameters to help you manage how agents invoke tools. Below are the parameters you may need:

+ Allow/Forbid an agent from using tools

```python
    oxy.LocalAgent(
        name="time_agent",
        desc="A tool that can get current time",
        tools=["time_tools"], # Allow usage
        except_tools=["math_tools"], # Forbid usage
    ),
```

+ Manage agent tool retrieval

```python
    oxy.LocalAgent(
        name="time_agent",
        desc="A tool that can get current time",
        tools=["time_tools"], 
        is_sourcing_tools = True, # Whether to retrieve tools
        is_retain_subagent_in_toolset = True, # Whether to keep subagents in the toolset
        top_k_tools = 10; # Number of tools returned by retrieval
        is_retrieve_even_if_tools_scarce = True, # Whether to keep retrieving when tools are scarce
    ),
```

[Previous: Using Custom MCP Tools](./custom-mcp-tools.md)
[Next: Setting Up OxyGent Config](../getting-started/config.md)
[Back to Home](../readme.md)

---

## Related Examples

- [FunctionHub Tool Registration Example](../../examples/tools/demo_functionhub.md) -- Demonstrates tool registration and management
- [ReAct Agent Example](../../examples/agents/demo_react_agent.md) -- Demonstrates how agents automatically invoke tools
