# OxyGent Examples

This directory contains documentation for all OxyGent example scripts, organized by feature area. Each subdirectory covers a specific aspect of the framework with runnable, self-contained examples.

---

## Start Here

If you're new to OxyGent, try these three examples first:

| Example | What You'll Learn |
|---------|------------------|
| [Single Agent](./agents/demo_single_agent.md) | Minimal ChatAgent with custom prompts and hooks |
| [ReAct Agent with Tools](./agents/demo_react_agent.md) | ReActAgent with reflexion and tool calling |
| [Hierarchical Multi-Agent](./agents/demo_hierarchical_agents.md) | Master-sub agent architecture and delegation |

---

## Categories

| Category | Examples | Description |
| -------- | :------: | ----------- |
| [Agents](./agents/readme.md) | 14 | Agent types, collaboration patterns, and callback hooks |
| [Advanced](./advanced/readme.md) | 9 | Advanced features: RAG, SFT data generation, skill recall, evaluation |
| [Backend](./backend/readme.md) | 14 | Web service modes, SSE streaming, async chat, batch processing |
| [A2A](./a2a/readme.md) | 20 | Agent-to-Agent protocol: servers, clients, streaming, multi-agent |
| [Tools](./tools/readme.md) | 4 | Tool types: FunctionTool, HttpTool, and tool retrieval |
| [LLMs](./llms/readme.md) | 4 | LLM integrations: HttpLLM, OpenAILLM, LocalLLM, MockLLM |
| [Flows](./flows/readme.md) | 2 | Flow orchestration: Reflexion and MathReflexion |
| [Banks](./banks/readme.md) | 4 | BankTool / BankClient: remote tool serving over HTTP |
| [MCP Tools](./mcp_tools/readme.md) | 3 | MCP protocol tool integration (Stdio, SSE, Streamable) |
| [Distributed](./distributed/readme.md) | 3 | Distributed multi-agent systems with SSEOxyGent |
| [Ecommerce](./ecommerce/readme.md) | 5 | E-commerce domain: product search, order tracking, customer service |
| [Live Prompts](./live_prompts/readme.md) | 2 | Hot-reload prompt management and dynamic agent updates |
| [FH Tools](./fh_tools/readme.md) | 1 | FunctionHub tool collections |
| [Application](./application/readme.md) | 1 | Full application examples |
| [Other](./other/readme.md) | 1 | Miscellaneous examples |

---

## Getting Started

1. Install OxyGent and its dependencies (see the main README).
2. Set the required environment variables in a `.env` file:
   ```
   DEFAULT_LLM_API_KEY=your_api_key
   DEFAULT_LLM_BASE_URL=your_base_url
   DEFAULT_LLM_MODEL_NAME=your_model_name
   ```
3. Run any example directly:
   ```bash
   python -m examples.agents.demo_single_agent
   ```
