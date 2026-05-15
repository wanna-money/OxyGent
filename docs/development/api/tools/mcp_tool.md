# MCPTool
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

`MCPTool` is an individual tool proxy for MCP server tools. It represents a specific tool discovered from an MCP server and acts as a lightweight proxy that delegates actual execution to the parent MCP client while providing the standard `BaseTool` interface.

## Parameters


| Parameter                | Type / Allowed value | Default | Description                                                        |
| ------------------------ | -------------------- | ------- | ------------------------------------------------------------------ |
| `is_permission_required` | `bool`               | `True`  | Whether the tool requires explicit permission before execution.    |
| `mcp_client`             | `Any`                | `None`  | Reference to the parent MCP client that handles actual execution.  |
| `server_name`            | `str`                | `""`    | Name of the MCP server that provides this tool.                    |

## Methods


| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                              |
| ----------------------- | ----------------- | ------------- | -------------------------------------------------------------- |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | Execute the MCP tool by delegating to the parent MCP client.   |

## Inherited
 Please refer to the [BaseTool](./base_tools.md) class for inherited parameters and methods.

## Usage

`MCPTool` instances are created automatically by `BaseMCPClient` during tool discovery. They are not typically instantiated directly.
