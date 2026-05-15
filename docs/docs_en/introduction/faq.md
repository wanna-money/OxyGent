# Frequently Asked Questions

---

### What is the difference between ChatAgent and ReActAgent?

**ChatAgent** makes a single LLM call per request. It has no tool access and no reasoning loop. Use it for simple Q&A, content generation, or as a building block inside larger systems.

**ReActAgent** implements a Reasoning + Acting loop. It can call tools, observe results, and iterate until it reaches an answer. Use it when the agent needs to take actions, look up information, or solve multi-step problems.

If you are unsure which to use, start with `ReActAgent` -- it can do everything `ChatAgent` does, plus tool calling.

---

### How do I choose between FunctionHub and MCP tools?

**FunctionHub** wraps Python functions as tools. They run in-process, have zero startup overhead, and are ideal for custom business logic.

**MCP tools** (Model Context Protocol) connect to external tool servers over stdio, SSE, or streamable HTTP. They support cross-language tools, community-published tool packages, and process isolation.

Rule of thumb:
- Writing a tool in Python for your own project? Use `FunctionHub`.
- Using a third-party tool server or need language-agnostic tools? Use MCP.

See [Register a Local Tool](./tools/register-tool.md) and [Use Custom MCP Tools](./tools/custom-mcp-tools.md) for details.

---

### Can I use OxyGent without Elasticsearch or Redis?

Yes. OxyGent uses local fallbacks automatically:
- **LocalEs** (file-based) or **MemoryEs** (in-memory) replaces Elasticsearch.
- **LocalRedis** (in-memory) replaces Redis.

No configuration is needed. OxyGent detects whether external databases are available and falls back gracefully. You can run a complete multi-agent system with zero infrastructure dependencies.

---

### What LLM providers are supported?

OxyGent supports any **OpenAI-compatible API** endpoint. This includes:
- OpenAI (GPT-4, GPT-4o, etc.)
- DeepSeek
- Qwen (Tongyi Qianwen)
- Anthropic (via compatible proxy)
- Any self-hosted model with an OpenAI-compatible API

OxyGent provides several LLM wrappers:

| Class | Use case |
|-------|----------|
| `HttpLLM` | Cloud models via HTTP API (most common) |
| `OpenAILLM` | Models via the OpenAI Python SDK |
| `LocalLLM` | HuggingFace models loaded locally |
| `MockLLM` | Deterministic responses for testing |

See [Select an LLM](./agents/select-llm.md) for configuration details.

---

### How do I deploy to production?

Use `start_web_service()` to launch OxyGent as a FastAPI server:

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(port=8080)
```

This gives you:
- `POST /sse/chat` for SSE streaming (recommended for production)
- `POST /chat` for synchronous responses
- `POST /async/chat` for async polling
- A built-in web UI

You can run the FastAPI app behind **nginx** or any reverse proxy. For distributed setups, use `SSEOxyGent` to connect agents across processes.

---

### How do I debug agent behavior?

Several options:

1. **Web UI debugger**: Launch with `start_web_service()` and use the built-in interface to inspect agent traces, tool calls, and reasoning steps.

2. **Logging**: Configure detailed logging via `Config.set_log_config()`:
   ```python
   Config.set_log_config({
       "level_terminal": "DEBUG",
       "is_detailed_tool_call": True,
       "is_detailed_observation": True,
   })
   ```

3. **Trace IDs**: Every request gets a `trace_id`. Use it to follow the complete execution chain across agents and tools.

4. **Message config**: Enable tool call and observation output:
   ```python
   Config.set_message_config({
       "is_send_tool_call": True,
       "is_send_observation": True,
       "is_send_think": True,
   })
   ```

See [Visual Debugging](./backend/debugging.md) for the full debugging guide.

---

### What is the difference between Workflow and Flow?

**BaseFlow** is the abstract base class for all execution patterns. Agents and flows both inherit from it.

**Workflow** is a specific flow type where you define a sequence of steps that execute in order. Each step can call a sub-agent, tool, or custom function.

Built-in flows include:
- **Workflow** -- user-defined step sequence
- **PlanAndSolve** -- LLM plans steps, then executes them
- **Reflexion** -- self-reflection and retry loop
- **MathReflexion** -- math-specific reflection with verification

See [Create a Workflow](./advanced/workflow.md) and [Preset Flows](./advanced/preset-flows.md).

---

### Can agents call other agents?

Yes. Use the `sub_agents` parameter to give an agent access to other agents:

```python
oxy.ReActAgent(
    name="master",
    is_master=True,
    sub_agents=["researcher", "writer"],
    llm_model="default_llm",
)
```

The master agent sees each sub-agent as a callable tool (using the sub-agent's `desc` field as the tool description). It decides when to delegate based on the query.

See [Create a Multi-Agent System](./multi-agent/multi-agent-system.md).

---

### How do I add memory and context?

OxyGent automatically manages **short-term memory** (recent conversation turns). You can configure its size:

```python
# Per agent
oxy.ChatAgent(name="agent", short_memory_size=10, ...)

# Globally
Config.set_agent_short_memory_size(10)
```

For **long-term memory**, use the storage layer (Elasticsearch) to persist traces and retrieve historical context. The `RAGAgent` can also retrieve external knowledge from vector databases.

See [Memory and Regeneration](./advanced/continue-exec.md) and [RAG](./advanced/rag.md).

---

### How do I connect agents across processes?

Use **SSEOxyGent** for distributed deployment. An `SSEOxyGent` acts as a proxy for a remote agent running in another process or machine:

```python
oxy.SSEOxyGent(
    name="remote_agent",
    desc="A remote agent running on another server",
    server_url="http://192.168.1.100:8080",
)
```

For cross-framework interoperability, use the **A2A protocol** (Agent-to-Agent). OxyGent can act as both an A2A server and client, enabling communication with agents built in LangChain, AgentScope, and other frameworks.

See [Distributed Systems](./multi-agent/distributed.md) and [A2A Quick Start](./a2a/demo-guide.md).

---

[Back to Home](./readme.md)
