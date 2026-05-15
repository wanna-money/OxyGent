# FunctionHub
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

`FunctionHub` 是用于注册和管理 Python 函数作为工具的中心枢纽。它提供了基于装饰器的接口，将普通 Python 函数转换为可执行工具，支持同步和异步函数并自动进行转换。

## 参数

| 参数        | 类型 / 允许值       | 默认值  | 描述                                                                   |
| ----------- | -------------------- | ------- | ---------------------------------------------------------------------- |
| `func_dict` | `dict`               | `{}`    | 函数及其元数据的注册表：`{name: (description, async_func)}`。          |

## 方法

| 方法               | 协程（异步）      | 返回值       | 用途简述                                                                   |
| ------------------ | ----------------- | ------------ | -------------------------------------------------------------------------- |
| `init()`           | 是                | `None`       | 为所有已注册函数创建 `FunctionTool` 实例并注册到 MAS。                     |
| `tool(description)`| 否                | `Callable`   | 用于将函数注册为工具的装饰器（支持同步和异步）。                           |
| `cleanup()`        | 是                | `None`       | 清理资源，包括线程池。                                                     |

## 继承
 请参阅 [BaseTool](../tools/base_tools.md) 类了解继承的参数和方法。

## 用法

```python
file_tools = FunctionHub(name="file_tools")


@file_tools.tool(
    description="Create a new file or overwrite an existing file with new content."
)
def write_file(
    path: str = Field(description="File path"),
    content: str = Field(description="File content"),
) -> str:
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)
    return "Successfully wrote to " + path
```
