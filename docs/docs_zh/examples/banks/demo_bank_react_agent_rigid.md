# Bank ReAct 智能体 -- 刚性模式

**源文件:** `examples/banks/demo_bank_react_agent_rigid.py`

## 概述

本示例展示了将银行工具与 `ReActAgent` 集成的**刚性**（确定性）模式。与让智能体自主决定何时调用银行工具不同，`preceding_oxy` 机制在智能体处理每个查询之前自动调用 `user_profile_retrieve` 工具。检索结果被注入到智能体的提示词中，确保智能体始终拥有用户上下文，而无需依赖自身的推理来获取。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- 已安装 OxyGent 包（`pip install -r requirements.txt`）
- 在 `http://127.0.0.1:8090` 运行的**银行服务器**，需提供用户档案检索工具

## 运行方式

1. 在端口 8090 启动银行服务器。
2. 运行：

```bash
python -m examples.banks.demo_bank_react_agent_rigid
```

## 代码详解

### 组件（`oxy_space`）

| 组件 | 类型 | 角色 |
|---|---|---|
| `default_llm` | `HttpLLM` | 语言模型，温度 0.01，信号量 4 |
| `qa_agent` | `ReActAgent` | 具有刚性前置上下文注入的问答智能体 |
| `remote_user_profile_banks` | `BankClient` | 连接 `http://127.0.0.1:8090` 银行服务器的客户端 |

### 智能体配置 -- 刚性模式

```python
oxy.ReActAgent(
    name="qa_agent",
    llm_model="default_llm",
    prompt=SYSTEM_PROMPT + "\nYou can refer to the following information to answer the question:\n${preceding_text}",
    preceding_oxy=["user_profile_retrieve"],
    preceding_placeholder="preceding_text",
)
```

关键参数：

- **`preceding_oxy=["user_profile_retrieve"]`**：在每次查询前，系统自动调用银行中的 `user_profile_retrieve` 工具。这不是可选的，每次请求都会执行。
- **`preceding_placeholder="preceding_text"`**：检索结果替换提示词中的 `${preceding_text}`。
- **`prompt`**：在默认 `SYSTEM_PROMPT` 基础上扩展了引用前置文本的部分，确保智能体知道使用检索到的上下文。

这是"刚性"方法，因为工具调用被硬编码到智能体的生命周期中，不受智能体推理的影响。

### 请求过滤器

```python
def func_filter(payload):
    payload["group_data"] = {"user_pin": "002"}
    return payload
```

注入用户身份用于银行数据范围限定。

### 入口

```python
async def main():
    async with MAS(oxy_space=oxy_space, func_filter=func_filter) as mas:
        await mas.start_web_service(first_query="Who I am")
```

## 核心概念

- **刚性模式 vs 自主模式**：在刚性模式中，银行工具通过 `preceding_oxy` 在每次查询前确定性调用。在自主模式中，智能体自行决定何时调用工具。刚性模式更可预测，确保上下文始终可用；自主模式更灵活，但依赖于 LLM 的推理能力。
- **前置 Oxy（Preceding Oxy）**：在智能体主处理循环之前自动调用指定工具的机制。结果通过命名占位符注入到提示词中。
- **`SYSTEM_PROMPT`**：从 `oxygent.prompts` 导入的默认系统提示词，扩展了前置上下文部分。这为智能体提供了基础指令加上检索到的信息。

## 预期行为

1. Web 界面打开，查询"Who I am"。
2. 在智能体处理查询之前，自动从银行为用户 `002` 调用 `user_profile_retrieve`。
3. 检索到的档案数据注入到提示词的 `${preceding_text}` 位置。
4. `qa_agent` 使用系统提示指令和检索到的用户档案进行回答。
5. 每个后续查询也会触发自动档案检索，确保上下文一致。
