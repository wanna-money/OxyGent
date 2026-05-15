# What is MCP?

**MCP** (Model Context Protocol) is an open protocol for connecting AI models to external tools and data sources. It defines a standard client-server interface so that any tool server can be used by any compatible AI agent, regardless of programming language or framework.

---

## Client-Server Architecture

MCP follows a client-server pattern:

```
Agent (MCP Client)  <---->  Tool Server (MCP Server)
```

- The **client** (your agent) discovers available tools, sends requests, and receives results.
- The **server** exposes tools via a standardized interface. Servers can be written in any language.

Communication happens over one of three transports:
- **stdio** -- The server runs as a subprocess. Communication is via stdin/stdout.
- **SSE** (Server-Sent Events) -- The server runs as a remote HTTP service.
- **Streamable HTTP** -- The server runs as a remote HTTP service with streaming support.

---

## Why Use MCP?

1. **Cross-language**: Tool servers can be written in Python, TypeScript, Go, Rust, or any language. The protocol is language-agnostic.
2. **Ecosystem**: A growing community publishes reusable MCP tool servers (filesystem, databases, APIs, browsers, etc.). You can use them without writing any tool code.
3. **Process isolation**: Tools run in a separate process. A buggy or slow tool cannot crash your agent.
4. **Composability**: One agent can connect to many MCP servers simultaneously, each providing different tools.

---

## How OxyGent Supports MCP

OxyGent provides three MCP client classes, one for each transport:

| Class | Transport | Use case |
|-------|-----------|----------|
| `StdioMCPClient` | stdio | Local tool servers launched as subprocesses |
| `SSEMCPClient` | SSE | Remote tool servers over HTTP (legacy) |
| `StreamableMCPClient` | Streamable HTTP | Remote tool servers with streaming |

Example using a stdio MCP server:

```python
oxy.StdioMCPClient(
    name="math_tools",
    params={
        "command": "uv",
        "args": ["--directory", "./mcp_servers", "run", "math_tools.py"],
    },
)
```

The MCP client automatically discovers all tools exposed by the server and makes them available to any agent that references it by name.

---

## Further Reading

- [Use Open-Source MCP Tools](../tools/opensource-mcp-tools.md) -- Integrate community tool servers
- [Use Custom MCP Tools](../tools/custom-mcp-tools.md) -- Build and connect your own MCP servers
- [MCP Tool API Reference](../../api/tools/mcp_tool.md) -- Full parameter reference
- [Register a Local Tool](../tools/register-tool.md) -- Alternative: Python-native FunctionHub tools

---

[Back to Concepts](.)
[Back to Home](../readme.md)
