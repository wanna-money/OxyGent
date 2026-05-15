# 如何自定义处理传递给子智能体的提示词？

在较为复杂的 MAS 系统中，您可能需要更新提示词，以防关键信息在智能体（Agent）之间传递时丢失。

OxyGent 支持通过外部方法处理提示词。例如，如果您在提示词中包含了文件内容，并希望确保每个 Agent 都能读取完整的提示词，可以使用 `update_query` 方法在查询中传递提示词。
## OxyRequest 常用方法

`func_process_input` 接收一个 `OxyRequest` 对象，您可以通过以下方法访问和修改请求内容：

| 方法 | 说明 |
|------|------|
| `get_query()` | 获取当前智能体收到的查询内容 |
| `get_query(master_level=True)` | 获取用户对 master 智能体的原始查询 |
| `set_query(text)` | 替换当前查询内容 |
| `get_short_memory()` | 获取当前智能体的对话记忆 |
| `get_short_memory(master_level=True)` | 获取 master 智能体的对话记忆 |
| `call(callee, arguments)` | 按名称调用其他智能体或工具 |
| `send_message(msg)` | 向前端发送流式消息 |
| `get_shared_data(key)` | 获取 trace 级别共享数据 |
| `set_shared_data(key, value)` | 设置 trace 级别共享数据 |
| `get_global_data(key)` | 获取 MAS 级别全局数据 |

> `master_level=True` 表示获取 master 智能体层级的数据，而不是当前子智能体的数据。这在子智能体需要了解用户原始意图时非常有用。

## 示例：更新提示词
```python
def update_query(oxy_request: OxyRequest):
    user_query = oxy_request.get_query(master_level=True)
    current_query = oxy_request.get_query()
    oxy_request.set_query(
        f"user query is {user_query}\ncurrent query is {current_query}"
    )
    return oxy_request
```

在上述代码中，我们通过 `update_query` 方法合并了 `user_query` 和 `current_query`，并将其设置为新的查询内容。

### 将更新方法应用于智能体

然后，您需要将 `update_query` 方法传递给 Agent 的输入处理函数 `func_process_input` 中，使得每个 Agent 都能使用自定义的处理逻辑：

```python
    oxy.ReActAgent(
        name="file_agent",
        desc="A tool that can operate the file system",
        tools=["file_tools"],
        func_process_input=update_query, #假设您希望file_agent读到原始文件 
    ),
    oxy.ReActAgent(
        name="time_agent",
        desc="A tool that can get current time",
        tools=["time_tools"], #您可以控制每个agent的处理方法
    ),
    # ...
```
## 完整的可运行样例

以下是可运行的完整代码示例：

```python
import asyncio

from oxygent import MAS, oxy, Config, OxyRequest
import os
from oxygent import preset_tools

Config.set_agent_llm_model("default_llm")

def update_query(oxy_request: OxyRequest):
    user_query = oxy_request.get_query(master_level=True)
    current_query = oxy_request.get_query()
    oxy_request.set_query(
        f"user query is {user_query}\ncurrent query is {current_query}"
    )
    return oxy_request

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.01},
        semaphore=4,
        timeout=240,
    ),
    oxy.StdioMCPClient(
        name="time_tools",
        params={
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
        },
    ),
    preset_tools.file_tools,
    oxy.ReActAgent(
        name="file_agent",
        desc="A tool that can operate the file system",
        tools=["file_tools"],
        func_process_input=update_query,
    ),
    oxy.ReActAgent(
        name="time_agent",
        desc="A tool that can get current time",
        tools=["time_tools"],
    ),
    oxy.ChatAgent(
        name="text_summarizer",
        desc="A tool that can summarize markdown text",
        prompt="You are a text summarizer. Please provide a concise summary of the given text.",
        func_process_input=update_query,
    ),
    oxy.ChatAgent(
        name="data_analyser",
        desc="A tool that can summarize echart data",
        prompt="You are a data analyst. Please analyze the given data and provide insights.",
        func_process_input=update_query,
    ),
    oxy.ChatAgent(
        name="document_checker",
        desc="A tool that can find problems in document",
        prompt="You are a document checker. Please review the document and identify any issues.",
        func_process_input=update_query,
    ),
    oxy.ParallelAgent(
        name="analyzer",
        desc="A tool that analyze markdown document",
        permitted_tool_name_list=["text_summarizer", "data_analyser", "document_checker"],
        func_process_input=update_query,
    ),
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        sub_agents=["file_agent","time_agent","analyzer"],
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello!"
        )


if __name__ == "__main__":
    asyncio.run(main())
```

[上一章：提供响应元数据](./trust-mode.md)
[下一章：处理LLM和智能体输出](./handle-output.md)
[回到首页](../readme.md)

---

## 相关示例

- [单智能体示例](../../examples/agents/demo_single_agent.md) — 展示func_process_input的基本用法
