# How to Quickly Duplicate Multiple Agents? (Mixture of Agents)

## Overview

Mixture of Agents (MoA) is a multi-agent collaboration pattern that creates multiple parallel instances of the same agent to process the same query, then aggregates all instances' responses into a single final answer. This approach is similar to Ensemble Learning in machine learning and can improve the quality and stability of responses.

In OxyGent, you can easily implement the MoA pattern using the `team_size` parameter, without manually creating and managing multiple agent instances.

## `team_size` Parameter Description

`team_size` is a configuration parameter for agents that specifies the number of instances to run in parallel:

- **Default value**: `team_size=1`, meaning only one instance runs (normal mode)
- **Setting `team_size=N`**: OxyGent automatically creates N agent instances with the same configuration, processing the same query in parallel
- All instances run independently, each producing its own response
- The system automatically aggregates the output of all instances to generate a final comprehensive answer

Use cases include:
- When more comprehensive and higher-quality answers are needed
- When you want to reduce the randomness and bias of individual answers
- Business scenarios with high reliability requirements for answers

## Basic Usage

If you need to generate multiple identical agents, you can use the `team_size` parameter to quickly duplicate agents.

```python
oxy.ReActAgent(
    name="time_agent",
    desc="A tool for time query",
    tools=["time_tools"],
    llm_model="default_llm",
    team_size=2,
),
```

`team_size` currently can only duplicate relatively simple agents. More comprehensive agent duplication will be supported in the future.

## Complete Runnable Example

Below is a complete example using `team_size` to implement Mixture of Agents. In this example, we create a `ChatAgent` with `team_size=4`, meaning 4 instances run simultaneously to answer the same question:

```python
"""Demo: Mixture of Agents (MoA) via the team_size parameter.

Setting team_size=N on an agent causes N parallel instances to process
the same query concurrently, producing an ensemble of responses that
are aggregated into a single answer.
"""

import asyncio
import os

from oxygent import MAS, oxy

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.7},
    ),
    oxy.ChatAgent(
        name="qa_agent",
        llm_model="default_llm",
        # MoA: 4 parallel instances process the same query and results are aggregated
        team_size=4,
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="What is the Agent?")


if __name__ == "__main__":
    asyncio.run(main())
```

### Running Instructions

1. Make sure you have configured the `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, and `DEFAULT_LLM_MODEL_NAME` environment variables in your `.env` file
2. After running the script, OxyGent will automatically duplicate `qa_agent` into 4 parallel instances
3. When a user sends a query, all 4 instances process it simultaneously, and the results are aggregated into a comprehensive answer
4. Increasing `temperature` appropriately (e.g., 0.7 in the example) can increase the diversity of responses across instances, resulting in a more comprehensive aggregated result

[Previous: Building a Simple Multi-Agent System](./multi-agent-system.md)
[Next: Running Agents in Parallel](./parallel.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Mixture of Agents Example](../../examples/agents/demo_mixture_of_agents.md) -- Demonstrates the complete usage of the MoA pattern via the team_size parameter
- [Parallel Agent Example](../../examples/agents/demo_parallel.md) -- Demonstrates ParallelAgent parallel execution, as a contrast to MoA
