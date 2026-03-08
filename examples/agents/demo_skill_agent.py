"""
SkillAgent demo - Direct path-based skill loading.

This demonstrates the simplified skill management architecture:

1. SkillAgent accepts skill directory paths directly via `skills` parameter
2. No need for SkillSource components or global registry
3. Skills are loaded directly from specified paths during initialization

KEY CONCEPT:
- skills=["./path/to/skills1", "./path/to/skills2"] - Direct path binding
- Each path can be a single skill folder or parent directory containing multiple skills
- SKILL.md files define skill metadata (name, description, etc.)

Usage:
  1. Manual activation: /<skill-name> [task]
  2. Natural language: "I want to create a skill..." (requires enable_selector=True)
  3. List skills: "What skills do you have?"
"""
import asyncio
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from oxygent import MAS, Config, oxy, preset_tools


async def main():
    oxy_space = [
        oxy.HttpLLM(
            name="default_llm",
            api_key=os.getenv("DEFAULT_LLM_API_KEY"),
            base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
            model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        ),

        # Direct path binding - no SkillSource needed
        oxy.SkillAgent(
            name="master_agent",
            llm_model="default_llm",
            enable_selector=True,
            tools=["view_text_file", "execute_shell_command"],
            # Direct skill paths - each can be a single skill folder or parent directory
            skills=[
                ".oxygent/skills",
            ],
        ),

        preset_tools.file_tools,
        preset_tools.shell_tools,
    ]

    async with MAS(oxy_space=oxy_space) as mas:
        first_query = (
            "What skills do you have?\n"
        )
        await mas.start_web_service(first_query=first_query)


if __name__ == "__main__":
    asyncio.run(main())