# 如何选择智能体？

OxyGent提供了很多种预设智能体，这些智能体足以帮助您完成基础的MAS构建，以下是简要介绍：

## `oxy.ChatAgent`

`oxy.ChatAgent`是最基础的会话智能体，功能和内部的LLM大致相同。它支持多轮对话记忆管理、自定义提示词配置以及向LLM传递自定义参数，适合作为简单对话场景的首选或复杂系统中的基础组件。

**适用场景：** 问答系统、客服机器人、个人助手、内容生成（文案/摘要）、原型开发与概念验证。

**不适用场景：** 需要复杂推理规划、多步骤工作流或并行任务处理的场景，请使用 ReActAgent、WorkflowAgent 或 ParallelAgent。

| 参数               | 类型  | 描述             | 默认值                          |
|-------------------|-------|-----------------|-------------------------------|
| `name`            | str   | 智能体名称        | 必填                          |
| `desc`            | str   | 智能体描述        | 必填                          |
| `llm_model`       | str   | 使用的语言模型标识符 | 必填                          |
| `prompt`          | str   | 系统提示词        | `"You are a helpful assistant."` |
| `short_memory_size` | int | 短期记忆大小      | 继承自 LocalAgent              |

```python
    oxy.ChatAgent(
        name="planner_agent",
        desc="An agent capable of making plans",
        llm_model="default_llm",
        prompt="""
            For a given goal, create a simple and step-by-step executable plan. \
            The plan should be concise, with each step being an independent and complete functional module—not an atomic function—to avoid over-fragmentation. \
            The plan should consist of independent tasks that, if executed correctly, will lead to the correct answer. \
            Ensure that each step is actionable and includes all necessary information for execution. \
            The result of the final step should be the final answer. Make sure each step contains all the information required for its execution. \
            Do not add any redundant steps, and do not skip any necessary steps.
        """.strip(),
    )
```

## `oxy.WorkflowAgent`

在Chat的基础上增加[工作流](../advanced/workflow.md)，可以自定义内部流程走向的Agent。

```python
    oxy.WorkflowAgent(
        name='search_agent',
        desc='一个可以查询数据的工具',
        sub_agents=['ner_agent', 'nen_agent'],
        func_workflow=data_workflow,
        llm_model='default_llm',
    )
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | 必填 | 智能体名称 |
| `desc` | str | `""` | 智能体描述 |
| `func_workflow` | Callable | `None` | 自定义工作流函数 |
| `sub_agents` | list[str] | `[]` | 可调用的子智能体名称 |

## `oxy.ReActAgent`

一种支持[规划、执行、观察、纠错重试](https://www.promptingguide.ai/zh/techniques/react)的agent，适合进行复杂的工作, 常常作为master_agent。

```python
    oxy.ReActAgent(
        name="master_agent",
        sub_agents=["knowledge_agent", "find_agent", "search_agent"],
        is_master=True,
        llm_model="default_llm",
    )
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | 必填 | 智能体名称 |
| `desc` | str | `""` | 智能体描述 |
| `llm_model` | str | `"default_llm"` | LLM 模型名称 |
| `max_react_rounds` | int | `16` | 最大推理-行动轮数 |
| `trust_mode` | bool | `False` | 是否启用 Trust Mode 输出元数据 |
| `is_discard_react_memory` | bool | `True` | 每次新查询是否清空推理记忆 |
| `func_parse_llm_response` | Callable | `None` | 自定义 LLM 输出解析函数 |
| `func_reflexion` | Callable | `None` | 自定义反思函数 |

ReActAgent包含一些独特的可调节参数，包括：

+ `max_react_rounds: int `：最大react轮数
+ `trust_mode: bool`：是否[提供响应元数据](../advanced/trust-mode.md)
+ `func_parse_llm_response: Optional[Callable[[str], LLMResponse]]` ：[处理LLM输出](../advanced/handle-output.md)

## `oxy.SSEOxyGent`

支持[分布式](../multi-agent/distributed.md)的agent。

```python
    oxy.SSEOxyGent(
        name='math_agent',
        desc='一个可以查询圆周率的工具',
        server_url='http://127.0.0.1:8081'
    )
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | 必填 | 智能体名称 |
| `desc` | str | `""` | 智能体描述 |
| `server_url` | str | 必填 | 远程 MAS 的 URL 地址 |

## `oxy.ParallelAgent`

支持[并行](../multi-agent/parallel.md)的agent。

```python
    oxy.ParallelAgent(
        name="analyzer",
        desc="A tool that analyze markdown document",
        permitted_tool_name_list=["text_summarizer", "data_analyser", "document_checker"]
    ),
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | 必填 | 智能体名称 |
| `desc` | str | `""` | 智能体描述 |
| `permitted_tool_name_list` | list[str] | `[]` | 并行执行的智能体/工具名称列表 |

## `oxy.PlanAndSolveAgent`

一种将规划与执行分离的两阶段Agent。PlanAndSolveAgent 协调一个规划器（通常是 ChatAgent）和一个执行器（通常是 ReActAgent），规划器以 JSON 格式生成分步计划，执行器逐步完成任务。

```python
    oxy.PlanAndSolveAgent(
        name="master_agent",
        is_master=True,
        planner="planner_agent",
        solver="solver_agent",
    )
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | 必填 | 智能体名称 |
| `planner` | str | `"planner_agent"` | 规划器智能体名称 |
| `solver` | str | `"executor_agent"` | 执行器智能体名称 |
| `max_replan_rounds` | int | `30` | 最大重规划轮数 |

## `oxy.RAGAgent`

支持检索增强生成（Retrieval-Augmented Generation）的Agent。通过自定义的 `func_retrieve_knowledge` 异步函数检索外部知识，并将检索结果通过命名占位符（如 `${knowledge}`）注入到 Agent 的提示词中。

```python
    async def my_retrieve(oxy_request):
        # 在此处实现您的检索逻辑，例如查询向量数据库
        return "检索到的知识内容"

    oxy.RAGAgent(
        name="rag_agent",
        desc="A knowledge-augmented agent",
        func_retrieve_knowledge=my_retrieve,
        knowledge_placeholder="knowledge",
        prompt="Based on the following knowledge: ${knowledge}\nPlease answer the user's question.",
        llm_model="default_llm",
    )
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | 必填 | 智能体名称 |
| `desc` | str | 必填 | 智能体描述 |
| `func_retrieve_knowledge` | Callable | 必填 | 知识检索函数 |
| `knowledge_placeholder` | str | `"knowledge"` | Prompt 中的知识占位符名称 |
| `prompt` | str | 必填 | 包含 `${knowledge}` 占位符的提示词 |

## `oxy.ShellUseAgent`

通过 SSH 连接到远程主机并自主执行 Shell 命令来完成任务的Agent。适用于服务器运维、自动化部署等场景。

```python
    oxy.ShellUseAgent(
        name="shell_agent",
        desc="An agent that can execute shell commands on remote hosts",
        tools=["ssh_tools"],
        max_react_rounds=64,
        is_discard_react_memory=False,
        auth_info={
            "hostname": "your_host",
            "port": 22,
            "username": "your_username",
            "password": "your_password",
        },
    )
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | 必填 | 智能体名称 |
| `desc` | str | `""` | 智能体描述 |
| `auth_info` | dict | `{}` | SSH 连接参数（hostname, port, username, password） |
| `max_react_rounds` | int | `64` | 最大推理-行动轮数 |

## `oxy.SkillAgent`

能够从目录（如 `./skills`）中动态加载技能定义的Agent。技能是可复用的结构化任务模板，Agent 可以自动发现并调用这些技能。

```python
    oxy.SkillAgent(
        name="skill_agent",
        desc="An agent that can discover and execute skills",
        tools=["file_tools", "shell_tools"],
        llm_model="default_llm",
    )
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | 必填 | 智能体名称 |
| `desc` | str | `""` | 智能体描述 |
| `skills` | list[str] | `None` | 技能目录路径列表 |

[上一章：预设提示词](./select-prompt.md)
[下一章：注册一个工具](../tools/register-tool.md)
[回到首页](../readme.md)

---

## 相关示例

- [单 Agent 示例](../../examples/agents/demo_single_agent.md) — 最简单的 ChatAgent 配置
- [ReAct Agent 示例](../../examples/agents/demo_react_agent.md) — 带反思机制的 ReActAgent
- [工作流 Agent 示例](../../examples/agents/demo_workflow_agent.md) — WorkflowAgent 编排子 Agent
- [并行 Agent 示例](../../examples/agents/demo_parallel.md) — ParallelAgent 并行执行
- [计划-求解 Agent 示例](../../examples/agents/demo_plan_and_solve_agent.md) — PlanAndSolveAgent 的两阶段规划执行
- [RAG Agent 示例](../../examples/agents/demo_rag_agent.md) — 检索增强生成 Agent
- [Shell 操作 Agent 示例](../../examples/agents/demo_shell_use_agent.md) — ShellUseAgent 远程执行命令
- [技能 Agent 示例](../../examples/agents/demo_skill_agent.md) — SkillAgent 动态加载技能
- [层级式多 Agent 示例](../../examples/agents/demo_hierarchical_agents.md) — 主从 Agent 层级架构
- [异构 Agent 协作示例](../../examples/agents/demo_heterogeneous_agents.md) — 混合不同类型的 Agent
- [分布式 Agent 示例](../../examples/distributed/app_master_agent.md) — SSEOxyGent 分布式部署
