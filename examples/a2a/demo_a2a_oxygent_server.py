"""Run OxyGent MAS with built-in A2A server endpoints.

Run:
    PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py
"""

import asyncio
import os

from oxygent import MAS, Config, oxy

PORT = 8090
A2A_BASE_PATH = "/a2a"

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    oxy.ChatAgent(
        name="master_agent",
        llm_model="default_llm",
        is_master=True,
        desc="Local echo workflow as MAS target agent",
    ),
]


async def main():
    Config.set_server_port(PORT)
    async with MAS(
        oxy_space=oxy_space,
        enable_a2a_server=True,
        a2a_base_path=A2A_BASE_PATH,
    ) as mas:
        await mas.start_web_service(first_query="A2A MAS server is running.")


if __name__ == "__main__":
    asyncio.run(main())
