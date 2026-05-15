# StreamableMCPClient
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

`StreamableMCPClient` is an MCP client implementation using Streamable-HTTP transport. It extends `BaseMCPClient` to provide HTTP streaming connection capabilities for communicating with MCP servers.

## Parameters


| Parameter     | Type / Allowed value | Default | Description                                              |
| ------------- | -------------------- | ------- | -------------------------------------------------------- |
| `server_url`  | `AnyUrl`             | `""`    | URL of the MCP server's streamable-HTTP endpoint.        |
| `middlewares` | `List[Any]`          | `[]`    | Client-side MCP middlewares for request processing.      |

## Methods


| Method                                     | Coroutine (async) | Return Value | Purpose (concise)                                                         |
| ------------------------------------------ | ----------------- | ------------ | ------------------------------------------------------------------------- |
| `init(is_fetch_tools)`                     | Yes               | `None`       | Initialize the HTTP streaming connection to the MCP server.               |
| `call_tool(tool_name, arguments, headers)` | Yes               | `Any`        | Open a fresh streamable-HTTP connection and invoke the named tool.        |

## Inherited
 Please refer to the [BaseMCPClient](./base_mcp_client.md) class for inherited parameters and methods.

## Usage

```python
oxy.StreamableMCPClient(
    name="remote_tools",
    server_url="http://127.0.0.1:8000/mcp",
)
```
