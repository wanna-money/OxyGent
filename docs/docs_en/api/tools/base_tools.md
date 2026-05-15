# BaseTool
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

`BaseTool` is the abstract base class for all tools in the OxyGent system. It provides common functionality for tool implementations including permission control, category identification, and execution timeout management. Tools are specialized Oxy instances that typically require permissions and have shorter timeout periods.

## Parameters

| Parameter                | Type / Allowed value | Default                       | Description                                   |
| ------------------------ | -------------------- | ----------------------------- | --------------------------------------------- |
| `is_permission_required` | `bool`               | `True`                        | Whether permission is required for execution. |
| `category`               | `str`                | `"tool"`                      | Tool category identifier.                     |
| `semaphore`              | `int`                | `Config.get_tool_semaphore()` | Concurrency limit for parallel tool calls.    |
| `timeout`                | `float`              | `Config.get_tool_timeout()`   | Execution timeout in seconds.                 |

## Methods

| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                                            |
| ----------------------- | ----------------- | ------------- | ---------------------------------------------------------------------------- |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | **Abstract** -- must be implemented by subclasses to perform the tool logic. |

## Inherited
 Please refer to the [Oxy](../agent/base_oxy.md) class for inherited parameters and methods.

## Usage

The class `BaseTool` must be inherited.
