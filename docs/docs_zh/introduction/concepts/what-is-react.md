# 什么是 ReAct？

ReAct（Reasoning and Acting）是一种让大语言模型交替进行推理和行动的范式，由 Yao et al. 在 2022 年的论文 *"ReAct: Synergizing Reasoning and Acting in Language Models"* 中提出。

---

## 核心思想

传统的 LLM 调用是"一问一答"：用户提问，模型直接回答。但面对需要查询外部信息或执行操作的任务时，仅靠模型自身的知识往往不够。

ReAct 的解决方案是让模型在"思考"和"行动"之间循环：

```
Thought  →  我需要查一下今天的天气
Action   →  调用 get_weather("北京")
Observation → 北京今天晴，25°C
Thought  →  用户问的是北京天气，我已经拿到结果了
Answer   →  北京今天天气晴朗，气温 25°C。
```

每一轮循环包含三个步骤：

1. **Thought（思考）**：模型分析当前状态，决定下一步该做什么。
2. **Action（行动）**：模型选择并调用一个工具，传入参数。
3. **Observation（观察）**：工具返回执行结果，模型读取后继续思考。

这个循环持续进行，直到模型认为已经获得足够信息，给出最终回答。

---

## OxyGent 中的 ReActAgent

OxyGent 的 `ReActAgent` 是 ReAct 范式的完整实现。它自动管理推理-行动循环，开发者只需声明智能体和工具：

```python
oxy_space = [
    oxy.HttpLLM(name="llm", ...),
    my_tools,  # FunctionHub 或 MCP 工具
    oxy.ReActAgent(
        name="agent",
        is_master=True,
        llm_model="llm",
        tools=["my_tools"],
        max_react_rounds=10,  # 最大循环次数
    ),
]
```

### 关键参数

| 参数 | 说明 |
|------|------|
| `max_react_rounds` | 最大推理-行动循环次数，防止无限循环 |
| `tools` | 智能体可用的工具名称列表 |
| `sub_agents` | 可调度的子智能体（子智能体也被视为一种"工具"） |
| `is_discard_react_memory` | 是否丢弃详细的 ReAct 记忆，节省上下文窗口 |
| `func_reflexion` | 自定义反思函数，对输出不满意时触发重做 |

### 与 ChatAgent 的区别

- `ChatAgent`：单轮 LLM 调用，不支持工具，适合纯对话。
- `ReActAgent`：多轮推理-行动循环，支持工具和子智能体调用，适合需要外部能力的复杂任务。

---

[返回首页](../readme.md)
