"""Demo: Loading configuration from a JSON file.

Config.load_from_json() merges a "default" profile with an environment-
specific overlay selected by the `env` parameter (e.g., "dev", "prod").
At deploy time, set the APP_ENV environment variable to switch profiles
automatically.

For programmatic production configuration (log paths, server host/port,
etc.) without a JSON file, see demo_production_config.py.
"""

import asyncio
import os

from oxygent import MAS, Config, oxy

Config.load_from_json("./config.json", env="default")
Config.set_agent_llm_model("default_llm")

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    oxy.ReActAgent(
        name="master_agent",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="hello")


if __name__ == "__main__":
    asyncio.run(main())
