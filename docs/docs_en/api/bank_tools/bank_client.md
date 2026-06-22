# BankClient

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

`BankClient` connects to a remote bank server (a FastAPI application using `BankRouter`) and dynamically discovers and registers its tools as `BankTool` instances. During `init()`, it fetches the tool list from the server's `/list_banks` endpoint and registers each tool into the MAS runtime.

## Parameters

| Parameter                | Type / Allowed value | Default | Description                                             |
| ------------------------ | -------------------- | ------- | ------------------------------------------------------- |
| `server_url`             | `AnyUrl`             | `""`    | URL of the remote bank server.                          |
| `included_bank_name_list`| `list`               | `[]`    | Names of bank tools discovered from the server.         |
| `headers`                | `dict[str, str]`     | `{}`    | Extra HTTP headers sent with requests.                  |

## Methods

| Method                        | Coroutine (async) | Return Value | Purpose (concise)                                                                 |
| ----------------------------- | ----------------- | ------------ | --------------------------------------------------------------------------------- |
| `init()`                      | Yes               | `None`       | Connect to bank server, fetch tool list, and register `BankTool` instances.       |
| `add_tools(tools_response)`   | No                | `None`       | Parse the server response and create/register `BankTool` instances into MAS.      |
| `_execute(oxy_request)`       | Yes               | `OxyResponse`| Abstract; raises `NotImplementedError` (tools are invoked via individual `BankTool`). |

## Inherited

Please refer to the [BaseBank](./base_bank.md) class for inherited parameters and methods.

## Usage

```python
oxy.BankClient(
    name="my_bank",
    server_url="http://localhost:8000",
    headers={"Authorization": "Bearer xxx"},
)
```

During MAS initialization, `BankClient.init()` will automatically fetch tools from `http://localhost:8000/list_banks` and register them.
