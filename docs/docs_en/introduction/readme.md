# OxyGent Tutorial

> This tutorial series guides you through building multi-agent systems (MAS) with OxyGent step by step.
> If you are new to OxyGent, we recommend reading the documents in order, especially those marked with *.

---

## Getting Started

| Document | Description |
|----------|-------------|
| [Install OxyGent](./getting-started/install.md)* | Environment setup and installation |
| [Run the Demo](./getting-started/demo.md)* | Quick-start demo |
| [Configuration](./getting-started/config.md)* | Configure LLM, Agent, Server, and more |

## Agents

| Document | Description |
|----------|-------------|
| [Create Your First Agent](./agents/create-agent.md)* | Register an LLM and Agent |
| [Chat with an Agent](./agents/chat-with-agent.md) | Web UI, CLI, batch processing, API calls |
| [Select an LLM](./agents/select-llm.md) | HttpLLM, OpenAILLM, LocalLLM, MockLLM |
| [Preset Prompts](./agents/select-prompt.md) | Customize and append prompts |
| [Agent Types](./agents/agent-types.md) | ChatAgent, ReActAgent, WorkflowAgent, and more |
| [Live Prompt Management](./agents/live-prompts.md) | Hot-reload prompts at runtime |

## Tools

| Document | Description |
|----------|-------------|
| [Register a Local Tool](./tools/register-tool.md)* | FunctionHub tool registration |
| [Use Open-Source MCP Tools](./tools/opensource-mcp-tools.md)* | Integrate community MCP tools |
| [Use Custom MCP Tools](./tools/custom-mcp-tools.md)* | Stdio / SSE / Streamable MCP |
| [Manage Tool Invocations](./tools/manage-tools.md) | Tool retrieval and access control |
| [Document Tools Guide](./tools/document-tools.md) | Document parsing and processing tools |

## Multi-Agent Systems

| Document | Description |
|----------|-------------|
| [Create a Multi-Agent System](./multi-agent/multi-agent-system.md)* | Master-sub agent architecture |
| [Mixture of Agents](./multi-agent/mixture-of-agents.md) | Multi-agent aggregated decision-making |
| [Parallel Execution](./multi-agent/parallel.md)* | ParallelAgent concurrent execution |
| [Distributed Systems](./multi-agent/distributed.md)* | SSEOxyGent cross-process communication |

## Advanced Features

| Document | Description |
|----------|-------------|
| [Response Metadata](./advanced/trust-mode.md) | Trust Mode structured metadata output |
| [Process Input](./advanced/process-input.md)* | func_process_input hook |
| [Handle LLM Output](./advanced/handle-output.md) | func_parse_llm_response hook |
| [Reflexion Pattern](./advanced/reflexion.md) | Reflexion / MathReflexion workflows |
| [Create a Workflow](./advanced/workflow.md)* | Custom execution flows with Workflow |
| [Preset Flows](./advanced/preset-flows.md) | PlanAndSolve, Reflexion, and built-in flows |
| [Memory and Regeneration](./advanced/continue-exec.md) | Historical context and re-execution |
| [Multimodal Agents](./advanced/multimodal.md)* | Image, video, and other multimodal inputs |
| [RAG (Retrieval-Augmented Generation)](./advanced/rag.md)* | External knowledge retrieval and injection |
| [Generate Training Data](./advanced/training.md)* | Automated SFT data generation |

## Backend Services & Debugging

| Document | Description |
|----------|-------------|
| [Database Setup](./backend/database.md) | Elasticsearch / Redis configuration |
| [Global Data](./backend/global-data.md) | MAS-level shared data |
| [Web API](./backend/web-api.md) | FastAPI endpoints and SSE streaming |
| [Rating API](./backend/rating-api.md) | Conversation rating and feedback |
| [Visual Debugging](./backend/debugging.md) | Web UI debugging tools |

## A2A Protocol

| Document | Description |
|----------|-------------|
| [A2A Quick Start](./a2a/demo-guide.md) | A2A server and client examples |
| [A2A Design & Capabilities](./a2a/design.md) | A2A protocol architecture and interop |

---

> For more hands-on examples, see the [Examples Documentation](../examples/readme.md).
