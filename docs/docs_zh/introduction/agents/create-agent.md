# 如何注册一个智能体?

在OxyGent中，基础的智能体由[智能体（Agent）](./agent-types.md)和内部封装的[大语言模型（LLM）](./select-llm.md)组成。

对于新用户，您可以使用`oxy.HttpLLM`方法通过您的`api_key`注册LLM：

```python
oxy.HttpLLM(
    name="default_llm",
    api_key=os.getenv("DEFAULT_LLM_API_KEY"),
    base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
    model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    llm_params={"temperature": 0.01},
    semaphore=4, # 并发量
    timeout=240, # 最大执行时间
),
```
> 其中 `semaphore` 参数的详细说明请参见 [并行](../multi-agent/parallel.md) 部分。

接下来，您可以使用`oxy.ChatAgent`或者`oxy.ReActAgent`封装您的第一个agent：
```python
oxy.ReActAgent(
    name="master_agent",
    prompt = master_prompt, # 支持自定义prompt
    is_master=True, # 设置为master
    llm_model="default_llm",
),
```

为了使 LLM 和智能体生效，它们需要被添加到 `oxy_space` 中。

> **关键概念**
> - **`oxy_space`** 是一个 Python 列表，包含了系统中所有的 LLM、Agent、Tool 组件。组件之间通过 `name` 字符串互相引用。
> - **`MAS`**（Multi-Agent System）是运行时容器。`async with MAS(oxy_space=...) as mas` 会注册所有组件并建立引用关系。
> - **`is_master=True`** 标记入口智能体——用户的消息首先到达它，由它决定如何处理或分发给子智能体。
> - 更多概念请参考 [OxyGent 概念总览](../getting-started/overview.md)。

## 完整的可运行样例

以下是可运行的完整代码示例：

```python
import asyncio

from oxygent import MAS, oxy
import os

master_prompt = """
你是一个文档分析专家，用户会向你提供文档，请为用户提供简要的文档摘要。
摘要可以是markdown格式。
"""

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
    oxy.ReActAgent(
        name="master_agent",
        prompt = master_prompt,
        is_master=True,
        llm_model="default_llm",
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

[上一章：快速上手](../getting-started/quickstart.md)
[下一章：和智能体交流](./chat-with-agent.md)
[回到首页](../readme.md)

---

## 相关示例

- [单 Agent 示例](../../examples/agents/demo_single_agent.md) — 最简单的 ChatAgent 配置
- [ReAct Agent 示例](../../examples/agents/demo_react_agent.md) — 带反思机制的 ReActAgent
- [层级式多 Agent 示例](../../examples/agents/demo_hierarchical_agents.md) — 主从 Agent 架构
