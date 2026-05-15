# How to Customize Prompt Processing for Sub-Agents?

In more complex MAS systems, you may need to update prompts to prevent critical information from being lost as it passes between agents.

OxyGent supports processing prompts through external methods. For example, if you include file content in a prompt and want to ensure that every Agent can read the complete prompt, you can use the `update_query` method to pass the prompt via the query.

## OxyRequest Quick Reference

`func_process_input` receives an `OxyRequest` object. You can use the following methods to access and modify the request content:

| Method | Description |
|--------|-------------|
| `get_query()` | Get the query received by the current agent |
| `get_query(master_level=True)` | Get the user's original query to the master agent |
| `set_query(text)` | Replace the current query content |
| `get_short_memory()` | Get the conversation memory of the current agent |
| `get_short_memory(master_level=True)` | Get the conversation memory of the master agent |
| `call(callee, arguments)` | Call another agent or tool by name |
| `send_message(msg)` | Send a streaming message to the frontend |
| `get_shared_data(key)` | Get trace-level shared data |
| `set_shared_data(key, value)` | Set trace-level shared data |
| `get_global_data(key)` | Get MAS-level global data |

> `master_level=True` retrieves data at the master agent level, rather than the current sub-agent's data. This is useful when a sub-agent needs to understand the user's original intent.

## Example: Updating the Prompt
```python
def update_query(oxy_request: OxyRequest):
    user_query = oxy_request.get_query(master_level=True)
    current_query = oxy_request.get_query()
    oxy_request.set_query(
        f"user query is {user_query}\ncurrent query is {current_query}"
    )
    return oxy_request
```

In the code above, we merge `user_query` and `current_query` using the `update_query` method and set it as the new query content.

### Applying the Update Method to Agents

Then, you need to pass the `update_query` method to the Agent's input processing function `func_process_input`, so that each Agent can use the custom processing logic:

```python
oxy.ReActAgent(
    name="file_agent",
    desc="A tool that can operate the file system",
    tools=["file_tools"],
    func_process_input=update_query, # assuming you want file_agent to read the original file
),
oxy.ReActAgent(
    name="time_agent",
    desc="A tool that can get current time",
    tools=["time_tools"], # you can control the processing method for each agent
),
# ...
```
## Complete Runnable Example

Here is a complete runnable code example:

```python
import asyncio

from oxygent import MAS, oxy, Config, OxyRequest
import os
from oxygent import preset_tools

Config.set_agent_llm_model("default_llm")

def update_query(oxy_request: OxyRequest):
    user_query = oxy_request.get_query(master_level=True)
    current_query = oxy_request.get_query()
    oxy_request.set_query(
        f"user query is {user_query}\ncurrent query is {current_query}"
    )
    return oxy_request

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.01},
        semaphore=4,
        timeout=240,
    ),
    oxy.StdioMCPClient(
        name="time_tools",
        params={
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
        },
    ),
    preset_tools.file_tools,
    oxy.ReActAgent(
        name="file_agent",
        desc="A tool that can operate the file system",
        tools=["file_tools"],
        func_process_input=update_query,
    ),
    oxy.ReActAgent(
        name="time_agent",
        desc="A tool that can get current time",
        tools=["time_tools"],
    ),
    oxy.ChatAgent(
        name="text_summarizer",
        desc="A tool that can summarize markdown text",
        prompt="You are a text summarizer. Please provide a concise summary of the given text.",
        func_process_input=update_query,
    ),
    oxy.ChatAgent(
        name="data_analyser",
        desc="A tool that can summarize echart data",
        prompt="You are a data analyst. Please analyze the given data and provide insights.",
        func_process_input=update_query,
    ),
    oxy.ChatAgent(
        name="document_checker",
        desc="A tool that can find problems in document",
        prompt="You are a document checker. Please review the document and identify any issues.",
        func_process_input=update_query,
    ),
    oxy.ParallelAgent(
        name="analyzer",
        desc="A tool that analyze markdown document",
        permitted_tool_name_list=["text_summarizer", "data_analyser", "document_checker"],
        func_process_input=update_query,
    ),
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        sub_agents=["file_agent","time_agent","analyzer"],
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello!"
        )


if __name__ == "__main__":
    asyncio.run(main())
```

[Previous: Providing Response Metadata](./trust-mode.md)
[Next: Handling LLM and Agent Output](./handle-output.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Single Agent Example](../../examples/agents/demo_single_agent.md) -- Demonstrates the basic usage of func_process_input
