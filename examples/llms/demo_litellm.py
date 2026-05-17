"""demo_litellm.py

Use any LLM provider through LiteLLM.  Install with: pip install litellm
"""

import asyncio

from oxygent import MAS, oxy

oxy_space = [
    oxy.LiteLLM(
        name="default_llm",
        model_name="anthropic/claude-sonnet-4-20250514",
        # api_key="sk-...",         # or set ANTHROPIC_API_KEY env var
        # base_url="http://localhost:4000",  # optional: LiteLLM proxy
    ),
    oxy.ReActAgent(
        name="agent",
        llm_model="default_llm",
        system_prompt="You are a helpful assistant.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        result = await mas.call(
            callee="agent",
            arguments={"messages": [{"role": "user", "content": "What is 2 + 2?"}]},
        )
        print("Result:", result.output)


if __name__ == "__main__":
    asyncio.run(main())
