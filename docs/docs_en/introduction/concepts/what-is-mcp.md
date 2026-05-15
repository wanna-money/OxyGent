# What is MCP?

**MCP** (Model Context Protocol) is an open protocol for connecting AI models to external tools and data sources. It defines a standard client-server interface so that any tool server can be used by any compatible AI agent, regardless of programming language or framework.

---

## Client-Server Architecture

MCP follows a client-server pattern:

```
┌──────────────┐    MCP Protocol  ┌──────────────┐
│  AI Framework│ ◄──────────────► │  MCP Server  │
│ (MCP Client) │                  │ (Tool Impl.) │
└──────────────┘                  └──────────────┘
```

- The **client** (your agent) discovers available tools, sends requests, and receives results.
- The **server** exposes tools via a standardized interface. Servers can be written in any language.

### Workflow

1. **Connect**: The MCP client starts and connects to the MCP server.
2. **Discover**: The client requests the server's tool list, obtaining each tool's name, description, and parameter schema.
3. **Call**: When the LLM decides to use a tool, the client sends the call request to the server.
4. **Return**: The server executes the tool and returns the result to the client.

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

### StdioMCPClient

Connects to a local MCP server by launching it as a subprocess:

```python
oxy.StdioMCPClient(
    name="file_tools",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "./data"],
    },
)
```

### SSEMCPClient

Connects to a remote MCP server via the SSE protocol:

```python
oxy.SSEMCPClient(
    name="remote_tools",
    params={"url": "http://mcp-server:8080/sse"},
)
```

### StreamableMCPClient

Connects to a remote MCP server via the Streamable HTTP protocol:

```python
oxy.StreamableMCPClient(
    name="remote_tools",
    params={"url": "http://mcp-server:8080/mcp"},
)
```

### Usage

Once an MCP client is registered in `oxy_space`, MAS automatically connects to the server, discovers its tools, and registers them during initialization. Agents can then use those tools simply by referencing the client name via the `tools` parameter:

```python
oxy_space = [
    oxy.HttpLLM(name="llm", ...),
    oxy.StdioMCPClient(name="file_tools", ...),
    oxy.ReActAgent(
        name="agent",
        is_master=True,
        tools=["file_tools"],
    ),
]
```

There is a large and growing ecosystem of open-source MCP servers available for common use cases such as file systems, databases, browsers, and search engines.

---

## Further Reading

- [Use Open-Source MCP Tools](../tools/opensource-mcp-tools.md) -- Integrate community tool servers
- [Use Custom MCP Tools](../tools/custom-mcp-tools.md) -- Build and connect your own MCP servers
- [MCP Tool API Reference](../../api/tools/mcp_tool.md) -- Full parameter reference
- [Register a Local Tool](../tools/register-tool.md) -- Alternative: Python-native FunctionHub tools

---

[Previous: What is ReAct?](./what-is-react.md)
[Next: What is A2A?](./what-is-a2a.md)
[Back to Home](../readme.md)

---

## Related Examples

- [MCP Tool Usage Example](../../examples/tools/demo_mcp.md) -- Demonstrates basic usage of MCP tools
- [MCP with Headers Example](../../examples/tools/demo_mcp_with_headers.md) -- Demonstrates how to configure custom request headers for MCP tools
