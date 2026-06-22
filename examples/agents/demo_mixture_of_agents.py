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
