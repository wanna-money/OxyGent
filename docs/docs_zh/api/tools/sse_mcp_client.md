# SSEMCPClient
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

`SSEMCPClient` 是使用 Server-Sent Events (SSE) 传输协议的 MCP 客户端实现。它扩展了 `BaseMCPClient`，通过 SSE 提供 MCP 通信能力，支持从服务器到客户端的实时单向通信。

## 参数


| 参数          | 类型 / 允许值       | 默认值  | 描述                                                   |
| ------------- | -------------------- | ------- | ------------------------------------------------------ |
| `sse_url`     | `AnyUrl`             | `""`    | 连接到 MCP 服务器的 SSE URL。                          |
| `middlewares` | `list[Any]`          | `[]`    | 应用于会话的客户端 MCP 中间件。                        |

## 方法


| 方法                                       | 协程（异步）      | 返回值       | 用途简述                                                         |
| ------------------------------------------ | ----------------- | ------------ | ---------------------------------------------------------------- |
| `init(is_fetch_tools)`                     | 是                | `None`       | 初始化到 MCP 服务器的 SSE 连接并发现工具。                       |
| `call_tool(tool_name, arguments, headers)` | 是                | `Any`        | 打开新的 SSE 连接并调用指定工具。                                |

## 继承
 请参阅 [BaseMCPClient](./base_mcp_client.md) 类了解继承的参数和方法。

## 用法

```python
oxy.SSEMCPClient(
    name="math_tools",
    sse_url="http://127.0.0.1:8000/sse",
)
```
