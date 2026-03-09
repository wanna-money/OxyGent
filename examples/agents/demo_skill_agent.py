import asyncio
import os

from oxygent import MAS, oxy, preset_tools


async def main():
    oxy_space = [
        oxy.HttpLLM(
            name="default_llm",
            api_key=os.getenv("DEFAULT_LLM_API_KEY"),
            base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
            model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        ),
        preset_tools.file_tools,
        preset_tools.shell_tools,
        oxy.SkillAgent(
            name="skill_agent",
            llm_model="default_llm",
            tools=["view_text_file", "execute_shell_command"],  # required
            skills=[".oxygent/skills"],  # A single skill folder or parent directory
        ),
    ]

    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="What skills do you have?")


if __name__ == "__main__":
    asyncio.run(main())
