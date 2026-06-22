# Quickstart

> Build your first agent, add tools, and orchestrate multiple agents -- all in 5 minutes.

---

## Prerequisites

- **Python 3.10+** installed
- OxyGent installed (see [Installation Guide](./install.md))
- An LLM API key (any OpenAI-compatible endpoint: OpenAI, DeepSeek, Qwen, etc.)

## 1. Set Environment Variables

Create a `.env` file in the project root. OxyGent loads it automatically on startup via `python-dotenv`:

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

Any OpenAI-compatible endpoint works (OpenAI, DeepSeek, Qwen, etc.).

---

## 2. Your First Agent

Create a file called `quickstart.py`:

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
        name="assistant",
        is_master=True,
        llm_model="default_llm",
        prompt="You are a helpful assistant.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        response = await mas.chat_with_agent(payload={"query": "Hello! What can you do?"})
        print("Agent:", response.output)


if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python quickstart.py
```

Expected output:

```
Agent: Hello! I'm a helpful assistant. I can answer questions, help with writing, ...
```

Key points:

- `oxy_space` is the component list containing LLMs and Agents.
- Components reference each other by `name`, e.g. `llm_model="default_llm"`.
- `is_master=True` marks the entry-point agent -- user messages arrive here first.
- `MAS` is the runtime container; use `async with` to manage its lifecycle.

`ChatAgent` makes a single LLM call with no tool access. That is useful for simple Q&A, but real work usually requires tools.

---

## 3. Launch the Web UI

Replace `chat_with_agent` with `start_web_service` to launch the built-in web interface:

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello!",
            welcome_message="Hi, I'm OxyGent. How can I assist you?",
        )
```

Your browser opens `http://127.0.0.1:8080` automatically. You can chat with your agent through the Web UI.

> To change the port, pass `port=8082` to `start_web_service()`, or set it globally with `Config.set_server_port(8082)`.

MAS supports multiple launch modes:

| Mode | Method | Use case |
|------|--------|----------|
| Web Service | `start_web_service()` | Web UI + REST API |
| CLI | `start_cli_mode()` | Interactive terminal chat |
| Batch | `start_batch_processing(querys)` | Concurrent batch execution |
| Programmatic | `chat_with_agent(payload)` | Embed into application code |

---

## 4. Add a Tool

Create a `FunctionHub` with a calculator tool, then switch to `ReActAgent` so the agent can reason about when to call it.

```python
import asyncio
import os

from pydantic import Field
from oxygent import MAS, oxy
from oxygent.oxy import FunctionHub

calculator_hub = FunctionHub(name="calculator")


@calculator_hub.tool(description="Add two numbers together")
def add(
    a: float = Field(description="First number"),
    b: float = Field(description="Second number"),
) -> float:
    return a + b


@calculator_hub.tool(description="Multiply two numbers together")
def multiply(
    a: float = Field(description="First number"),
    b: float = Field(description="Second number"),
) -> float:
    return a * b


oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    calculator_hub,
    oxy.ReActAgent(
        name="math_agent",
        is_master=True,
        llm_model="default_llm",
        tools=["calculator"],
        prompt="You are a math assistant. Use the calculator tools to answer math questions.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        response = await mas.chat_with_agent(
            payload={"query": "What is 12.5 + 7.3, then multiply the result by 4?"}
        )
        print("Agent:", response.output)


if __name__ == "__main__":
    asyncio.run(main())
```

The `ReActAgent` follows a Reasoning + Acting loop: it thinks about what to do, calls a tool, observes the result, and repeats until it has an answer.

Expected output:

```
Agent: 12.5 + 7.3 = 19.8. Multiplied by 4, that gives 79.2.
```

Key points:
- `FunctionHub` groups Python functions into a named tool collection.
- The `@hub.tool(description=...)` decorator registers each function.
- The agent references tools by the hub's `name`, not individual function names.
- `ReActAgent` automatically decides which tool to call based on the query.

---

## 5. Multi-Agent System

Add a second agent and wire them together. The master agent decides when to delegate.

```python
import asyncio
import os

from pydantic import Field
from oxygent import MAS, oxy
from oxygent.oxy import FunctionHub

calculator_hub = FunctionHub(name="calculator")


@calculator_hub.tool(description="Add two numbers together")
def add(
    a: float = Field(description="First number"),
    b: float = Field(description="Second number"),
) -> float:
    return a + b


oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    calculator_hub,
    # Sub-agent: handles math
    oxy.ReActAgent(
        name="math_agent",
        desc="A math specialist. Delegates math questions to this agent.",
        llm_model="default_llm",
        tools=["calculator"],
        prompt="You are a math assistant. Use the calculator tools to answer math questions.",
    ),
    # Master agent: routes queries
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        llm_model="default_llm",
        sub_agents=["math_agent"],
        prompt="You are a helpful assistant. Route math questions to math_agent. Answer other questions directly.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        response = await mas.chat_with_agent(
            payload={"query": "What is 99 + 1?"}
        )
        print("Agent:", response.output)


if __name__ == "__main__":
    asyncio.run(main())
```

The master agent sees `math_agent` as a callable tool (via its `desc` field). When a math question arrives, the master dispatches it to `math_agent`, which uses the calculator, then returns the result.

Key points:
- Only one agent has `is_master=True`. That is the entry point for user queries.
- Sub-agents are referenced by name in the `sub_agents` list.
- The `desc` field tells the master agent what each sub-agent is for.

---

## Next Steps

You now have the core building blocks. Explore further:

- [Agent Types](../agents/agent-types.md) -- ChatAgent, ReActAgent, WorkflowAgent, ParallelAgent, and more
- [Register a Local Tool](../tools/register-tool.md) -- Advanced FunctionHub usage
- [Use MCP Tools](../tools/custom-mcp-tools.md) -- Connect to external tool servers
- [Multi-Agent Systems](../multi-agent/multi-agent-system.md) -- Master-sub agent architecture in depth
- [Distributed Systems](../multi-agent/distributed.md) -- Cross-process agent communication
- [Configuration](./config.md) -- Global settings, LLM defaults, logging

## FAQ

### Why do I get a 404 error after starting?

Check that your environment variables are correctly configured. Different models may require different `base_url` formats. See [Selecting an LLM](../agents/select-llm.md) for details.

### How do I get help?

- Submit an issue on GitHub
- Browse the [full documentation](../readme.md)

[Previous: Install OxyGent](./install.md)
[Next: Configuration](./config.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Single Agent Example](../../examples/agents/demo_single_agent.md) -- The simplest ChatAgent configuration
- [Ollama Local Model Example](../../examples/llms/demo_ollama.md) -- Using a locally deployed model with Ollama
- [Streaming Chat Agent Example](../../examples/agents/demo_chat_agent_stream.md) -- ChatAgent with streaming output
