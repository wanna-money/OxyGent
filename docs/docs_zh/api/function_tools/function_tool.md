# FunctionTool
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

`FunctionTool` 是将 Python 函数封装为 OxyGent 系统中可执行工具的类。它自动从函数签名中提取输入模式，并通过适当的错误处理来执行函数，充当普通 Python 函数与 OxyGent 工具系统之间的桥梁。

## 参数

| 参数                     | 类型 / 允许值         | 默认值  | 描述                                                       |
| ------------------------ | --------------------- | ------- | ---------------------------------------------------------- |
| `is_permission_required` | `bool`                | `True`  | 执行时是否需要权限。                                       |
| `func_process`           | `Optional[Callable]`  | `None`  | 要封装和执行的 Python 函数。                               |
| `needs_oxy_request`      | `bool`                | `False` | 该工具是否需要 `oxy_request` 作为参数。                    |

## 方法

| 方法                           | 协程（异步）      | 返回值        | 用途简述                                                         |
| ------------------------------ | ----------------- | ------------- | ---------------------------------------------------------------- |
| `_extract_input_schema(func)`  | 否                | `dict`        | 从函数签名中提取包含参数和类型的输入模式。                       |
| `_execute(oxy_request)`        | 是                | `OxyResponse` | 使用提供的参数执行封装的函数，并进行错误处理。                   |

## 继承
 请参阅 [BaseTool](../tools/base_tools.md) 类了解继承的参数和方法。

## 用法

`FunctionTool` 实例通常由 `FunctionHub` 自动创建。直接使用方式：

```python
oxy.FunctionTool(
    name="my_tool",
    desc="A custom tool",
    func_process=my_async_function,
)
```
