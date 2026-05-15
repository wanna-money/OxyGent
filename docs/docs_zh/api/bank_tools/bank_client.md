# BankClient

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

`BankClient` 连接到远程 Bank 服务器（使用 `BankRouter` 的 FastAPI 应用），动态发现并将其工具注册为 `BankTool` 实例。在 `init()` 期间，它从服务器的 `/list_banks` 端点获取工具列表，并将每个工具注册到 MAS 运行时中。

## 参数

| 参数                     | 类型 / 允许值       | 默认值  | 描述                                                   |
| ------------------------ | -------------------- | ------- | ------------------------------------------------------ |
| `server_url`             | `AnyUrl`             | `""`    | 远程 Bank 服务器的 URL。                               |
| `included_bank_name_list`| `list`               | `[]`    | 从服务器发现的 Bank 工具名称列表。                     |
| `headers`                | `Dict[str, str]`     | `{}`    | 请求时发送的额外 HTTP 头。                             |

## 方法

| 方法                          | 协程（异步）      | 返回值        | 用途简述                                                                         |
| ----------------------------- | ----------------- | ------------- | -------------------------------------------------------------------------------- |
| `init()`                      | 是                | `None`        | 连接到 Bank 服务器，获取工具列表，并注册 `BankTool` 实例。                       |
| `add_tools(tools_response)`   | 否                | `None`        | 解析服务器响应，创建 `BankTool` 实例并注册到 MAS 中。                            |
| `_execute(oxy_request)`       | 是                | `OxyResponse` | 抽象方法；抛出 `NotImplementedError`（工具通过单独的 `BankTool` 调用）。         |

## 继承

请参阅 [BaseBank](./base_bank.md) 类了解继承的参数和方法。

## 用法

```python
oxy.BankClient(
    name="my_bank",
    server_url="http://localhost:8000",
    headers={"Authorization": "Bearer xxx"},
)
```

在 MAS 初始化期间，`BankClient.init()` 会自动从 `http://localhost:8000/list_banks` 获取工具并注册。
