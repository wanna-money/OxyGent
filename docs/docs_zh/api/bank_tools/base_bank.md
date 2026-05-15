# BaseBank

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

`BaseBank` 是 Bank 工具的抽象基类，扩展了 `BaseTool` 并将 `category` 固定为 `"bank"`。Bank 工具是基于 FastAPI 路由的工具集合，将 HTTP 端点作为可调用工具暴露在 OxyGent 框架中。该类是 `BankTool`（单个工具条目）和 `BankClient`（从 Bank 服务器发现并注册工具的客户端）的基础。

## 参数

| 参数       | 类型 / 允许值       | 默认值   | 描述                                                 |
| ---------- | -------------------- | -------- | ---------------------------------------------------- |
| `category` | `str`                | `"bank"` | 类别标识符，Bank 工具固定为 `"bank"`。               |

## 方法

| 方法                      | 协程（异步）      | 返回值        | 用途简述                                             |
| ------------------------- | ----------------- | ------------- | ---------------------------------------------------- |
| `_execute(oxy_request)`   | 是                | `OxyResponse` | 抽象方法；默认抛出 `NotImplementedError`。           |

## 继承

请参阅 [BaseTool](../tools/base_tools.md) 类了解继承的参数和方法。
