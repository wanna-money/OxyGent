# Bank 聊天智能体 - 记忆存储示例

**源文件:** `examples/banks/demo_bank_chat_agent_dump_memory.py`

## 概述

本示例展示了如何使用 **BankClient** 连接远程工具银行服务器，以及如何实现一个后处理回调函数，在每次响应后异步将对话历史（问答对）存储回银行。`ChatAgent` 在回答前从银行检索用户档案上下文，`dump_memory` 回调则将交互记录存储以供将来参考。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- 已安装 OxyGent 包（`pip install -r requirements.txt`）
- 在 `http://127.0.0.1:8090` 运行的 **银行服务器**，需提供用户档案检索（`user_profile_retrieve`）和存储（`user_profile_deposit`）工具

## 运行方式

1. 在端口 8090 启动银行服务器（参见仓库中的银行服务器示例）。
2. 运行此客户端：

```bash
python -m examples.banks.demo_bank_chat_agent_dump_memory
```

## 代码详解

### 回调函数

```python
async def dump_memory(oxy_response: OxyResponse) -> OxyResponse:
```

一个后处理回调（`func_process_output`），它：

1. 从响应中提取原始查询和智能体的回答。
2. 将它们序列化为 JSON 对象。
3. 通过 `oxy_request.call_async()` 异步调用银行服务器上的 `user_profile_deposit` 工具，设置 `is_send_message=False`（即发即忘，不向用户发送 SSE 消息）。
4. 原样返回 `OxyResponse`。

### 组件（`oxy_space`）

| 组件 | 类型 | 角色 |
|---|---|---|
| `default_llm` | `HttpLLM` | 语言模型，温度 0.01，信号量 4 |
| `qa_agent` | `ChatAgent` | 主问答智能体；使用银行工具和前置上下文 |
| `remote_user_profile_banks` | `BankClient` | 连接 `http://127.0.0.1:8090` 银行服务器的客户端 |

### 智能体配置详情

`qa_agent` 配置了以下关键参数：

- **`banks=["remote_user_profile_banks"]`**：注册银行客户端，使其工具可用。
- **`preceding_oxy=["user_profile_retrieve"]`**：在智能体处理查询之前，自动调用银行中的 `user_profile_retrieve` 获取相关上下文。
- **`preceding_placeholder="preceding_text"`**：检索结果注入到提示词中的 `${preceding_text}` 位置。
- **`func_process_output=dump_memory`**：每次响应后，`dump_memory` 回调存储问答对。

### 请求过滤器

```python
def func_filter(payload):
    payload["group_data"] = {"user_pin": "002"}
    return payload
```

传递给 `MAS` 的过滤函数，将 `group_data`（用户标识 `user_pin: "002"`）注入到每个传入的请求负载中。这使银行服务器能够将数据检索和存储限定在特定用户范围内。

### 入口

```python
async def main():
    async with MAS(oxy_space=oxy_space, func_filter=func_filter, name="temp_app") as mas:
        await mas.start_web_service(first_query="Who I am")
```

创建一个命名的 MAS 实例（`temp_app`），带有过滤函数，并启动 Web 服务。初始查询"Who I am"触发从银行检索用户档案。

## 核心概念

- **BankClient**：连接远程工具银行（基于 FastAPI 的服务器）的客户端组件，将其工具暴露给智能体。银行服务器可以托管任意数量的工具（检索、存储、搜索等）。
- **前置 Oxy（Preceding Oxy）**：`preceding_oxy` 机制在智能体处理用户查询前自动调用指定工具。结果通过占位符注入到提示词中，提供上下文信息。
- **`func_process_output`**：智能体上的后处理钩子，接收 `OxyResponse` 并可在返回响应给用户之前执行副作用（如记忆存储）。
- **`call_async` 与 `is_send_message=False`**：触发异步工具调用，不阻塞响应管道，也不向前端发送进度消息。
- **`func_filter`**：MAS 上的全局请求过滤器，可以向所有传入请求注入元数据（如用户身份）。

## 预期行为

1. Web 界面打开，查询"Who I am"。
2. 回答前，从银行调用 `user_profile_retrieve` 获取用户 `002` 的档案数据。
3. 检索到的档案数据作为 `${preceding_text}` 注入智能体的提示词。
4. `qa_agent` 基于检索到的档案上下文进行回答。
5. 响应生成后，`dump_memory` 异步将问答对通过 `user_profile_deposit` 存储回银行。
6. 在后续查询中，存储的历史记录将丰富未来的检索结果。
