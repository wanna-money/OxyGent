import asyncio
import os

from oxygent import MAS, oxy, preset_tools
from oxygent.prompts import SYSTEM_PROMPT_SHELL_USE

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    preset_tools.ssh_tools,
    oxy.ShellUseAgent(
        auth_info={
            "hostname": "127.0.0.1",
            "port": 22,
            "username": "root",
            "password": "admin",
        },
        prompt=SYSTEM_PROMPT_SHELL_USE,
        tools=["ssh_tools"],
        max_react_rounds=64,
        is_discard_react_memory=False,
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Please run the demo.py from https://github.com/jd-opensource/OxyGent.git"
        )


if __name__ == "__main__":
    asyncio.run(main())
