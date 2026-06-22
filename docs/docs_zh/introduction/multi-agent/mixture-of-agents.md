# 如何快速复制多个智能体？（Mixture of Agents）

## 概述

Mixture of Agents（MoA）是一种多智能体协作模式，通过创建同一智能体的多个并行实例来处理相同的查询，然后将所有实例的响应聚合为一个最终答案。这种方式类似于机器学习中的集成学习（Ensemble Learning），能够提高回答的质量和稳定性。

在OxyGent中，您可以通过 `team_size` 参数轻松实现MoA模式，无需手动创建和管理多个智能体实例。

## `team_size` 参数说明

`team_size` 是智能体的一个配置参数，用于指定需要并行运行的实例数量：

- **默认值**：`team_size=1`，即只运行一个实例（普通模式）
- **设置 `team_size=N`**：OxyGent 会自动创建 N 个相同配置的智能体实例，并行处理同一查询
- 所有实例独立运行，各自产出响应结果
- 系统自动聚合所有实例的输出，生成最终的综合答案

使用场景包括：
- 需要更全面、更高质量的回答时
- 希望降低单次回答的随机性和偏差时
- 对回答的可靠性要求较高的业务场景

## 基本用法

如果您需要生成多个相同的智能体，您可以使用`team_size`参数快速复制智能体。

```python
oxy.ReActAgent(
    name="time_agent",
    desc="A tool for time query",
    tools=["time_tools"],
    llm_model="default_llm",
    team_size=2,
),
```

`team_size`目前仅能复制较为简单的智能体，之后我们会支持更完备的智能体复制。

## 完整的可运行样例

以下是一个使用 `team_size` 实现 Mixture of Agents 的完整示例。在这个例子中，我们创建了一个 `ChatAgent`，并设置 `team_size=4`，表示同时运行 4 个实例来回答同一个问题：

```python
"""Demo: Mixture of Agents (MoA) via the team_size parameter.

Setting team_size=N on an agent causes N parallel instances to process
the same query concurrently, producing an ensemble of responses that
are aggregated into a single answer.
"""

import asyncio
import os

from oxygent import MAS, oxy

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.7},
    ),
    oxy.ChatAgent(
        name="qa_agent",
        llm_model="default_llm",
        # MoA: 4 parallel instances process the same query and results are aggregated
        team_size=4,
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="What is the Agent?")


if __name__ == "__main__":
    asyncio.run(main())
```

### 运行说明

1. 确保已配置 `.env` 文件中的 `DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL` 和 `DEFAULT_LLM_MODEL_NAME` 环境变量
2. 运行脚本后，OxyGent 会自动将 `qa_agent` 复制为 4 个并行实例
3. 当用户发送查询时，4 个实例同时处理，最终聚合为一个综合回答
4. 适当提高 `temperature`（如示例中的 0.7）可以增加各实例回答的多样性，从而获得更全面的聚合结果

[上一章：创建简单的多agent系统](./multi-agent-system.md)
[下一章：并行调用agent](./parallel.md)
[回到首页](../readme.md)

---

## 相关示例

- [Mixture of Agents示例](../../examples/agents/demo_mixture_of_agents.md) — 演示team_size参数实现MoA模式的完整用法
- [并行智能体示例](../../examples/agents/demo_parallel.md) — 演示ParallelAgent的并行执行，与MoA形成对比
