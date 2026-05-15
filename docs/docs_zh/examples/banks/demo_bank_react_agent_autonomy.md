# Bank ReAct 智能体 -- 自主模式

**源文件:** `examples/banks/demo_bank_react_agent_autonomy.py`

## 概述

本示例展示了一个通过 `BankClient` 连接远程工具银行的 **ReActAgent**，运行在**自主模式**下 -- 智能体根据用户查询自行决定何时以及如何调用银行提供的工具。与"刚性"模式不同，银行工具注册在智能体的 `banks` 列表中（而非 `preceding_oxy`），赋予智能体对工具调用的完全控制权。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- 已安装 OxyGent 包（`pip install -r requirements.txt`）
- 在 `http://127.0.0.1:8090` 运行的**银行服务器**，需提供用户档案工具

## 运行方式

1. 在端口 8090 启动银行服务器。
2. 运行：

```bash
python -m examples.banks.demo_bank_react_agent_autonomy
```

## 代码详解

### 组件（`oxy_space`）

| 组件 | 类型 | 角色 |
|---|---|---|
| `default_llm` | `HttpLLM` | 语言模型，温度 0.01，信号量 4 |
| `time_tools` | `StdioMCPClient` | MCP 时间查询工具（Asia/Shanghai 时区） |
| `qa_agent` | `ReActAgent` | 具有自主工具使用能力的问答智能体 |
| `remote_user_profile_banks` | `BankClient` | 连接 `http://127.0.0.1:8090` 银行服务器的客户端 |

### 智能体配置

`qa_agent` 是一个 `ReActAgent`，配置如下：
- **`tools=["time_tools"]`**：智能体可直接调用的 MCP 工具。
- **`banks=["remote_user_profile_banks"]`**：银行客户端，其工具对智能体可用。智能体根据查询自主决定是否调用银行工具。

这是**自主**模式：智能体在其工具描述中可以看到所有可用工具（直接工具和银行工具），并使用 ReAct 推理来决定调用哪些工具。

### 请求过滤器

```python
def func_filter(payload):
    payload["group_data"] = {"user_pin": "002"}
    return payload
```

将用户身份（`user_pin: "002"`）注入所有请求，用于银行数据范围限定。

### 入口

```python
async def main():
    async with MAS(oxy_space=oxy_space, func_filter=func_filter) as mas:
        await mas.start_web_service(first_query="Who I am")
```

## 核心概念

- **自主模式**：智能体拥有银行工具并通过 ReAct 推理自主决定何时使用，而非在处理查询前自动调用工具。
- **BankClient**：连接到远程基于 FastAPI 的工具银行服务器，使其工具如同本地工具一样可用。
- **混合工具源**：智能体组合了不同来源的工具 -- 用于时间查询的 `StdioMCPClient` 和用于用户档案操作的 `BankClient` -- 展示了 OxyGent 统一的工具接口。

## 预期行为

1. Web 界面打开，查询"Who I am"。
2. `qa_agent` 使用 ReAct 推理判断需要用户档案信息。
3. 自主调用银行中的用户档案检索工具。
4. 如果相关，还可能使用时间工具。
5. 智能体将检索到的信息合成为自然语言响应。
