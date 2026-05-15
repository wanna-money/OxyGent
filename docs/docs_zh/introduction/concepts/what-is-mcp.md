# 什么是 MCP？

MCP（Model Context Protocol，模型上下文协议）是由 Anthropic 提出的开放协议，旨在为大语言模型提供一种标准化的方式来连接外部工具和数据源。

---

## 核心思想

在 MCP 出现之前，每个 AI 框架都有自己的工具接入方式，工具开发者需要为不同框架重复适配。MCP 定义了统一的客户端-服务端通信协议，让工具只需实现一次，就能被所有支持 MCP 的框架调用。

```
┌─────────────┐    MCP 协议    ┌─────────────┐
│   AI 框架    │ ◄──────────► │  MCP 服务器   │
│ （MCP 客户端）│               │ （工具实现）   │
└─────────────┘               └─────────────┘
```

### 工作流程

1. **连接**：MCP 客户端启动并连接到 MCP 服务器。
2. **发现**：客户端请求服务器的工具列表，获取每个工具的名称、描述和参数模式。
3. **调用**：当 LLM 决定使用某个工具时，客户端将调用请求发送给服务器。
4. **返回**：服务器执行工具并返回结果给客户端。

### 传输方式

MCP 支持多种传输协议：

| 传输方式 | 说明 | 适用场景 |
|----------|------|----------|
| Stdio | 标准输入/输出 | 本地工具，客户端启动服务器进程 |
| SSE | Server-Sent Events | 远程工具，通过 HTTP 长连接 |
| Streamable HTTP | 可流式 HTTP | 远程工具，更现代的 HTTP 传输 |

---

## OxyGent 的 MCP 支持

OxyGent 内置了三种 MCP 客户端，对应三种传输方式：

### StdioMCPClient

通过启动子进程连接本地 MCP 服务器：

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

通过 SSE 协议连接远程 MCP 服务器：

```python
oxy.SSEMCPClient(
    name="remote_tools",
    params={"url": "http://mcp-server:8080/sse"},
)
```

### StreamableMCPClient

通过 Streamable HTTP 协议连接远程 MCP 服务器：

```python
oxy.StreamableMCPClient(
    name="remote_tools",
    params={"url": "http://mcp-server:8080/mcp"},
)
```

### 使用方式

MCP 客户端注册到 `oxy_space` 后，MAS 初始化时会自动连接服务器、发现工具并注册。智能体通过 `tools` 参数引用即可使用：

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

社区已有大量开源 MCP 服务器可直接使用，涵盖文件系统、数据库、浏览器、搜索引擎等常见场景。

---

[返回首页](../readme.md)
