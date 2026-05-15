# How to Configure Settings?

In OxyGent, you can use [Config](https://github.com/jd-opensource/OxyGent/blob/main/oxygent/config.py) to manage your custom settings.

## 1. Set the LLM Model

If multiple Agents use the same LLM, you can conveniently manage them by setting the LLM so that all Agents use the `llm_name` you specify:

```python
Config.set_agent_llm_model("default_llm")
```
## 2. Load Configuration

You can import a configuration file using the load method:

```python
Config.load_from_json("./config.json", env="default")
```
## 3. Set Model Parameters

You can set model parameters using the `Config.set_llm_config` method. For example, setting temperature, max tokens, and top-p:

```python
Config.set_llm_config(
    {
        "temperature": 0.2,
        "max_tokens": 2048,
        "top_p": 0.9,
    }
)
```

## 4. Set Log Format

You can configure logging details using `Config.set_log_config`, including the log path, log level, and colors:

```python
Config.set_log_config(
    {
        "path": "./cache_dir/demo.log",
        "level_root": "DEBUG",
        "level_terminal": "DEBUG",
        "level_file": "DEBUG",
        "color_is_on_background": True,
        "is_bright": True,
        "only_message_color": False,
        "color_tool_call": "MAGENTA",
        "color_observation": "GREEN",
        "is_detailed_tool_call": True,
        "is_detailed_observation": True,
    }
)
```
## 5. Set Agent Input Schema

You can set the agent's input schema using `Config.set_agent_input_schema`, defining input properties and required fields:

```python
Config.set_agent_input_schema(
    {
        "properties": {
            "query": {"description": "Query question"},
            "path": {"description": "File path to save the result"},
        },
        "required": ["query"],
    }
)
```

## 6. Set Output Format

You can set the output format using `Config.set_message_config`, deciding whether to send tool calls, observations, thinking processes, or final answers:

```python
Config.set_message_config(
    {
        "is_send_tool_call": False,
        "is_send_observation": False,
        "is_send_think": False,
        "is_send_answer": True,
    }
)
```

## Complete Runnable Example

Here is a complete runnable code example:

```python
import asyncio

from oxygent import MAS, oxy, Config
import os
import prompts
import tools

Config.set_agent_llm_model("default_llm")

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

[Previous: Managing Tool Calls](../tools/manage-tools.md)
[Next: Database Setup](../backend/database.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Config Setup Example](../../examples/backend/demo_config.md) -- Detailed usage of Config
- [Logger Setup Example](../../examples/backend/demo_logger_setup.md) -- Logging configuration examples
- [LLM Parameter Reset Example](../../examples/llms/demo_reset_llm_params.md) -- Dynamically setting LLM parameters
