# FunctionHub
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

`FunctionHub` is a central hub for registering and managing Python functions as tools. It provides a decorator-based interface for converting regular Python functions into executable tools, supporting both synchronous and asynchronous functions with automatic conversion.

## Parameters

| Parameter   | Type / Allowed value | Default | Description                                                                        |
| ----------- | -------------------- | ------- | ---------------------------------------------------------------------------------- |
| `func_dict` | `dict`               | `{}`    | Registry of functions and their metadata: `{name: (description, async_func)}`.     |

## Methods

| Method             | Coroutine (async) | Return Value | Purpose (concise)                                                                  |
| ------------------ | ----------------- | ------------ | ---------------------------------------------------------------------------------- |
| `init()`           | Yes               | `None`       | Create `FunctionTool` instances for all registered functions and register with MAS. |
| `tool(description)`| No                | `Callable`   | Decorator for registering functions as tools (supports sync and async).             |
| `cleanup()`        | Yes               | `None`       | Clean up resources including the thread pool.                                      |

## Inherited
 Please refer to the [BaseTool](../tools/base_tools.md) class for inherited parameters and methods.

## Usage

```python
file_tools = FunctionHub(name="file_tools")


@file_tools.tool(
    description="Create a new file or overwrite an existing file with new content."
)
def write_file(
    path: str = Field(description="File path"),
    content: str = Field(description="File content"),
) -> str:
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)
    return "Successfully wrote to " + path
```
