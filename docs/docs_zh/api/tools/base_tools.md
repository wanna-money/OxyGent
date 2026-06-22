# BaseTool
---
该类在类层级结构中的位置：


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

## 简介

`BaseTool` 是 OxyGent 系统中所有工具的抽象基类。它为工具实现提供了通用功能，包括权限控制、类别标识和执行超时管理。工具是特殊的 Oxy 实例，通常需要权限且具有较短的超时时间。

## 参数

| 参数                     | 类型 / 允许值       | 默认值                        | 描述                         |
| ------------------------ | -------------------- | ----------------------------- | ---------------------------- |
| `is_permission_required` | `bool`               | `True`                        | 执行时是否需要权限。         |
| `category`               | `str`                | `"tool"`                      | 工具类别标识符。             |
| `semaphore`              | `int`                | `Config.get_tool_semaphore()` | 并行工具调用的并发限制。     |
| `timeout`                | `float`              | `Config.get_tool_timeout()`   | 执行超时时间（秒）。        |

## 方法

| 方法                    | 协程（异步）      | 返回值        | 用途简述                                                       |
| ----------------------- | ----------------- | ------------- | -------------------------------------------------------------- |
| `_execute(oxy_request)` | 是                | `OxyResponse` | **抽象方法** -- 子类必须实现此方法以执行工具逻辑。             |

## 继承

 请参阅 [Oxy](../agent/base_oxy.md) 类了解继承的参数和方法。

## 用法

`BaseTool` 类必须被继承使用。
