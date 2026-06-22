# OxyGent API Reference

> Detailed class documentation for all OxyGent components. Each page includes parameters, methods, inheritance hierarchy, and usage examples.

## Agents
---
+ [BaseOxy](./agent/base_oxy.md) — The universal base class for all OxyGent components
+ [BaseFlow](./agent/base_flow.md) — Base class for execution flows
+ [BaseAgent](./agent/base_agent.md) — Base class for all agents
+ [LocalAgent](./agent/local_agent.md) — Agent that runs locally with an LLM
+ [ChatAgent](./agent/chat_agent.md) — Single-turn conversational agent
    + [RAGAgent](./agent/rag_agent.md) — Retrieval-augmented generation agent
+ [ReActAgent](./agent/react_agent.md) — Reasoning + Acting loop with tool calling
    + [ShellUseAgent](./agent/shell_use_agent.md) — SSH remote command execution
    + [SkillAgent](./agent/skill_agent.md) — Dynamically loaded skill agent
+ [ParallelAgent](./agent/parallel_agent.md) — Parallel sub-task execution
+ [WorkflowAgent](./agent/workflow_agent.md) — Custom step-by-step workflows
+ [PlanAndSolveAgent](./agent/plan_and_solve_agent.md) — Plan first, then execute
+ [RemoteAgent](./agent/remote_agent.md) — Connect to agents in other processes
    + [SSEOxyGent](./agent/sse_oxy_agent.md) — SSE-based distributed agent
    + [A2AClientAgent](./agent/a2a_client_agent.md) — A2A protocol client agent

## Tools
---
+ [BaseTool](./tools/base_tools.md) — Base class for all tools
+ [HttpTool](./api_tools/http_tool.md) — HTTP API wrapper tool
+ [FunctionTool](./function_tools/function_tool.md) — Single Python function as a tool
+ [FunctionHub](./function_tools/function_hub.md) — Collection of Python function tools
+ [MCPTool](./tools/mcp_tool.md) — MCP protocol tool wrapper
+ [BaseMCPClient](./tools/base_mcp_client.md) — Base MCP client
    + [StdioMCPClient](./tools/stdio_mcp_client.md) — MCP over stdio transport
    + [SSEMCPClient](./tools/sse_mcp_client.md) — MCP over SSE transport
    + [StreamableMCPClient](./tools/streamable_mcp_client.md) — MCP over Streamable HTTP
+ [BaseBank](./bank_tools/base_bank.md) — Base class for tool banks
    + [BankTool](./bank_tools/bank_tool.md) — Server-side tool bank
    + [BankClient](./bank_tools/bank_client.md) — Client for remote tool banks

## Preset Tools
---
+ [Preset Tools (10 FunctionHub collections)](./preset_tools.md) — Built-in tools: file, math, time, shell, python, http, image_gen, ssh, string, system

## Flows
---
+ [WorkFlow](./flows/workflow.md) — Sequential step execution
+ [ParallelFlow](./flows/parallel_flow.md) — Concurrent step execution
+ [PlanAndSolve](./flows/plan_and_solve.md) — Decompose → plan → solve
+ [Reflexion (+ MathReflexion)](./flows/reflexion.md) — Self-reflection and retry loop

## LLM
---
+ [BaseLLM](./llms/base_llm.md) — Base class for all LLM integrations
+ [RemoteLLM](./llms/remote_llm.md) — Base for remote API-based LLMs
    + [HttpLLM](./llms/http_llm.md) — Call models via HTTP API
    + [OpenAILLM](./llms/openai_llm.md) — Call models via OpenAI SDK
+ [LocalLLM](./llms/local_llm.md) — Load HuggingFace models locally
+ [MockLLM](./llms/mock_llm.md) — Mock model for testing

## Database
---
+ [BaseDB](./databases/base_db.md) — Base database interface
+ [BaseES](./databases/db_es/base_es.md) — Elasticsearch base
    + [JesES](./databases/db_es/jes_es.md) — JD Elasticsearch
    + [LocalES](./databases/db_es/local_es.md) — File-based local ES fallback
    + [MemoryEs](./databases/db_es/memory_es.md) — In-memory ES for testing
+ [BaseRedis](./databases/db_redis/base_redis.md) — Redis base
    + [JimdbApRedis](./databases/db_redis/jimdb_ap_redis.md) — JD Redis
    + [LocalRedis](./databases/db_redis/local_redis.md) — File-based local Redis fallback
+ [BaseVectorDB](./databases/db_vector/base_vector_db.md) — Vector database base
    + [VearchDB](./databases/db_vector/vearch_db.md) — Vearch vector DB

## Schemas
---
+ [OxyRequest / OxyResponse / OxyState](./schemas/oxy.md) — Core request/response types
+ [LLMState / LLMResponse](./schemas/llm.md) — LLM interaction types
+ [Message / Memory](./schemas/memory.md) — Conversation history and memory
+ [Observation / ExecResult](./schemas/observation.md) — Tool execution results
+ [SkillMetadata](./schemas/skill.md) — Skill definition metadata
+ [Evaluation (Rating models)](./schemas/evaluation.md) — Rating and evaluation types

## MAS System Modules
---
+ [Config](./config.md) — Global configuration singleton
+ [MAS](./mas.md) — Multi-Agent System runtime container
+ [DBFactory](./db_factory.md) — Database connection factory
+ [EmbeddingCache](./embedding_cache.md) — Embedding vector cache
+ [OxyFactory](./oxy_factory.md) — Component factory for deserialization

## Live Prompt
---
+ [Live Prompt](./live_prompt.md) — PromptManager, PromptOptimizer, VersionSync, DynamicAgentManager

## Transport
---
+ [A2A Protocol](./transport_a2a.md) — A2AServerGateway, A2AInMemoryStore
