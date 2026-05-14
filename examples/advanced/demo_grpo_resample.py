import asyncio
import os

from oxygent import MAS, Config, oxy, preset_tools
from oxygent.routes import get_task_info

Config.set_agent_llm_model("default_llm")
Config.set_message_is_send_tool_call(False)
Config.set_message_is_send_observation(False)
Config.set_storage_es_engine("MemoryEs")

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
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
    preset_tools.math_tools,
    oxy.ReActAgent(
        name="math_agent",
        desc="A tool that can perform mathematical calculations.",
        tools=["math_tools"],
    ),
    oxy.ReActAgent(
        is_master=True,
        name="master_agent",
        sub_agents=["time_agent", "file_agent", "math_agent"],
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        # Step1
        payload = {"query": "What time is it now? Please save it into time.txt."}
        oxy_response = await mas.chat_with_agent(payload)
        trace_id = oxy_response.oxy_request.current_trace_id

        await mas.await_background_tasks(trace_id)

        # Step2
        res = await get_task_info(trace_id)
        filterd_nodes = []
        for node in res["data"]["nodes"]:
            if node["node_type"] == "llm":
                filterd_nodes.append(node)

        # Step3
        tasks = []
        for node in sorted(filterd_nodes, key=lambda x: x["create_time"]):
            print(node["node_id"], node["caller"], node["callee"])
            payload = {"restart_node_id": node["node_id"]}
            tasks.append(mas.chat_with_agent(payload))
        oxy_responses = await asyncio.gather(*tasks)
        print("\n".join([oxy_response.output for oxy_response in oxy_responses]))


if __name__ == "__main__":
    asyncio.run(main())
