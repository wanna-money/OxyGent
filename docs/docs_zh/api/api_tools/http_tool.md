# HttpTool
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

`HttpTool` 是用于向外部 API 和服务发起 HTTP 请求的工具。它支持可配置的 HTTP 方法（GET、POST、PUT、DELETE、PATCH）、请求头和默认参数，并具有适当的超时处理。

## 参数


| 参数             | 类型 / 允许值       | 默认值  | 描述                                                       |
| ---------------- | -------------------- | ------- | ---------------------------------------------------------- |
| `method`         | `str`                | `"GET"` | 使用的 HTTP 方法（GET、POST、PUT、DELETE、PATCH）。        |
| `url`            | `str`                | `""`    | HTTP 请求的目标 URL。                                      |
| `headers`        | `dict`               | `{}`    | 请求中包含的 HTTP 头。                                     |
| `default_params` | `dict`               | `{}`    | 将与请求参数合并的默认参数。                               |

## 方法


| 方法                    | 协程（异步）      | 返回值        | 用途简述                                                         |
| ----------------------- | ----------------- | ------------- | ---------------------------------------------------------------- |
| `_execute(oxy_request)` | 是                | `OxyResponse` | 使用合并后的参数和超时处理执行 HTTP 请求。                       |

## 继承
 请参阅 [BaseTool](../tools/base_tools.md) 类了解继承的参数和方法。

## 用法

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
