# BankTool

---
该类在类层级结构中的位置：

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

## 简介

`BankTool` 表示由 Bank 服务器暴露的单个工具。它继承自 `BaseBank` 并实现了 `_execute()` 方法，通过 HTTP 调用工具。实例通常由 `BankClient.add_tools()` 动态创建，而非手动创建。

## 参数

| 参数                    | 类型 / 允许值            | 默认值  | 描述                                                         |
| ----------------------- | ------------------------ | ------- | ------------------------------------------------------------ |
| `server_url`            | `AnyUrl`                 | `""`    | 该工具对应的 Bank 服务器端点 URL。                           |
| `method`                | `Literal["GET", "POST"]` | `"GET"` | 调用此工具时使用的 HTTP 方法。                               |
| `is_permission_required`| `bool`                   | `True`  | 执行时是否需要权限。                                         |
| `headers`               | `Dict[str, str]`         | `{}`    | 请求时发送的额外 HTTP 头。                                   |
| `is_retrievable`        | `bool`                   | `False` | 该工具是否可通过向量搜索检索发现。                           |

## 方法

| 方法                    | 协程（异步）      | 返回值        | 用途简述                                                             |
| ----------------------- | ----------------- | ------------- | -------------------------------------------------------------------- |
| `_execute(oxy_request)` | 是                | `OxyResponse` | 向 `server_url` 发送 POST 请求，携带 `oxy_request.arguments` 并返回结果。 |

## 继承

请参阅 [BaseBank](./base_bank.md) 类了解继承的参数和方法。

## 用法

`BankTool` 实例通常由 `BankClient` 自动创建。手动创建方式：

```python
oxy.BankTool(
    name="get_weather",
    desc="Get weather for a city",
    server_url="http://localhost:8000/tools/get_weather",
    method="POST",
    headers={"Authorization": "Bearer xxx"},
)
```
