# BankTool

---
The position of the class is:

```markdown
[Oxy](../agent/base_oxy.md)
├── [BaseFlow](../agent/base_flow.md)
├── [BaseLLM](../llms/base_llm.md)
└── [BaseTool](../tools/base_tools.md)
    ├── [HttpTool](../api_tools/http_tool.md)
    ├── [FunctionHub](../function_tools/function_hub.md)
    ├── [FunctionTool](../function_tools/function_tool.md)
    ├── [BaseMCPClient](../tools/base_mcp_client.md)
    └── [BaseBank](./base_bank.md)
        ├── [BankTool](./bank_tool.md)
        └── [BankClient](./bank_client.md)
```

---

## Introduction

`BankTool` represents a single tool exposed by a bank server. It inherits from `BaseBank` and implements `_execute()` to invoke the tool via HTTP. Instances are typically created dynamically by `BankClient.add_tools()` rather than manually.

## Parameters

| Parameter               | Type / Allowed value | Default | Description                                                          |
| ----------------------- | -------------------- | ------- | -------------------------------------------------------------------- |
| `server_url`            | `AnyUrl`             | `""`    | URL of the bank server endpoint for this tool.                       |
| `method`                | `Literal["GET", "POST"]` | `"GET"` | HTTP method used when invoking this tool.                        |
| `is_permission_required`| `bool`               | `True`  | Whether permission is required for execution.                        |
| `headers`               | `Dict[str, str]`     | `{}`    | Extra HTTP headers sent with requests.                               |
| `is_retrievable`        | `bool`               | `False` | Whether this tool can be discovered via vector search retrieval.     |

## Methods

| Method                  | Coroutine (async) | Return Value  | Purpose (concise)                                                     |
| ----------------------- | ----------------- | ------------- | --------------------------------------------------------------------- |
| `_execute(oxy_request)` | Yes               | `OxyResponse` | POST to `server_url` with `oxy_request.arguments` and return result.  |

## Inherited

Please refer to the [BaseBank](./base_bank.md) class for inherited parameters and methods.

## Usage

`BankTool` instances are usually created automatically by `BankClient`. Manual creation:

```python
oxy.BankTool(
    name="get_weather",
    desc="Get weather for a city",
    server_url="http://localhost:8000/tools/get_weather",
    method="POST",
    headers={"Authorization": "Bearer xxx"},
)
```
