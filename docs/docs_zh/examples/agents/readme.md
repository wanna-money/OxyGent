# Agent 示例

本目录包含了 OxyGent 中各类 Agent 类型和协作模式的示例。每个示例都是一个独立的脚本，设置好所需的环境变量后即可直接运行。

## 示例列表

### 单 Agent
**文件:** `examples/agents/demo_single_agent.py`

演示了最简单的 Agent 配置：一个由 HttpLLM 驱动的 ChatAgent。该示例展示了 `func_process_input` 钩子（在用户查询到达 LLM 之前追加额外指令）和 `func_format_output` 钩子（在响应前添加前缀标签）的用法。通过 `Config.set_agent_short_memory_size(7)` 全局配置了短期记忆，使 Agent 能保留最近 7 轮的对话上下文。

**核心组件:** HttpLLM, ChatAgent, func_process_input, func_format_output

**[详细文档 →](./demo_single_agent.md)**

---

### 流式输出 Chat Agent
**文件:** `examples/agents/demo_chat_agent_stream.py`

展示了如何通过在 HttpLLM 上设置 `llm_params={"stream": True}` 来启用 ChatAgent 的流式（逐 token）输出。通过 `Config.set_message_is_show_in_terminal(True)` 开启了终端中流式 token 的显示。这是通过 Web UI 获取实时流式响应所需的最小配置。

**核心组件:** HttpLLM (stream), ChatAgent

**[详细文档 →](./demo_chat_agent_stream.md)**

---

### 带反思机制的 ReAct Agent
**文件:** `examples/agents/demo_react_agent.py`

介绍了带有自定义 `func_reflexion` 回调的 ReActAgent，该回调在每轮推理-行动循环后验证 Agent 的输出。在本示例中，反思函数使用正则表达式检查输出是否为纯数字；如果不是，则返回纠正反馈（"仅回答数字"），迫使 Agent 重新尝试。这种模式适用于对输出格式有严格约束的场景。

**核心组件:** HttpLLM, ReActAgent, func_reflexion

**[详细文档 →](./demo_react_agent.md)**

---

### RAG Agent
**文件:** `examples/agents/demo_rag_agent.py`

演示了 RAGAgent 的使用，它通过自定义的 `func_retrieve_knowledge` 异步函数支持检索增强生成。检索到的知识通过命名占位符（`${knowledge}`）注入到 Agent 的提示词中。本示例中检索函数返回了一个硬编码的圆周率值，但在生产环境中可以对接向量数据库或搜索引擎。

**核心组件:** HttpLLM, RAGAgent, func_retrieve_knowledge, knowledge_placeholder

**[详细文档 →](./demo_rag_agent.md)**

---

### 工作流 Agent
**文件:** `examples/agents/demo_workflow_agent.py`

展示了 WorkflowAgent 的使用，它通过一个 Python 工作流函数来编排子 Agent、LLM 和工具。工作流函数接收 OxyRequest，可以通过 `oxy_request.call()` 按名称调用任何已注册的 Oxy 组件。本示例串联了一次 ChatAgent 调用、一次直接 LLM 调用和一次 MCP 工具调用（calc_pi），以计算指定位数的圆周率。同时还演示了如何访问短期记忆和发送中间消息。

**核心组件:** HttpLLM, StdioMCPClient, ChatAgent, WorkflowAgent, func_workflow

**[详细文档 →](./demo_workflow_agent.md)**

---

### 层级式多 Agent
**文件:** `examples/agents/demo_hierarchical_agents.py`

构建了一个层级式多 Agent 系统，由一个主 ReActAgent 将任务委派给专业化的子 Agent。主 Agent 根据查询内容将请求路由到 `time_agent`（配备时间 MCP 工具）或 `file_agent`（配备文件系统 MCP 工具）。每个子 Agent 本身也是一个拥有独立工具集的 ReActAgent。该模式展示了如何通过 Agent 树结构分解复杂任务。

**核心组件:** HttpLLM, StdioMCPClient (x2), ReActAgent (x3)

**[详细文档 →](./demo_hierarchical_agents.md)**

---

### 异构 Agent 协作
**文件:** `examples/agents/demo_heterogeneous_agents.py`

演示了在同一个主 Agent 下混合使用不同类型的 Agent。一个 ReActAgent 作为主 Agent，将任务委派给一个 ChatAgent（`QA_agent`，用于通用知识问答）和一个 WorkflowAgent（`time_agent`，通过编程式工作流处理时间查询）。这表明子 Agent 不必是相同类型——可以在一个层级结构中自由组合 ChatAgent、WorkflowAgent、ReActAgent 等不同类型的 Agent。

**核心组件:** HttpLLM, StdioMCPClient, ReActAgent, ChatAgent, WorkflowAgent

**[详细文档 →](./demo_heterogeneous_agents.md)**

---

### 并行 Agent
**文件:** `examples/agents/demo_parallel.py`

演示了 ParallelAgent 的使用，它将单个查询同时分发给多个专家 ChatAgent 并聚合其响应。四个领域专家（技术架构师、商业分析师、风险管理专家和法律顾问）同时对同一份商业方案进行评估。该模式非常适合需要多视角独立评估并行执行的分析场景。

**核心组件:** HttpLLM, ChatAgent (x4), ParallelAgent

**[详细文档 →](./demo_parallel.md)**

---

### 混合 Agent (MoA)
**文件:** `examples/agents/demo_mixture_of_agents.py`

通过 `team_size` 参数实现了混合 Agent（Mixture of Agents）模式。在 ChatAgent 上设置 `team_size=4` 会使 4 个并行实例同时处理同一查询，各自独立生成响应，然后自动聚合为一个最终答案。这种集成方法通过推理多样性提升了回答质量，无需定义多个不同的 Agent。

**核心组件:** HttpLLM, ChatAgent (team_size=4)

**[详细文档 →](./demo_mixture_of_agents.md)**

---

### 计划-求解 Agent
**文件:** `examples/agents/demo_plan_and_solve_agent.py`

展示了 PlanAndSolveAgent，这是一种将规划与执行分离的两阶段 Agent。一个 ChatAgent 作为规划器，以 JSON 格式生成和更新分步计划。一个 ReActAgent 作为执行器，使用预置的时间工具和文件工具逐步执行任务。PlanAndSolveAgent 负责协调规划和执行之间的循环，直到任务完成。

**核心组件:** HttpLLM, ChatAgent (规划器), preset_tools (time_tools, file_tools), ReActAgent (执行器), PlanAndSolveAgent

**[详细文档 →](./demo_plan_and_solve_agent.md)**

---

### Shell 操作 Agent
**文件:** `examples/agents/demo_shell_use_agent.py`

演示了 ShellUseAgent 的使用，它通过 SSH 连接到远程主机并自主执行 Shell 命令来完成任务。Agent 配置了 SSH 认证信息（主机名、端口、用户名、密码），并使用预置的 SSH 工具。通过设置 `max_react_rounds=64` 和 `is_discard_react_memory=False`，它可以执行长时间的多步操作，同时保留之前所有命令及其输出的完整上下文。

**核心组件:** HttpLLM, preset_tools.ssh_tools, ShellUseAgent, auth_info

**[详细文档 →](./demo_shell_use_agent.md)**

---

### 技能 Agent
**文件:** `examples/agents/demo_skill_agent.py`

介绍了 SkillAgent，它能够从目录（`.oxygent/skills`）中动态加载技能定义。技能是可复用的结构化任务模板，Agent 可以自动发现并调用这些技能。该 Agent 还配备了来自 preset_tools 的文件查看和 Shell 命令工具，使其能够读取技能文件并在技能执行过程中运行命令。

**核心组件:** HttpLLM, preset_tools (file_tools, shell_tools), SkillAgent, skills

**[详细文档 →](./demo_skill_agent.md)**

---

### 文档分析 Agent
**文件:** `examples/agents/demo_document_analysis_agent.py`

使用预置的 `document_tools` 配置了一个用于文档分析的 ReActAgent，支持处理和分析多种文档格式（PDF、Word、Excel 等）。HttpLLM 启用了流式输出以实现实时响应。这是将预置工具包与 ReActAgent 结合用于特定领域任务的实用示例。

**核心组件:** HttpLLM (stream), preset_tools.document_tools, ReActAgent

**[详细文档 →](./demo_document_analysis_agent.md)**

---

### 评估与进化（批处理）
**文件:** `examples/agents/demo_evaluate_and_evolve.py`

演示了用于 SFT（监督微调）数据质量审核的批处理模式。与其他启动 Web 服务的示例不同，本示例使用 `mas.start_batch_processing()` 并发评估多个数据样本。工作流程为：从 Elasticsearch 中检索 LLM 节点数据，将每个样本发送给 ChatAgent 按照预定义标准进行质量评估，解析 JSON 结果，过滤掉低质量样本，并将通过审核的数据写入 JSONL 文件用于训练。

**核心组件:** HttpLLM, ChatAgent, batch_processing, Elasticsearch

**[详细文档 →](./demo_evaluate_and_evolve.md)**
