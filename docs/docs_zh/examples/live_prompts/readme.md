# 动态提示词示例

本目录包含了 OxyGent 动态提示词（Live Prompt）系统的使用示例，展示如何实现提示词的热加载，在运行时更新提示词而无需重启应用。

---

## 示例列表

### 多 Agent 系统中的动态提示词

**文件:** `examples/live_prompts/demo.py`

演示了在一个四 Agent 层级系统中使用动态提示词。三个专业子 Agent（`time_agent`、`file_agent`、`math_agent`）由一个主 ReActAgent 协调。每个 Agent 展示了不同的提示词策略：`time_agent` 设置 `use_live_prompt=False` 并定义了代码级提示词，意味着它始终使用代码中的静态提示词；`file_agent` 同样设置 `use_live_prompt=False`，仅使用其代码级 prompt 参数；`math_agent` 保持 `use_live_prompt` 为默认值（启用），因此其提示词可以在运行时通过动态提示词系统进行更新；`master_agent` 同样使用动态提示词。全局 LLM 模型通过 `Config.set_agent_llm_model()` 配置。该示例展示了如何在同一个多 Agent 系统中混合使用静态和动态提示词策略。

**核心组件:**
- `HttpLLM` -- 语言模型后端
- `Config.set_agent_llm_model` -- 全局 LLM 配置
- `preset_tools` -- 为子 Agent 提供的 time_tools、file_tools、math_tools
- `ReActAgent` (x4) -- 主 Agent 和三个子 Agent，各自使用不同的 `use_live_prompt` 设置

**[详细文档 →](./demo.md)**

---

### 动态提示词 Key 共享

**文件:** `examples/live_prompts/demo_live_prompt.py`

演示了多个 Agent 如何通过 `prompt_key` 参数共享同一个动态提示词。定义了三个 ChatAgent：`chat_agent1` 和 `chat_agent2` 都设置了 `prompt_key="my_prompt"`，意味着它们会在提示词存储中查找同一条动态提示词条目，共享相同的动态管理提示词。`chat_agent3` 设置 `use_live_prompt=False`，完全退出动态提示词系统，仅使用其代码级的静态提示词。该示例展示了 `prompt_key` 如何实现集中式提示词管理 -- 更新提示词存储中的 `my_prompt` 条目将同时更新所有引用它的 Agent 的提示词。

**核心组件:**
- `HttpLLM` -- 语言模型后端
- `ChatAgent` (x3) -- 三个 Agent 演示 prompt_key 共享和 use_live_prompt 开关
- `prompt_key` -- 用于集中式动态提示词查找的共享键
- `use_live_prompt` -- 控制是否启用动态提示词系统的标志

**[详细文档 →](./demo_live_prompt.md)**
