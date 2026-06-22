import asyncio
import os

from oxygent import MAS, Config, oxy, preset_tools

Config.set_agent_llm_model("default_llm")

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    preset_tools.math_tools,
    preset_tools.time_tools,
    oxy.ReActAgent(
        name="time_agent",
        desc="A tool that can query the time",
        tools=["time_tools"],
    ),
    preset_tools.file_tools,
    oxy.ReActAgent(
        name="file_agent",
        desc="A tool that can operate the file system",
        tools=["file_tools"],
    ),
    preset_tools.oxy_manage_tools,
    oxy.ReActAgent(
        name="doctor_agent",
        desc="A system administrator that can inspect, create, delete, move, and modify agents and tools in the organization at runtime",
        tools=["oxy_manage_tools"],
    ),
    oxy.ReActAgent(
        is_master=True,
        name="master_agent",
        sub_agents=["time_agent", "file_agent", "doctor_agent"],
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query=[
                "Please create a new ReActAgent named 'math_agent' with description 'A tool that can perform mathematical calculations', give it the math_tools, and attach it to master_agent.",
                "What is 2 raised to the power of 9?",
                "Please move the get_current_time Oxy from under time_agent to under master_agent, and then delete time_agent.",
                "what time it is now.",
            ]
        )


if __name__ == "__main__":
    asyncio.run(main())
