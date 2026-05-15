# Frequently Asked Questions

---

### 1. What is the difference between ChatAgent and ReActAgent?

**ChatAgent** makes a single LLM call per request. It has no tool access and no reasoning loop. Use it for simple Q&A, content generation, or as a building block inside larger systems.

**ReActAgent** implements a Reasoning + Acting loop. It can call tools, observe results, and iterate until it reaches an answer. Use it when the agent needs to take actions, look up information, or solve multi-step problems.

If you are unsure which to use, start with `ReActAgent` -- it can do everything `ChatAgent` does, plus tool calling.

---

### 2. How do I choose between FunctionHub and MCP tools?

**FunctionHub** wraps Python functions as tools. They run in-process, have zero startup overhead, and are ideal for custom business logic.

```python
hub = oxy.FunctionHub(name="my_tools")

@hub.tool(description="Get weather")
def get_weather(city: str) -> str:
    return f"{city} sunny"
```

**MCP tools** (StdioMCPClient / SSEMCPClient / StreamableMCPClient) connect to external tool servers. They support cross-language tools, community-published tool packages (file systems, databases, browsers, etc.), and process isolation.

Rule of thumb: use `FunctionHub` for your own Python functions, use MCP for external services.

See [Register a Local Tool](./tools/register-tool.md) and [Use Custom MCP Tools](./tools/custom-mcp-tools.md) for details.

---

### 3. Can I use OxyGent without Elasticsearch or Redis?

**Yes.** OxyGent uses local fallbacks automatically when no external database is available:

- Elasticsearch -> `LocalEs` (file-based) or `MemoryEs` (in-memory)
- Redis -> `LocalRedis` (in-memory queue)

The local mode is fully sufficient for development and debugging. For production, it is recommended to configure Elasticsearch for conversation persistence and trace queries, and Redis for SSE message queuing.

---

### 4. What LLM providers are supported?

OxyGent supports any **OpenAI-compatible API** endpoint via `HttpLLM`. This includes:

- OpenAI (GPT-4o, GPT-4, GPT-3.5, etc.)
- DeepSeek
- Qwen (Tongyi Qianwen)
- Zhipu AI (GLM)
- Anthropic Claude (via compatible proxy)
- Any self-hosted open-source model (vLLM, Ollama, etc.)

OxyGent also provides:
- `OpenAILLM`: Uses the official OpenAI SDK with support for additional advanced features.
- `LocalLLM`: Loads HuggingFace models locally without needing an API.
- `MockLLM`: Returns fixed content for unit testing.

See [Select an LLM](./agents/select-llm.md) for configuration details.

---

### 5. How do I deploy to production?

Recommended steps:

1. **Configure external databases**: Set up Elasticsearch and Redis connections to ensure conversation persistence and reliable SSE message delivery.
2. **Use Config for configuration management**: Manage environment-specific parameters via `config.json` (`default` / `production`), and switch environments using the `APP_ENV` environment variable.
3. **Start the web service**: `start_web_service()` is built on FastAPI + Uvicorn and can be used directly in production.
4. **Reverse proxy**: Deploy Nginx or an API gateway in front to handle HTTPS, load balancing, etc.
5. **Monitoring and tracing**: Use the trace data stored in Elasticsearch for monitoring and alerting.

```python
# Production example
Config.load_from_json("config.json")  # Load configuration

async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(host="0.0.0.0", port=8080)
```

---

### 6. How do I debug agent behavior?

OxyGent provides multiple layers of debugging support:

- **Web UI debugger**: `start_web_service()` includes a built-in debug interface where you can inspect the agent's reasoning process, tool calls, and intermediate results in real time.
- **CLI mode**: `start_cli_mode()` provides interactive terminal sessions with logs printed directly to the console.
- **Logging system**: OxyGent has built-in structured logging that automatically records trace_id, inputs/outputs, latency, and other details for each execution.
- **Elasticsearch tracing**: With ES configured, all execution records can be queried and traced back in Elasticsearch.
- **MockLLM**: Use `MockLLM` to replace a real LLM and test your flows without consuming API quota.

See [Visual Debugging](./backend/debugging.md) for the full debugging guide.

---

### 7. What is the difference between Workflow and Flow?

**BaseFlow** is the abstract base class for all execution patterns. Agents and flows both inherit from it. It defines components that contain multi-step execution logic.

**Workflow** is a specific flow type where you define a sequence of steps that execute in order. It is suited for fixed-process scenarios such as "retrieve -> summarize -> format".

Built-in flows include:
- **PlanAndSolve** -- LLM plans steps, then executes them one by one.
- **Reflexion** -- self-reflection after execution; retries if unsatisfied.
- **MathReflexion** -- math-specific reflection with verification.

See [Create a Workflow](./advanced/workflow.md) and [Preset Flows](./advanced/preset-flows.md).

---

### 8. Can agents call other agents?

**Yes.** Use the `sub_agents` parameter to declare sub-agents. The master agent can invoke sub-agents during its reasoning process. Sub-agents can also have their own sub-agents and tools, forming a multi-level organizational structure.

```python
oxy_space = [
    oxy.ReActAgent(name="researcher", desc="Responsible for information retrieval", tools=["search_tools"]),
    oxy.ReActAgent(name="writer", desc="Responsible for content writing"),
    oxy.ReActAgent(
        name="master",
        is_master=True,
        sub_agents=["researcher", "writer"],
    ),
]
```

The master agent automatically decides which sub-agent to dispatch based on user intent. The sub-agent's `desc` field is the key factor in the master's dispatching decision.

See [Create a Multi-Agent System](./multi-agent/multi-agent-system.md).

---

### 9. How do I manage memory and context?

OxyGent provides multiple memory management mechanisms:

- **Short-term memory**: Conversation context for each turn is automatically maintained. Control the number of retained turns with `Config.set_agent_short_memory_size(n)`.
- **ReAct memory**: The reasoning chain (Thought/Action/Observation) in ReActAgent can be optionally retained or discarded via the `is_discard_react_memory` parameter.
- **Memory token control**: Use `memory_max_tokens` to limit context length and prevent exceeding the model's context window.
- **Shared data**: `OxyRequest.shared_data` is shared across all components in the same call chain, suitable for passing structured context.
- **Global data**: `MAS.global_data` is shared across all requests, suitable for storing global configuration or caches.
- **Continue execution**: Use `from_trace_id` to continue from a historical conversation, maintaining context continuity.

See [Memory and Regeneration](./advanced/continue-exec.md) and [RAG](./advanced/rag.md).

---

### 10. How do I connect agents across processes?

OxyGent provides two cross-process communication options:

#### SSEOxyGent (OxyGent internal protocol)

Use a remote OxyGent service as a local agent. The remote service exposes an SSE interface via `start_web_service()`, and the local side connects through `SSEOxyGent`.

```python
# Remote service (Process A)
async with MAS(oxy_space=[...]) as mas:
    await mas.start_web_service(port=8081)

# Local reference (Process B)
oxy_space = [
    oxy.SSEOxyGent(name="remote_agent", server_url="http://localhost:8081"),
    oxy.ReActAgent(name="master", is_master=True, sub_agents=["remote_agent"]),
]
```

#### A2AClientAgent (Google A2A protocol)

Connect to any external service that supports the A2A (Agent-to-Agent) protocol, enabling cross-framework interoperability.

```python
oxy_space = [
    oxy.A2AClientAgent(
        name="external_agent",
        server_url="http://external-service:8080",
    ),
    oxy.ReActAgent(name="master", is_master=True, sub_agents=["external_agent"]),
]
```

See [Distributed Systems](./multi-agent/distributed.md) and [A2A Quick Start](./a2a/demo-guide.md).

---

[Back to Home](./readme.md)
