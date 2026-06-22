# What is A2A?

**A2A** (Agent-to-Agent) is an open protocol by Google for agent interoperability. It defines a standard way for AI agents built in different frameworks to discover each other, exchange messages, and collaborate on tasks -- even when they run in separate processes, languages, or organizations.

---

## Why A2A?

In practice, multi-agent systems are rarely built with a single framework. Your organization might use OxyGent for some agents, LangChain for others, and a partner might expose agents built with AgentScope. A2A provides a common protocol so these heterogeneous agents can work together without framework-specific integration code.

Key capabilities:
- **Agent discovery**: Agents expose an Agent Card at `/.well-known/agent.json` describing their capabilities.
- **Message exchange**: Standardized `message/send` and `message/stream` endpoints for synchronous and streaming communication.
- **Task management**: Track task state, cancel tasks, and resubscribe to streaming results.
- **Context continuity**: Link multiple tasks in a session using `context_id` and `reference_task_ids`.

### Core Concepts

| Concept | Description |
|---------|-------------|
| Agent Card | An agent's business card that describes its capabilities, skills, and communication endpoints, exposed at `/.well-known/agent.json` |
| Task | A unit of work representing the full lifecycle of a single interaction (submitted / in-progress / completed / failed, etc.) |
| Message | A communication unit exchanged between client and server |
| Artifact | An output produced during task execution |

### Workflow

```
┌──────────────┐                         ┌──────────────┐
│  Agent A     │  1. Discover Agent Card │  Agent B     │
│ (A2A Client) │ ──────────────────────► │ (A2A Server) │
│              │                         │              │
│              │  2. Send Message        │              │
│              │ ──────────────────────► │              │
│              │                         │ 3. Execute   │
│              │  4. Return Result /     │    Task      │
│              │     Stream Updates      │              │
│              │ ◄────────────────────── │              │
└──────────────┘                         └──────────────┘
```

1. **Discover**: The client fetches the server's Agent Card to learn about its capabilities.
2. **Send**: The client sends a request via `message/send` or `message/stream`.
3. **Execute**: The server receives the request and executes the task.
4. **Return**: The server returns results, supporting both synchronous responses and SSE streaming updates.

---

## How OxyGent Implements A2A

OxyGent supports A2A on both the server and client sides:

**Server** (`A2AServerGateway`): Exposes any OxyGent MAS as an A2A-compatible service. It acts as a protocol gateway -- incoming A2A requests are converted to internal MAS calls, and results are converted back to A2A responses. No changes to your agents are needed.

Any OxyGent MAS can enable A2A server capabilities with a single flag, exposing its internal agents to external A2A clients:

```python
async with MAS(oxy_space=oxy_space, enable_a2a_server=True) as mas:
    await mas.start_web_service()
```

MAS automatically generates an Agent Card and registers the A2A protocol endpoints. External clients can then discover and call the agents via `/.well-known/agent.json`.

**Client** (`A2AClientAgent`): Connects to any A2A-compatible server as a remote agent. It discovers the server's capabilities via the Agent Card, then sends requests using the standard A2A protocol.

```python
# Client: call an external A2A agent
oxy.A2AClientAgent(
    name="external_agent",
    desc="An agent running on another framework",
    server_url="http://partner-service:8080",
)
```

---

## Design Philosophy

OxyGent's A2A implementation follows a "protocol gateway" approach: A2A is not a new agent type, but rather a protocol adaptation layer. On the server side, A2A requests are translated into internal MAS calls; on the client side, A2A responses are translated into standard `OxyResponse` objects. This maximizes reuse of existing framework capabilities while minimizing integration overhead.

---

## Cross-Framework Interoperability

OxyGent's A2A implementation has been tested with:

- **AgentScope** -- OxyGent client calling AgentScope server, and vice versa
- **Google A2A SDK** -- Standard SDK calling OxyGent server (streaming and non-streaming)
- **LangChain / LangGraph** -- Via A2A protocol bridges

This means you can expose your OxyGent agents to any A2A-compatible framework, or consume external agents without writing custom integration logic.

---

## Further Reading

- [A2A Quick Start](../a2a/demo-guide.md) -- Server and client examples
- [A2A Design and Capabilities](../a2a/design.md) -- Protocol architecture and mapping details
- [A2AClientAgent API Reference](../../api/agent/a2a_client_agent.md) -- Full parameter reference
- [Distributed Systems](../multi-agent/distributed.md) -- Cross-process communication with SSEOxyGent

---

[Previous: What is MCP?](./what-is-mcp.md)
[Next: Create Your First Agent](../agents/create-agent.md)
[Back to Home](../readme.md)

---

## Related Examples

- [A2A Quick Start](../a2a/demo-guide.md) -- A2A server and client examples
- [Distributed Agent Example](../../examples/distributed/app_master_agent.md) -- SSEOxyGent distributed deployment
