# SSEMCPClient
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

`SSEMCPClient` is an MCP client implementation using Server-Sent Events (SSE) transport. It extends `BaseMCPClient` to provide MCP communication over SSE, enabling real-time, unidirectional communication from servers to clients.

## Parameters


| Parameter     | Type / Allowed value | Default | Description                                                      |
| ------------- | -------------------- | ------- | ---------------------------------------------------------------- |
| `sse_url`     | `AnyUrl`             | `""`    | The URL for the SSE connection to the MCP server.                |
| `middlewares` | `list[Any]`          | `[]`    | Client-side MCP middlewares to apply to the session.             |

## Methods


| Method                                     | Coroutine (async) | Return Value | Purpose (concise)                                                           |
| ------------------------------------------ | ----------------- | ------------ | --------------------------------------------------------------------------- |
| `init(is_fetch_tools)`                     | Yes               | `None`       | Initialize the SSE connection to the MCP server and discover tools.         |
| `call_tool(tool_name, arguments, headers)` | Yes               | `Any`        | Open a fresh SSE connection and invoke the named tool.                      |

## Inherited
 Please refer to the [BaseMCPClient](./base_mcp_client.md) class for inherited parameters and methods.

## Usage

```python
oxy.SSEMCPClient(
    name="math_tools",
    sse_url="http://127.0.0.1:8000/sse",
)
```
