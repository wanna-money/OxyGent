# How to Register an Agent?

In OxyGent, a basic agent consists of an [Agent](./agent-types.md) and an internally wrapped [Large Language Model (LLM)](./select-llm.md).

For new users, you can use the `oxy.HttpLLM` method to register an LLM with your `api_key`:

```python
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.01},
        semaphore=4, # concurrency limit
        timeout=240, # maximum execution time
    ),
```
> For detailed explanation of the `semaphore` parameter, please refer to the [Parallel](../multi-agent/parallel.md) section.

Next, you can use `oxy.ChatAgent` or `oxy.ReActAgent` to wrap your first agent:
```python
    oxy.ReActAgent(
        name="master_agent",
        prompt = master_prompt, # supports custom prompts
        is_master=True, # set as master
        llm_model="default_llm",
    ),
```

For the LLM and agent to take effect, they need to be added to the `oxy_space`.

## Complete Runnable Example

Here is a complete runnable code example:

```python
import asyncio

from oxygent import MAS, oxy
import os

master_prompt = """
You are a document analysis expert. Users will provide you with documents. Please provide a brief summary of the document.
The summary can be in markdown format.
"""

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
    oxy.ReActAgent(
        name="master_agent",
        prompt = master_prompt,
        is_master=True,
        llm_model="default_llm",
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

[Previous: Run the Demo](../getting-started/demo.md)
[Next: Chat with an Agent](./chat-with-agent.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Single Agent Example](../../examples/agents/demo_single_agent.md) -- The simplest ChatAgent configuration
- [ReAct Agent Example](../../examples/agents/demo_react_agent.md) -- ReActAgent with reflection mechanism
- [Hierarchical Multi-Agent Example](../../examples/agents/demo_hierarchical_agents.md) -- Master-subordinate Agent architecture
