# Bank ReAct 智能体 -- 通过 MCP 实现自主模式

**源文件:** `examples/banks/demo_bank_react_agent_autonomy_by_mcp.py`

## 概述

本示例是自主模式银行智能体的变体，使用 **SSEMCPClient** 代替 `BankClient` 连接远程工具银行。银行工具通过 SSE（Server-Sent Events）协议以 MCP 工具的形式暴露，智能体将其与任何其他 MCP 工具同等对待。这展示了 OxyGent 通过 MCP 协议（而非原生 BankClient 接口）消费银行工具的能力。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- 已安装 OxyGent 包（`pip install -r requirements.txt`）
- 在 `http://127.0.0.1:8000/sse` 运行的**支持 MCP SSE 的银行服务器**（注意：与 BankClient 示例使用不同的端口和协议）
- PATH 中可用 `uvx`（用于 `mcp-server-time`）

## 运行方式

1. 在端口 8000 启动支持 MCP SSE 的银行服务器。
2. 运行：

```bash
python -m examples.banks.demo_bank_react_agent_autonomy_by_mcp
```

## 代码详解

### 组件（`oxy_space`）

| 组件 | 类型 | 角色 |
|---|---|---|
| `default_llm` | `HttpLLM` | 语言模型，温度 0.01，信号量 4 |
| `time_tools` | `StdioMCPClient` | MCP 时间查询工具（Asia/Shanghai 时区） |
| `qa_agent` | `ReActAgent` | 具有自主工具使用能力的问答智能体 |
| `remote_user_profile_banks` | `SSEMCPClient` | 通过 SSE 连接银行服务器的 MCP 客户端，地址为 `http://127.0.0.1:8000/sse` |

### 关键区别：SSEMCPClient vs BankClient

在本示例中，银行工具通过 `SSEMCPClient` 而非 `BankClient` 访问：

```python
oxy.SSEMCPClient(
    name="remote_user_profile_banks",
    sse_url="http://127.0.0.1:8000/sse",
)
```

银行工具注册在智能体的 `tools` 列表中（而非 `banks`）：

```python
oxy.ReActAgent(
    name="qa_agent",
    tools=["time_tools", "remote_user_profile_banks"],
    ...
)
```

这意味着智能体将银行工具视为普通 MCP 工具，使其与其他工具源无法区分。

### 请求过滤器

```python
def func_filter(payload):
    payload["group_data"] = {"user_pin": "002"}
    return payload
```

与其他银行示例相同的用户范围限定过滤器。

### 入口

```python
async def main():
    async with MAS(oxy_space=oxy_space, func_filter=func_filter) as mas:
        await mas.start_web_service(first_query="Who I am")
```

## 核心概念

- **SSEMCPClient**：通过 Server-Sent Events（SSE）与工具服务器通信的 MCP 客户端。这是 `StdioMCPClient`（使用标准 I/O）的替代方案，适用于远程服务器。
- **MCP 作为通用工具协议**：通过将银行工具暴露为 MCP 端点，智能体可以使用与任何 MCP 工具相同的接口来消费它们，展示了协议级别的互操作性。
- **Tools vs Banks**：在本示例中，MCP 客户端列在 `tools` 而非 `banks` 中。智能体将银行的工具视为标准 MCP 工具，对其使用拥有同样的自主决策能力。

## 预期行为

1. Web 界面打开，查询"Who I am"。
2. `qa_agent` 使用 ReAct 推理，在工具列表中看到时间工具和用户档案工具。
3. 自主决定通过 MCP SSE 调用用户档案检索工具。
4. 智能体基于检索到的用户 `002` 的档案返回响应。
