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

---

## How OxyGent Implements A2A

OxyGent supports A2A on both the server and client sides:

**Server** (`A2AServerGateway`): Exposes any OxyGent MAS as an A2A-compatible service. It acts as a protocol gateway -- incoming A2A requests are converted to internal MAS calls, and results are converted back to A2A responses. No changes to your agents are needed.

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

[Back to Concepts](.)
[Back to Home](../readme.md)
