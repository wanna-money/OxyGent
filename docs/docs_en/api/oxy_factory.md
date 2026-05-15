# OxyFactory
---
The position of the class is:

```
oxygent/oxy_factory.py
```

---

## Introduction

`OxyFactory` is a factory class for creating OxyGent operators. It provides a centralized way to create various types of Oxy components including agents, tools, LLMs, and workflows. The factory uses a registry pattern with a static dictionary mapping class names to their corresponding class constructors, enabling dynamic component creation based on string identifiers.

## Parameters

| Parameter | Type / Allowed value | Default | Description |
| --------- | -------------------- | ------- | ----------- |
| `_creators` | `dict` | `{}` | Static dictionary mapping class names to class constructors |

### Supported Components

| Component Type | Class Name | Dangerous | Description |
| -------------- | ---------- | --------- | ----------- |
| Agent | `ChatAgent` | Yes | Chat-based conversational agent |
| Agent | `ReActAgent` | Yes | ReAct pattern reasoning agent |
| Agent | `WorkflowAgent` | Yes | Workflow-based agent |
| Tool | `HttpTool` | Yes | HTTP-based tool for web requests |
| Tool | `MCPTool` | Yes | Model Context Protocol tool |
| Tool | `FunctionTool` | Yes | Function-based tool |
| LLM | `HttpLLM` | No | HTTP-based language model |
| LLM | `OpenAILLM` | No | OpenAI language model |
| MCP Client | `StdioMCPClient` | Yes | Standard I/O MCP client |
| MCP Client | `SSEMCPClient` | Yes | Server-Sent Events MCP client |
| Workflow | `Workflow` | Yes | Workflow component |

> **Security:** Components marked "Dangerous" in the table above are blocked by `create_oxy()` and will raise `SecurityError` if requested externally. Only safe components (LLMs) can be created through the factory.

## Methods

| Method | Coroutine (async) | Return Value | Purpose |
| ------ | ----------------- | ------------ | ------- |
| `_init_creators()` | No | `None` | Class method to populate the `_creators` registry at module load time. |
| `create_oxy(operator_class_name, **kwargs)` | No | `Oxy` | Static method to create an Oxy component. Raises `SecurityError` for dangerous or unknown classes. |
