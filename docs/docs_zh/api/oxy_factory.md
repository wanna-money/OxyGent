# OxyFactory
---
类所在位置:

```
oxygent/oxy_factory.py
```

---

## 简介

`OxyFactory` 是用于创建 OxyGent 算子的工厂类。它提供了一种集中式的方式来创建各种类型的 Oxy 组件，包括 Agent、工具、LLM 和工作流。该工厂使用注册表模式，通过一个静态字典将类名映射到对应的类构造函数，从而实现基于字符串标识符的动态组件创建。

## 参数

| 参数 | 类型 / 允许值 | 默认值 | 描述 |
| --------- | -------------------- | ------- | ----------- |
| `_creators` | `dict` | `{}` | 类名到类构造函数的静态映射字典 |

### 支持的组件

| 组件类型 | 类名 | 危险性 | 描述 |
| -------------- | ---------- | --------- | ----------- |
| Agent | `ChatAgent` | 是 | 基于聊天的对话 Agent |
| Agent | `ReActAgent` | 是 | ReAct 模式推理 Agent |
| Agent | `WorkflowAgent` | 是 | 基于工作流的 Agent |
| 工具 | `HttpTool` | 是 | 基于 HTTP 的 Web 请求工具 |
| 工具 | `MCPTool` | 是 | Model Context Protocol 工具 |
| 工具 | `FunctionTool` | 是 | 基于函数的工具 |
| LLM | `HttpLLM` | 否 | 基于 HTTP 的语言模型 |
| LLM | `OpenAILLM` | 否 | OpenAI 语言模型 |
| MCP 客户端 | `StdioMCPClient` | 是 | 标准 I/O MCP 客户端 |
| MCP 客户端 | `SSEMCPClient` | 是 | Server-Sent Events MCP 客户端 |
| 工作流 | `Workflow` | 是 | 工作流组件 |

> **安全说明：** 上表中标记为"危险"的组件会被 `create_oxy()` 阻止，如果外部请求创建将抛出 `SecurityError`。只有安全的组件（LLM）可以通过工厂创建。

## 方法

| 方法 | 协程 (async) | 返回值 | 用途 |
| ------ | ----------------- | ------------ | ------- |
| `_init_creators()` | 否 | `None` | 类方法，在模块加载时填充 `_creators` 注册表。 |
| `create_oxy(operator_class_name, **kwargs)` | 否 | `Oxy` | 静态方法，创建 Oxy 组件。对危险或未知的类将抛出 `SecurityError`。 |
