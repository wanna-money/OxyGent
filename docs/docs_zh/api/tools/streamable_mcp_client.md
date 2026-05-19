# StreamableMCPClient
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

`StreamableMCPClient` 是使用 Streamable-HTTP 传输协议的 MCP 客户端实现。它扩展了 `BaseMCPClient`，提供 HTTP 流式连接能力，用于与 MCP 服务器通信。

## 参数


| 参数          | 类型 / 允许值       | 默认值  | 描述                                                   |
| ------------- | -------------------- | ------- | ------------------------------------------------------ |
| `server_url`  | `AnyUrl`             | `""`    | MCP 服务器的 Streamable-HTTP 端点 URL。                |
| `middlewares` | `list[Any]`          | `[]`    | 用于请求处理的客户端 MCP 中间件。                      |

## 方法


| 方法                                       | 协程（异步）      | 返回值       | 用途简述                                                           |
| ------------------------------------------ | ----------------- | ------------ | ------------------------------------------------------------------ |
| `init(is_fetch_tools)`                     | 是                | `None`       | 初始化到 MCP 服务器的 HTTP 流式连接。                              |
| `call_tool(tool_name, arguments, headers)` | 是                | `Any`        | 打开新的 Streamable-HTTP 连接并调用指定工具。                      |

## 继承
 请参阅 [BaseMCPClient](./base_mcp_client.md) 类了解继承的参数和方法。

## 用法

```python
oxy.StreamableMCPClient(
    name="remote_tools",
    server_url="http://127.0.0.1:8000/mcp",
)
```
