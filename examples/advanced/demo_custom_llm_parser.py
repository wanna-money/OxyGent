"""Demo: Custom LLM response parser using XML format.

By default, OxyGent expects the LLM to output tool calls in JSON format.
This example shows how to replace the default parser with a custom one
that uses XML tags instead, via the func_parse_llm_response parameter.

This is useful when working with LLMs that produce non-standard output
formats, or when you want fine-grained control over response parsing.
"""

import asyncio
import os
import xml.etree.ElementTree as ET

from oxygent import MAS, Config, OxyRequest, oxy
from oxygent.schemas import LLMResponse, LLMState

Config.set_agent_llm_model("default_llm")


# -- Custom XML-based LLM response parser --
async def parse_llm_response(
    ori_response: str, oxy_request: OxyRequest = None
) -> LLMResponse:
    """Parse XML-formatted LLM output into a structured LLMResponse.

    Expected formats:
        Tool call:  <tool><tool_name>name</tool_name>
                      <arguments><param>value</param></arguments></tool>
        Answer:     <answer><think>reasoning</think>final answer</answer>
    """
    try:
        root = ET.fromstring(ori_response)
        if root.find("tool_name") is not None:
            tool_call = {
                "tool_name": root.find("tool_name").text,
                "arguments": {
                    child.tag: child.text for child in root.find("arguments")
                },
            }
            return LLMResponse(
                state=LLMState.TOOL_CALL,
                output=tool_call,
                ori_response=ori_response,
            )
        else:
            think = root.find("think")
            think_text = think.text if think is not None else ""
            answer_text = "".join(root.itertext()).replace(think_text, "").strip()
            return LLMResponse(
                state=LLMState.ANSWER,
                output=answer_text,
                ori_response=ori_response,
            )
    except Exception as e:
        return LLMResponse(
            state=LLMState.ERROR_PARSE, output=str(e), ori_response=ori_response
        )


# -- Prompt that instructs the LLM to use XML format --
NOTE_AGENT_PROMPT = """\
You are a helpful note-taking assistant. Record memos in the format:
[2025-06-18 10:00] Location - Meeting

You should first get the current time (use Asia/Shanghai timezone),
then save the note to local_file/note.txt. Create the file if it does not exist.

Available tools:
${tools_description}

Choose the appropriate tool based on the user's request.
If no tool is needed, reply directly.
When answering a question requires multiple tool calls, call only one tool at a time.

IMPORTANT: Use the following XML formats for your responses:

1. When you want to call a tool:
<tool>
<think>your reasoning</think>
<tool_name>tool name here</tool_name>
<arguments>
<param1>value1</param1>
<param2>value2</param2>
</arguments>
</tool>

2. When you want to give a final answer:
<answer>
<think>your reasoning</think>
Your answer here
</answer>

Use only the tools explicitly defined above.
"""


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
        name="note_agent",
        prompt=NOTE_AGENT_PROMPT,
        tools=["time_tools", "file_tools"],
        # Register the custom XML parser
        func_parse_llm_response=parse_llm_response,
    ),
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        sub_agents=["note_agent"],
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Save a memo: team standup at 3 PM in room 618"
        )


if __name__ == "__main__":
    asyncio.run(main())
