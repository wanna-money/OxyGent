# StdioMCPClient
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

`StdioMCPClient` 是通过标准输入/输出流与 MCP 服务器通信的 MCP 客户端实现。它会启动并管理作为 MCP 服务器的外部进程（如 Node.js 脚本或 Python uvx 包）。

## 参数


| 参数      | 类型 / 允许值       | 默认值  | 描述                                                                     |
| --------- | -------------------- | ------- | ------------------------------------------------------------------------ |
| `params`  | `dict[str, Any]`     | `{}`    | 配置参数，包括 `command`、`args` 和 `env` 值。                           |

## 方法


| 方法                                     | 协程（异步）      | 返回值                  | 用途简述                                                   |
| ---------------------------------------- | ----------------- | ----------------------- | ---------------------------------------------------------- |
| `init(is_fetch_tools)`                   | 是                | `None`                  | 初始化到 MCP 服务器进程的 Stdio 连接。                     |
| `_ensure_directories_exist(args)`        | 是                | `None`                  | 在启动 MCP 服务器前确保所需目录存在。                      |
| `call_tool(tool_name, arguments, headers)` | 是              | `Any`                   | 打开新的 Stdio 连接并调用指定工具。                        |
| `get_server_params()`                    | 是                | `StdioServerParameters` | 解析并返回 Stdio 传输的服务器参数。                        |

## 继承
 请参阅 [BaseMCPClient](./base_mcp_client.md) 类了解继承的参数和方法。

## 用法

```python
oxy.StdioMCPClient(
    name="time_tools",
    params={
        "command": "uvx",
        "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
    },
)
```
