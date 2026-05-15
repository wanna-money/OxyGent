# OxyGent Conceptual Overview

OxyGent is an open-source Python multi-agent system (MAS) framework. It unifies LLMs, Agents, Tools, and Flows into modular "Oxy" components that are assembled together via name-based references, helping you rapidly build, run, and iterate on multi-agent systems.

---

## Core Concepts

### oxy_space: The Component List

`oxy_space` is a Python list containing all the components in the system -- LLMs, Agents, and Tools. Each component has a `name`, and components reference each other by name rather than by Python object reference.

```python
oxy_space = [
    oxy.HttpLLM(name="default_llm", ...),        # LLM component
    oxy.StdioMCPClient(name="time_tools", ...),   # Tool component
    oxy.ReActAgent(name="master_agent", ...,       # Agent component
        tools=["time_tools"],                       # Reference tools by name
        llm_model="default_llm",                    # Reference LLM by name
        is_master=True,
    ),
]
```

### MAS: The Runtime Container

`MAS` (Multi-Agent System) is OxyGent's runtime container. It receives `oxy_space`, registers all components internally, establishes references between them, and offers multiple ways to start:

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service()          # Web UI + API server
    # or
    await mas.start_cli_mode()             # Command-line interaction
    # or
    result = await mas.chat_with_agent(    # Programmatic invocation
        payload={"query": "Hello"}
    )
```

### is_master: The Entry Agent

The agent with `is_master=True` is the entry point for user queries. User messages first arrive at the master agent, which decides whether to answer directly or delegate to sub-agents or tools. A MAS can have only one master agent.

### Component Types

```
Oxy (base class)
├── LLM (Large Language Model)
│   ├── HttpLLM         — Call cloud models via HTTP API
│   ├── OpenAILLM       — Call compatible models using OpenAI SDK
│   ├── LocalLLM        — Load HuggingFace models locally
│   └── MockLLM         — Mock model for testing
├── Agent
│   ├── ChatAgent       — Basic conversation (single LLM call)
│   ├── ReActAgent      — Reason-act loop (with tool calling)
│   ├── WorkflowAgent   — Custom workflows
│   ├── ParallelAgent   — Parallel sub-task execution
│   ├── PlanAndSolveAgent — Plan first, then execute
│   ├── RAGAgent        — Retrieval-augmented generation
│   ├── ShellUseAgent   — SSH remote command execution
│   ├── SkillAgent      — Dynamically loaded skills
│   └── SSEOxyGent      — Connect to remote distributed agents
└── Tool
    ├── FunctionHub      — Python function tool collections
    ├── StdioMCPClient   — MCP stdio tools
    ├── SSEMCPClient     — MCP SSE tools
    └── StreamableMCPClient — MCP Streamable tools
```

---

## Glossary

| Term | Description |
|------|-------------|
| oxy_space | Python list containing all components (LLMs, Agents, Tools) |
| MAS | Multi-Agent System -- the runtime container that manages the lifecycle of all components |
| is_master | Marks the entry agent that receives user queries |
| OxyRequest | Request object passed between components, carrying query content, context, shared data, etc. |
| OxyResponse | Response object containing output results and state |
| trace_id | Trace identifier that marks a complete conversation or task chain |
| sub_agents | List of sub-agents that the master agent can dispatch |
| tools | List of tool names available to an agent |
| llm_model | Name of the LLM used internally by an agent |
| semaphore | Concurrency control semaphore that limits simultaneous requests |
| FunctionHub | Container that registers Python functions as tools |
| StdioMCPClient | Connects to external tool servers via stdio protocol |
| preset_tools | OxyGent's built-in tool set (file, math, time, shell, etc.) |

---

## Minimal Working Example

```python
import asyncio, os
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
    ),
]

async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="Hello!")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## What's Next

- [Install OxyGent](./install.md) -- Set up the framework
- [Run the Demo](./demo.md) -- Quick start
- [Create Your First Agent](../agents/create-agent.md) -- Dive deeper

---

[Next: Install OxyGent](./install.md)
[Back to Home](../readme.md)
