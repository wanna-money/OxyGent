# HttpTool
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

`HttpTool` is a tool for making HTTP requests to external APIs and services. It supports configurable HTTP methods (GET, POST, PUT, DELETE, PATCH), headers, and default parameters with proper timeout handling.

## Parameters


| Parameter        | Type / Allowed value | Default | Description                                                     |
| ---------------- | -------------------- | ------- | --------------------------------------------------------------- |
| `method`         | `str`                | `"GET"` | HTTP method to use (GET, POST, PUT, DELETE, PATCH).             |
| `url`            | `str`                | `""`    | Target URL for the HTTP request.                                |
| `headers`        | `dict`               | `{}`    | HTTP headers to include in the request.                         |
| `default_params` | `dict`               | `{}`    | Default parameters that will be merged with request arguments.  |

## Methods


| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                                          |
| ----------------------- | ----------------- | ------------- | -------------------------------------------------------------------------- |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | Execute the HTTP request with merged parameters and timeout handling.      |

## Inherited
 Please refer to the [BaseTool](../tools/base_tools.md) class for inherited parameters and methods.

## Usage

```python
oxy.HttpTool(
    name="weather_api",
    desc="Query weather data from an external API",
    method="GET",
    url="https://api.example.com/weather",
    headers={"Authorization": "Bearer ${API_KEY}"},
    default_params={"units": "metric"},
)
```
