# How to Use Live Prompts

OxyGent provides a live prompts feature that allows you to dynamically load and update agent prompts at runtime without restarting the application. This is ideal for scenarios that require frequent prompt adjustments.

## What Are Live Prompts

Live Prompts is a prompt management system stored in a database that supports:
- **Automatic integration**: Built-in support in LocalAgent, no additional configuration needed
- **Version management**: Saves prompt history versions, supports rollback
- **Fallback mechanism**: Automatically uses the default prompt in code when live prompts are unavailable
- **Flexible toggle**: Option to enable or disable the live prompt feature

## Basic Usage

### Method 1: Default Usage (Recommended)

Simply set the `prompt` parameter in the Agent, and the system will automatically use the live prompt feature:

```python
oxy.ReActAgent(
    name="time_agent",
    desc="A tool that can query the time",
    prompt="You are a time management assistant. Help users with time-related queries.",
    tools=["time_tools"],
    # use_live_prompt=True is the default, can be omitted
)
```

**How it works:**
1. When the Agent initializes, it automatically looks up a live prompt with the key `time_agent_prompt` from storage
2. If found and activated, the stored prompt is used
3. If not found, the `prompt` parameter in the code is used as a fallback

### Method 2: Custom prompt_key

If you want to use a different key name:

```python
oxy.ReActAgent(
    name="time_agent",
    desc="A tool that can query the time",
    prompt="Default prompt",
    prompt_key="my_custom_prompt_key",  # custom key name
    tools=["time_tools"],
)
```

### Method 3: Disable Live Prompt

If you don't need the live prompt feature (use static prompts only):

```python
oxy.ReActAgent(
    name="time_agent",
    desc="A tool that can query the time",
    prompt="You are a time management assistant.",
    tools=["time_tools"],
    use_live_prompt=False  # disable live prompt
)
```

## Parameter Reference

### LocalAgent Live Prompt Parameters

- **`prompt`** (str): Prompt content, used as a fallback
- **`prompt_key`** (str, optional): Key name for the live prompt
  - Default: `"{agent_name}_prompt"`
  - Used to look up the dynamic prompt from storage
- **`use_live_prompt`** (bool, optional): Whether to enable the live prompt feature
  - Default: `True`
  - When set to `False`, only the `prompt` parameter in the code is used

## Complete Example

Here is a complete example using live prompts:

```python
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
    preset_tools.time_tools,
    # Use the system default prompt
    oxy.ReActAgent(
        name="time_agent",
        desc="A tool that can query the time",
        prompt="You are a time management assistant. Help users with time-related queries.",
        tools=["time_tools"],
        use_live_prompt=False  # disable live prompt, and prompt is empty, so the system default prompt is used
    ),
    preset_tools.file_tools,

    # Use only the prompt defined in code
    oxy.ReActAgent(
        name="file_agent",
        desc="A tool that can operate the file system",
        tools=["file_tools"],
        prompt="You are a file system assistant. Help users with file operations safely and efficiently.",
        use_live_prompt=False # disable live prompt, use the prompt parameter in code
    ),
    preset_tools.math_tools,

    # Use live prompts
    oxy.ReActAgent(
        name="math_agent",
        desc="A tool that can perform mathematical calculations.",
        tools=["math_tools"],
        prompt="You are a math assistant. Help users with mathematical calculations.",
    ),
     # Use live prompts
    oxy.ReActAgent(
        is_master=True,
        name="master_agent",
        sub_agents=["time_agent", "file_agent", "math_agent"],
        prompt="You are the master agent. Coordinate the actions of your sub-agents effectively.",
    ),
]

async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="What time is it now? Please save it into time.txt."
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Hot-Reloading Prompts

After modifying prompts in storage, you need to manually trigger a hot reload for the changes to take effect:

### Method 1: Via Agent Instance

```python
# Get the agent instance
agent = mas.oxy_name_to_oxy["time_agent"]

# Hot reload the prompt
success = await agent.reload_prompt()
if success:
    print("Prompt has been updated")
```

### Method 2: Via Convenience Functions

```python
from oxygent.live_prompt.wrapper import (
    hot_reload_agent,       # reload by agent name
    hot_reload_prompt,      # reload by prompt_key
    hot_reload_all_prompts  # reload all agents
)

# Hot reload a single agent
await hot_reload_agent("time_agent")

# Hot reload all agents using a specific prompt_key
await hot_reload_prompt("time_agent_prompt")

# Hot reload all agents
await hot_reload_all_prompts()
```

### Method 3: Auto-Trigger on Save (Recommended)

Automatically trigger a hot reload in the prompt management platform's save API:

```python
from oxygent.live_prompt.manager import PromptManager
from oxygent.live_prompt.wrapper import hot_reload_prompt

# Save the prompt
await manager.save_prompt(
    prompt_key="time_agent_prompt",
    prompt_content="Updated prompt content..."
)

# Automatically trigger hot reload
await hot_reload_prompt("time_agent_prompt")
```

## Configuration Requirements

The live prompts feature requires a database connection:
- Supports Elasticsearch as the primary storage
- Automatically falls back to LocalEs (local file storage) when ES is unavailable
- Configure database connection parameters through the `Config` system

### Configuration Parameters

Add the following configuration to `config.json`:

```json
{
  "live_prompt": {
    "es_polling_interval": 2  // ES polling interval (seconds), default is 2
  }
}
```

**Parameter description**:
- **`es_polling_interval`**: ES polling interval in seconds
  - Default: `2`
  - Use case: Controls the delay of prompt synchronization between different instances in multi-instance deployments
  - Recommendation: Adjust based on actual needs; smaller values mean faster synchronization but increase ES query frequency

**Configure via code**:

```python
from oxygent import Config

# Set ES polling interval to 5 seconds
Config.set_live_prompt_es_polling_interval(5)

# Get the current configuration
interval = Config.get_live_prompt_es_polling_interval()
print(f"Current polling interval: {interval}s")
```

### Multi-Instance Deployment Requirements

**Important**: If using the live prompts feature in a multi-instance deployment environment, **Elasticsearch must be configured**.

The system automatically detects the synchronization mechanism based on configuration:

1. **ES Polling (Recommended)**:
   - Requirement: Remote Elasticsearch
   - Advantages: No additional components needed, based on existing ES storage
   - Latency: Default 2-second polling interval (configurable via `live_prompt.es_polling_interval`)

2. **No Synchronization Mechanism**:
   - When ES is locally configured or not configured
   - **Warning**: Cache inconsistency across instances, live_prompt is not recommended
   - Only suitable for single-instance deployments

## Notes

1. **Backward compatibility**: Existing code requires no modifications; live prompt is enabled by default
2. **Multi-instance deployment**:
   - Remote ES must be configured to ensure cache consistency
   - Without configuration, caches may be inconsistent across instances
3. **Performance considerations**:
   - Prompts are loaded from the database once during initialization, then cached
   - Agents with live prompt disabled perform slightly better (no database queries)
   - ES polling mode: Default 2-second delay (adjustable via `live_prompt.es_polling_interval`)
   - Smaller polling intervals mean faster synchronization but increase ES query load
4. **Error handling**: When the live prompt system is unavailable, the `prompt` parameter in code is automatically used, ensuring stable system operation
5. **Version management**: The system automatically saves prompt modification history, supporting version rollback
6. **Flexible control**: Live prompt can be individually enabled or disabled for each Agent

## FAQ

### Q1: How to disable the live prompt feature?
**A**: Set the `use_live_prompt=False` parameter.

### Q2: What is the default value of prompt_key?
**A**: `{agent_name}_prompt`. For example, if the Agent is named `time_agent`, the default `prompt_key` is `time_agent_prompt`.

### Q3: What happens if there is no prompt in storage?
**A**: The `prompt` parameter in the code is used as a fallback.

### Q4: Does live prompt affect performance?
**A**: The impact is minimal. The database is accessed only once during initialization, then the cache is used. If you have extremely high performance requirements, you can disable live prompt.

### Q5: How to ensure prompt synchronization in multi-instance deployments?
**A**: Remote Elasticsearch must be configured. The system will automatically synchronize via ES polling:
- ES polling: Default 2-second synchronization delay (configurable)
- Local configuration: Cannot synchronize across instances, a warning will be displayed

### Q6: How to know which synchronization mechanism is currently in use?
**A**: Check the log output at startup:
- `ES polling enabled for remote hosts: xxx` - Using ES polling
- `ES polling not available` - No synchronization mechanism (single instance only)
- `Starting ES polling with Xs interval` - Shows the current polling interval

### Q7: How to adjust the ES polling interval?
**A**: Through the following two methods:

**Method 1: Set in the configuration file**
```json
{
  "live_prompt": {
    "es_polling_interval": 5
  }
}
```

**Method 2: Set via code**
```python
from oxygent import Config
Config.set_live_prompt_es_polling_interval(5)
```

[Previous: Agent Types](./agent-types.md)
[Next: Register a Local Tool](../tools/register-tool.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Live Prompts Example](../../examples/live_prompts/demo_live_prompt.md) -- Complete usage example of live prompts
- [Live Prompts Demo](../../examples/live_prompts/demo.md) -- Live prompts quick start
- [Config Setup Example](../../examples/backend/demo_config.md) -- Configuration management example
