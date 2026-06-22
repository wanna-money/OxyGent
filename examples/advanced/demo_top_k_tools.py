"""Demo: Automatic top-K tool retrieval via vector similarity.

When an agent has many tools registered, setting top_k_tools=N causes
only the N most relevant tools (by vector similarity to the query) to
be presented to the LLM on each turn. This reduces prompt size and
improves tool selection accuracy.

NOTE: This feature requires a Vearch vector database and an embedding
model to be configured. Load a config with Vearch settings, e.g.:
    Config.load_from_json("./config.json", env="test")
"""

import asyncio
import os

from oxygent import MAS, Config, oxy

# Load config that includes Vearch vector DB and embedding model settings.
# The "test" environment should define vearch.router_url, vearch.db_name, etc.
Config.load_from_json("./config.json", env="test")


oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.1},
    ),
    oxy.StdioMCPClient(
        name="time_tools",
        params={
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
        },
    ),
    oxy.StdioMCPClient(
        name="file_tools",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "./local_file"],
        },
    ),
    oxy.ReActAgent(
        name="master_agent",
        llm_model="default_llm",
        tools=["time_tools", "file_tools"],
        # Only the top 3 most relevant tools are sent to the LLM per query
        top_k_tools=3,
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="What time is it now?")


if __name__ == "__main__":
    asyncio.run(main())
