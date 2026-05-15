# MCPTool
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

`MCPTool` 是 MCP 服务器工具的独立工具代理。它代表从 MCP 服务器发现的特定工具，作为轻量级代理将实际执行委托给父 MCP 客户端，同时提供标准的 `BaseTool` 接口。

## 参数


| 参数                     | 类型 / 允许值       | 默认值  | 描述                                                       |
| ------------------------ | -------------------- | ------- | ---------------------------------------------------------- |
| `is_permission_required` | `bool`               | `True`  | 执行前是否需要显式权限。                                   |
| `mcp_client`             | `Any`                | `None`  | 对负责实际执行的父 MCP 客户端的引用。                      |
| `server_name`            | `str`                | `""`    | 提供此工具的 MCP 服务器名称。                              |

## 方法


| 方法                    | 协程（异步）      | 返回值        | 用途简述                                                 |
| ----------------------- | ----------------- | ------------- | -------------------------------------------------------- |
| `_execute(oxy_request)` | 是                | `OxyResponse` | 通过委托给父 MCP 客户端来执行 MCP 工具。                 |

## 继承
 请参阅 [BaseTool](./base_tools.md) 类了解继承的参数和方法。

## 用法

`MCPTool` 实例由 `BaseMCPClient` 在工具发现过程中自动创建，通常不需要直接实例化。
