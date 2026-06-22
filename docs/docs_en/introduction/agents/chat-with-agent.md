# How to Chat with an Agent?

OxyGent supports multiple ways to interact with agents.

## 1. Visual Interface

If you have set up an agent system, the simplest way is to use `start_web_service` to launch the [official visual tool](../backend/debugging.md). You can chat with agents using the chat box, just like mainstream AI product clients.

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello!" # default content in the chat box
        )
```

## 2. Command Line

Alternatively, if you prefer using the command line for interaction, you can use `start_cli_mode` to start your agent.
```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_cli_mode(
            first_query="Hello!" # default content in the chat box
        )
```

If you only want a single round of interaction with the agent, you can use `chat_with_agent` and pass the conversation content via `payload`:

```python
async def test():
    async with MAS(oxy_space=oxy_space) as mas:
        out = await mas.chat_with_agent(payload={"query": "The 30 positions of pi."})
        print("output:", out.output)
```

You can also use the `call` method to interact with any specific agent:

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "hello"},
        ]
        result = await mas.call(callee="master_agent", arguments={"messages": messages})
        print(result)
```

If you want to develop with OxyGent, you can also use other more advanced and customizable approaches, such as directly editing conversation data:

```python
# find in ollama_demo.py
async def chat():
    async with MAS(oxy_space=oxy_space) as mas:
        history = [{"role": "system", "content": "You are a helpful assistant."}]

        while True:
            user_in = input("User: ").strip()
            if user_in.lower() in {"exit", "quit", "q"}:
                break

            history.append({"role": "user", "content": user_in})
            result = await mas.call(
                callee="master_agent",
                arguments={"query": history},
            )
            assistant_out = result
            print(f"Assistant: {assistant_out}\n")
            history.append({"role": "assistant", "content": assistant_out})

if __name__ == "__main__":
    asyncio.run(chat())
```

You can read the source code for more information.

[Previous: Create Your First Agent](./create-agent.md)
[Next: Select the LLM for Your Agent](./select-llm.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Single Agent Example](../../examples/agents/demo_single_agent.md) -- The simplest ChatAgent configuration
- [Streaming Chat Agent Example](../../examples/agents/demo_chat_agent_stream.md) -- ChatAgent with streaming output
- [Ollama Local Model Example](../../examples/llms/demo_ollama.md) -- Interact with Ollama models via command line
- [MAS Launch Example](../../examples/backend/demo_launch_mas.md) -- Multiple ways to launch MAS
