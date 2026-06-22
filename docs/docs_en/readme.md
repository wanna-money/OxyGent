# OxyGent Documentation

**OxyGent** is an open-source Python framework for building multi-agent systems. It unifies LLMs, Agents, Tools, and Flows into modular components that snap together by name, making it fast to build, run, and iterate on agent-based applications.

---

## Why OxyGent?

- **Agent loop built-in** — handles tool invocation, response parsing, and multi-turn reasoning automatically
- **Python-first** — define agents, tools, and flows as Python objects; no DSLs or config files required
- **10+ agent types** — ChatAgent, ReActAgent, WorkflowAgent, ParallelAgent, PlanAndSolveAgent, RAGAgent, and more
- **MCP protocol support** — connect to any MCP tool server (Stdio, SSE, Streamable) alongside native Python tools
- **Multi-agent orchestration** — hierarchical delegation, parallel execution, mixture-of-agents, and distributed systems
- **A2A interop** — built-in Agent-to-Agent protocol support for cross-framework communication (LangChain, LangGraph, AgentScope)
- **Web UI + API included** — FastAPI server with SSE streaming, built-in chat interface, and visual debugging
- **Production utilities** — tracing, conversation history, live prompt management, SFT data generation

---

## Hello World

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
        result = await mas.chat_with_agent(payload={"query": "Hello!"})
        print(result.output)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Choose Your Path

| Your Goal | Start Here |
|-----------|-----------|
| Build your first agent in 5 minutes | [Quickstart](./introduction/getting-started/quickstart.md) |
| Understand core concepts and terminology | [Conceptual Overview](./introduction/getting-started/overview.md) |
| Learn the architecture and class hierarchy | [Architecture Overview](./introduction/getting-started/architecture.md) |
| Add tools (Python functions) to your agent | [Register a Local Tool](./introduction/tools/register-tool.md) |
| Use MCP protocol tools | [Open-Source MCP Tools](./introduction/tools/opensource-mcp-tools.md) |
| Build a multi-agent system | [Multi-Agent System](./introduction/multi-agent/multi-agent-system.md) |
| Run agents in parallel | [Parallel Execution](./introduction/multi-agent/parallel.md) |
| Deploy as a web service | [Web API](./introduction/backend/web-api.md) |
| Connect agents across processes | [Distributed Systems](./introduction/multi-agent/distributed.md) |
| Interop with LangChain / LangGraph | [A2A Protocol](./introduction/a2a/demo-guide.md) |
| Generate SFT training data | [Training Data](./introduction/advanced/training.md) |

---

## Documentation Sections

| Section | Description |
|---------|-------------|
| [Tutorial](./introduction/readme.md) | Step-by-step guides from installation to advanced features |
| [API Reference](./api/readme.md) | Detailed class and method documentation |
| [Examples](./examples/readme.md) | 87 runnable example scripts organized by feature |
| [FAQ](./introduction/faq.md) | Common questions and answers |
