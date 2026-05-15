# Quick Start

This section will get you running your first OxyGent agent in 5 minutes.

## Prerequisites

- Python 3.10+ installed
- OxyGent installed (see [Installation Guide](./install.md))
- An LLM API key (any OpenAI-compatible endpoint: OpenAI, DeepSeek, Qwen, etc.)

## Step 1: Set Environment Variables

Create a `.env` file in the project root (OxyGent loads it automatically on startup):

```
DEFAULT_LLM_API_KEY=your_api_key
DEFAULT_LLM_BASE_URL=your_base_url
DEFAULT_LLM_MODEL_NAME=your_model_name
```

Or export them directly in your terminal:

```bash
export DEFAULT_LLM_API_KEY="your_api_key"
export DEFAULT_LLM_BASE_URL="your_base_url"
export DEFAULT_LLM_MODEL_NAME="your_model_name"
```

> OxyGent uses `python-dotenv` to automatically load the `.env` file from the project root at startup.

## Step 2: Create and Run Your First Agent

Create a file called `my_first_agent.py`:

```python
import asyncio
import os

from oxygent import MAS, oxy

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    oxy.ChatAgent(
        name="my_agent",
        llm_model="default_llm",
        prompt="You are a helpful assistant.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        payload = {"query": "Hello! What can you do?"}
        oxy_response = await mas.chat_with_agent(payload=payload)
        print("LLM: ", oxy_response.output)


if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python my_first_agent.py
```

You should see output similar to:

```
LLM:  Hello! I'm a helpful assistant. I can answer questions, ...
```

## Step 3: Launch the Web UI

Replace `chat_with_agent` with `start_web_service` to launch the built-in web interface:

```python
import asyncio
import os

from oxygent import MAS, oxy

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    oxy.ChatAgent(
        name="my_agent",
        llm_model="default_llm",
        prompt="You are a helpful assistant.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello",
            welcome_message="Hi, I'm OxyGent. How can I assist you?",
        )


if __name__ == "__main__":
    asyncio.run(main())
```

After running, your browser will automatically open `http://127.0.0.1:8080`, where you can chat with your agent through the Web UI.

> To change the port, pass `port=8082` to `start_web_service`, or set it globally with `Config.set_server_port(8082)`.

## Step 4: Interactive CLI Mode

If you prefer chatting in the terminal, use `start_cli_mode`:

```python
import asyncio
import os

from oxygent import MAS, oxy

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    oxy.ChatAgent(
        name="my_agent",
        llm_model="default_llm",
        prompt="You are a helpful assistant.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_cli_mode(first_query="Hello")


if __name__ == "__main__":
    asyncio.run(main())
```

After running, you can keep typing questions in the terminal to chat with your agent. Type `reset` to start a new session.

## FAQ

### Why do I get a 404 error after starting?

Check that your environment variables are correctly configured. Different models may require different `base_url` formats. See [Selecting an LLM](../agents/select-llm.md) for details.

### How do I get help?

- Submit an issue on GitHub
- Browse the [full documentation](../readme.md)

---

[Previous: Install OxyGent](./install.md)
[Next: Configure Settings](../getting-started/config.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Single Agent Example](../../examples/agents/demo_single_agent.md) -- The simplest ChatAgent configuration
- [Ollama Local Model Example](../../examples/llms/demo_ollama.md) -- Using a locally deployed model with Ollama
- [Streaming Chat Agent Example](../../examples/agents/demo_chat_agent_stream.md) -- ChatAgent with streaming output
