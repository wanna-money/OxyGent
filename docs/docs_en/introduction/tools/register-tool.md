# How to Register a Local Tool?

In OxyGent, it is recommended to register local tools via [function hub](https://github.com/jd-opensource/OxyGent/blob/main/oxygent/oxy/function_tools/function_hub.py). You can also register tools using MCP. For details, refer to [Using Custom MCP Tools](./custom-mcp-tools.md) or [Using Open-Source MCP Tools](./opensource-mcp-tools.md).

## Step 1: Create a Tool File
First, create a new `tools.py` file and use `FunctionHub` to register a tool package:

```python
# in tools.py
import os
from pydantic import Field
from oxygent.oxy import FunctionHub

# Register tool package
file_tools = FunctionHub(name="file_tools")
```
## Step 2: Register Tools
Next, use the `@file_tools.tool()` decorator to register Python functions as tools. For example, you can register some basic file operation tools:

```python
# in tools.py
@file_tools.tool(
    description="Create a new file or completely overwrite an existing file with new content. Use with caution as it will overwrite existing files without warning. Handles text content with proper encoding. Only works within allowed directories."
)
def write_file(
    path: str = Field(description=""), content: str = Field(description="")
) -> str:
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)
    return "Successfully wrote to " + path

# other tools...
```
## Step 3: Add Tools to the Agent

Place the registered tools into the Agent's accessible scope. The Agent will automatically invoke the corresponding tools based on their descriptions:

```python
# in execute file
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
    tools.file_tools,
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        tools=["file_tools"],
        llm_model="default_llm",
    ),
]
```
## Complete Runnable Example

Below is a complete code example showing how to create tools and integrate them into an Agent:
```python
import asyncio

from oxygent import MAS, oxy
import os
import prompts
import tools

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
    tools.file_tools, # The entire tool package can be placed in oxy_space
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        tools=["file_tools"], # Add tools here
        llm_model="default_llm",
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
## Tool File Example

Below are some commonly used tools registered in the `tools.py` file:
```python
import os

from pydantic import Field

from oxygent.oxy import FunctionHub

file_tools = FunctionHub(name="file_tools")

@file_tools.tool(
    description="Create a new file or completely overwrite an existing file with new content. Use with caution as it will overwrite existing files without warning. Handles text content with proper encoding. Only works within allowed directories."
)
def write_file(
    path: str = Field(description=""), content: str = Field(description="")
) -> str:
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)
    return "Successfully wrote to " + path


@file_tools.tool(
    description="Read the content of a file. Returns an error message if the file does not exist."
)
def read_file(path: str = Field(description="Path to the file to read")) -> str:
    if not os.path.exists(path):
        return f"Error: The file at {path} does not exist."
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


@file_tools.tool(
    description="Delete a file. Returns a success message if the file is deleted, or an error if the file does not exist."
)
def delete_file(path: str = Field(description="Path to the file to delete")) -> str:
    if not os.path.exists(path):
        return f"Error: The file at {path} does not exist."
    os.remove(path)
    return f"Successfully deleted the file at {path}"

```

[Previous: Choosing an Agent Type](../agents/create-agent.md)
[Next: Using Open-Source MCP Tools](./opensource-mcp-tools.md)
[Back to Home](../readme.md)

---

## Related Examples

- [FunctionHub Tool Registration Example](../../examples/tools/demo_functionhub.md) -- Demonstrates how to register local tools using FunctionHub
- [Single Agent Example](../../examples/agents/demo_single_agent.md) -- Demonstrates basic usage of a single agent with tools
