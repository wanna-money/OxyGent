# BaseMCPClient
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

`BaseMCPClient` 是 Model Context Protocol (MCP) 服务器的基础客户端。它为连接和交互 MCP 服务器提供了基础，负责处理服务器生命周期管理、工具发现、动态工具注册以及通过 MCP 协议执行工具。

## 参数


| 参数                      | 类型 / 允许值       | 默认值                                | 描述                                                     |
| ------------------------- | -------------------- | ------------------------------------- | -------------------------------------------------------- |
| `included_tool_name_list` | `list`               | `[]`                                  | 从 MCP 服务器发现并注册的工具名称列表。                  |
| `headers`                 | `Dict[str, str]`     | `{}`                                  | 与服务器通信时使用的额外 HTTP 头。                       |
| `is_dynamic_headers`      | `bool`               | `False`                               | 是否在每次调用时从请求上下文重新构建 HTTP 头。           |
| `is_inherit_headers`      | `bool`               | `False`                               | 是否从父请求继承 HTTP 头。                               |
| `is_keep_alive`           | `bool`               | `Config.get_tool_mcp_is_keep_alive()` | 是否在多次工具调用间复用 MCP 连接。                      |

## 方法


| 方法                         | 协程（异步）      | 返回值        | 用途简述                                                    |
| ---------------------------- | ----------------- | ------------- | ----------------------------------------------------------- |
| `list_tools()`               | 是                | `None`        | 从 MCP 服务器发现并注册工具。                               |
| `add_tools(tools_response)`  | 否                | `None`        | 从服务器的工具列表动态注册 `MCPTool` 实例。                 |
| `_execute(oxy_request)`      | 是                | `OxyResponse` | 通过 MCP 服务器执行工具调用。                               |
| `cleanup()`                  | 是                | `None`        | 清理 MCP 服务器资源和连接。                                 |

## 继承
 请参阅 [BaseTool](./base_tools.md) 类了解继承的参数和方法。

## 用法

`BaseMCPClient` 类必须被继承使用。
