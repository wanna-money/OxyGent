# BaseBank

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

`BaseBank` is an abstract base class for bank tools, extending `BaseTool` with a fixed `category` of `"bank"`. Bank tools are FastAPI-router-based tool collections that expose HTTP endpoints as callable tools within the OxyGent framework. This class serves as the foundation for both `BankTool` (individual tool entries) and `BankClient` (clients that discover and register tools from a bank server).

## Parameters

| Parameter  | Type / Allowed value | Default  | Description                                           |
| ---------- | -------------------- | -------- | ----------------------------------------------------- |
| `category` | `str`                | `"bank"` | Category identifier, always `"bank"` for bank tools.  |

## Methods

| Method                    | Coroutine (async) | Return Value  | Purpose (concise)                                  |
| ------------------------- | ----------------- | ------------- | -------------------------------------------------- |
| `_execute(oxy_request)`   | Yes               | `OxyResponse` | Abstract; raises `NotImplementedError` by default. |

## Inherited

Please refer to the [BaseTool](../tools/base_tools.md) class for inherited parameters and methods.
