# How to Run the Demo?

Use `python` to directly run any of our demos.

### Why Doesn't the System Start When I Run the Demo After Downloading?
---
OxyGent is only an agent system framework and does not provide LLM services by itself. Therefore, you need to set up your own LLM API in `.env`.
```bash
   export DEFAULT_LLM_API_KEY="your_api_key"
   export DEFAULT_LLM_BASE_URL="your_base_url"  # if you want to use a custom base URL
   export DEFAULT_LLM_MODEL_NAME="your_model_name"  
```
```bash
   # create a .env file
   DEFAULT_LLM_API_KEY="your_api_key"
   DEFAULT_LLM_BASE_URL="your_base_url"
   DEFAULT_LLM_MODEL_NAME="your_model_name"
```

### Why Do I Get a 404 Error When Running the Demo After Setting Environment Variables?
---
First, please check whether you have referenced any non-existent environment variables.
If that doesn't solve the problem, please refer to [About LLM API](../agents/select-llm.md).

### How to Get Help?
---
You can get help through the following channels:

+ Submit an issue on GitHub
+ Join the discussion group (see the README)
+ If you have an internal Slack workspace, contact the OxyGent Core team directly.

OxyGent will provide more comprehensive community services in the future.

[Previous: Install OxyGent](./install.md)
[Next: Create Your First Agent](../agents/create-agent.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Single Agent Example](../../examples/agents/demo_single_agent.md) -- The simplest ChatAgent configuration
- [Ollama Local Model Example](../../examples/llms/demo_ollama.md) -- Using a locally deployed model with Ollama
- [Streaming Chat Agent Example](../../examples/agents/demo_chat_agent_stream.md) -- ChatAgent with streaming output
