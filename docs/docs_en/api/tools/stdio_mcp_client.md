# StdioMCPClient
---
The position of the class is:


```markdown
[Oxy](../agent/base_oxy.md)
├── [BaseFlow](../agent/base_flow.md)
├── [BaseLLM](../llms/base_llm.md)
└── [BaseTool](../tools/base_tools.md)
    ├── [MCPTool](../tools/mcp_tool.md)
    ├── [BaseMCPClient](../tools/base_mcp_client.md)
    │   ├── [StdioMCPClient](../tools/stdio_mcp_client.md)
    │   ├── [SSEMCPClient](../tools/sse_mcp_client.md)
    │   └── [StreamableMCPClient](../tools/streamable_mcp_client.md)
    ├── [HttpTool](../api_tools/http_tool.md)
    ├── [FunctionHub](../function_tools/function_hub.md)
    ├── [FunctionTool](../function_tools/function_tool.md)
    └── [BaseBank](../bank_tools/base_bank.md)
        ├── [BankTool](../bank_tools/bank_tool.md)
        └── [BankClient](../bank_tools/bank_client.md)
```

---

## Introduction

`StdioMCPClient` is an MCP client implementation that communicates with MCP servers through standard input/output streams. It spawns and manages external processes (like Node.js scripts or Python uvx packages) that act as MCP servers.

## Parameters


| Parameter | Type / Allowed value | Default | Description                                                              |
| --------- | -------------------- | ------- | ------------------------------------------------------------------------ |
| `params`  | `dict[str, Any]`     | `{}`    | Configuration parameters including `command`, `args`, and `env` values.  |

## Methods


| Method                           | Coroutine (async) | Return Value  | Purpose (concise)                                                    |
| -------------------------------- | ----------------- | ------------- | -------------------------------------------------------------------- |
| `init(is_fetch_tools)`           | Yes               | `None`        | Initialize the stdio connection to the MCP server process.           |
| `_ensure_directories_exist(args)`| Yes               | `None`        | Ensure required directories exist before starting MCP server.        |
| `call_tool(tool_name, arguments, headers)` | Yes      | `Any`         | Open a fresh stdio connection and invoke the named tool.             |
| `get_server_params()`            | Yes               | `StdioServerParameters` | Resolve and return the server parameters for stdio transport.  |

## Inherited
 Please refer to the [BaseMCPClient](./base_mcp_client.md) class for inherited parameters and methods.

## Usage

```python
oxy.StdioMCPClient(
    name="time_tools",
    params={
        "command": "uvx",
        "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
    },
)
```
