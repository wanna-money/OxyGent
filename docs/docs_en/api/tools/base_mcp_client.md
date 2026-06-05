# BaseMCPClient
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

`BaseMCPClient` is the base client for Model Context Protocol (MCP) servers. It provides a foundation for connecting to and interacting with MCP servers, handling server lifecycle management, tool discovery, dynamic tool registration, and tool execution through the MCP protocol.

## Parameters


| Parameter                 | Type / Allowed value | Default                               | Description                                                        |
| ------------------------- | -------------------- | ------------------------------------- | ------------------------------------------------------------------ |
| `included_tool_name_list` | `list`               | `[]`                                  | Tool names discovered and registered from the MCP server.          |
| `headers`                 | `dict[str, str]`     | `{}`                                  | Extra HTTP headers for server communication.                       |
| `is_dynamic_headers`      | `bool`               | `False`                               | Whether to rebuild HTTP headers on each call from request context. |
| `is_inherit_headers`      | `bool`               | `False`                               | Whether to inherit HTTP headers from the parent request.           |
| `is_keep_alive`           | `bool`               | `Config.get_tool_mcp_is_keep_alive()` | Whether to reuse the MCP connection across tool calls.             |

## Methods


| Method                       | Coroutine (async) | Return Value  | Purpose (concise)                                                     |
| ---------------------------- | ----------------- | ------------- | --------------------------------------------------------------------- |
| `list_tools()`               | Yes               | `None`        | Discover and register tools from the MCP server.                      |
| `add_tools(tools_response)`  | No                | `None`        | Register `MCPTool` instances dynamically from the server's tool list. |
| `_execute(oxy_request)`      | Yes               | `OxyResponse` | Execute a tool call through the MCP server.                           |
| `cleanup()`                  | Yes               | `None`        | Clean up MCP server resources and connections.                        |

## Inherited
 Please refer to the [BaseTool](./base_tools.md) class for inherited parameters and methods.

## Usage

The class `BaseMCPClient` must be inherited.
