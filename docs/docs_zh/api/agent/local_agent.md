# LocalAgent
---
该类在类层次结构中的位置：


```markdown
[Oxy](./base_oxy.md)
├── [BaseFlow](./base_flow.md)
│   └── [BaseAgent](./base_agent.md)
│       ├── [LocalAgent](./local_agent.md)
│       │   ├── [ChatAgent](./chat_agent.md)
│       │   │   └── [RAGAgent](./rag_agent.md)
│       │   ├── [ReActAgent](./react_agent.md)
│       │   │   ├── [ShellUseAgent](./shell_use_agent.md)
│       │   │   └── [SkillAgent](./skill_agent.md)
│       │   ├── [ParallelAgent](./parallel_agent.md)
│       │   ├── [WorkflowAgent](./workflow_agent.md)
│       │   └── [PlanAndSolveAgent](./plan_and_solve_agent.md)
│       └── [RemoteAgent](./remote_agent.md)
│           ├── [SSEOxyGent](./sse_oxy_agent.md)
│           └── [A2AClientAgent](./a2a_client_agent.md)
└── [BaseTool](../tools/base_tools.md)
```

---

## 简介

`LocalAgent` 是具有工具管理和记忆能力的本地 Agent。

该 Agent 扩展了 BaseAgent，提供以下本地执行能力：
- 动态工具发现与检索
- 子 Agent 委托和层级支持
- 对话记忆管理
- LLM 模型集成与提示词模板化
- 基于团队的并行执行支持

## 参数


| 参数                                 | 类型 / 允许的值        | 默认值                                 | 描述                                                            |   
| ---------------------------------- | -------------------- | ------------------------------ | ----------------------------------------------------------- |
| `llm_model`                        | `str`                | `Config.get_agent_llm_model()` | 该 Agent 调用的 LLM 标识符。                                               |
| `prompt`                           | `Optional[str]`      | `Config.get_agent_prompt()`    | 基础系统提示词模板。                                                        |
| `prompt_key`                       | `Optional[str]`      | `None`                         | 实时提示词查询的键名；默认为 `{agent_name}_prompt`。                          |
| `use_live_prompt`                  | `bool`               | `Config.get_live_prompt_is_active()` | 是否使用实时提示词热重载系统。                                          |
| `additional_prompt`                | `Optional[str]`      | `""`                           | 用户提供的文本，追加到提示词末尾。                                             |
| `tools_placeholder`                | `str`                | `"tools_description"`          | 提示词模板中用于注入工具描述的占位符键名。                                       |
| `sub_agents`                       | `list`               | `[]`                           | 该 Agent 可委托的其他 Agent 名称。                                          |
| `tools`                            | `list`               | `[]`                           | 显式可用的工具。                                                           |
| `except_tools`                     | `list`               | `[]`                           | 显式禁止的工具。                                                           |
| `banks`                            | `list`               | `[]`                           | 该 Agent 可用的 Bank 工具（BankTool / BankClient）。                        |
| `is_sourcing_tools`                | `bool`               | `False`                        | 启用动态工具检索而非静态列表。                                               |
| `is_retain_subagent_in_toolset`    | `bool`               | `False`                        | 在返回给 LLM 的工具集中保留子 Agent 可见。                                    |
| `top_k_tools`                      | `int`                | `10`                           | 检索工具的最大数量。                                                        |
| `is_retrieve_even_if_tools_scarce` | `bool`               | `True`                         | 当前工具池较少时仍执行检索。                                                  |
| `short_memory_size`                | `int`                | `Config.get_agent_short_memory_size()` | 短期记忆中保留的对话轮数。                                            |
| `intent_understanding_agent`       | `Optional[str]`      | `None`                         | 用于改写查询以进行工具检索的 Agent。                                          |
| `is_retain_master_short_memory`    | `bool`               | `False`                        | 是否同时附加用户-主 Agent 会话记忆。                                          |
| `is_attachment_processing_enabled` | `bool`               | `True`                         | 是否将附件注入到查询中。                                                     |
| `is_multimodal_supported`          | `bool`               | `False`                        | 所选 LLM 是否能处理图片。                                                   |
| `team_size`                        | `int`                | `1`                            | 并行运行的克隆实例数量（混合 Agent 模式）。                                     |   

## 方法


| 方法                                                            | 协程（async）        | 返回值          | 用途（简要）                                                                        |   
| ------------------------------------------------------------- | ----------------- | ------------- | --------------------------------------------------------------------------------- |
| `__init__(**kwargs)`                                          | 否                | `None`        | 初始化对象并验证 `llm_model` 已设置。                                                |
| `_init_available_tool_name_list()`                            | 否                | `None`        | 构建允许的工具列表（tools、子 Agent、hubs、MCP 客户端、banks）。                       |
| `__deepcopy__(memo)`                                          | 否                | `LocalAgent`  | 深拷贝 Agent，同时保持共享的 MAS 引用。                                               |
| `reload_prompt()`                                             | 是                | `bool`        | 从实时提示词系统热重载提示词。                                                        |
| `init()`                                                      | 是                | `None`        | 一次性初始化；执行工具发现、多模态检查和可选的团队生成。                                   |
| `_get_history(oxy_request, is_get_user_master_session=False)` | 是                | `Memory`      | 从 Elasticsearch 检索近期对话历史。                                                  |
| `_get_llm_tool_desc_list(oxy_request, query)`                 | 是                | `str`         | 为 LLM 组装工具描述（静态列表或检索结果）。                                            |
| `_build_instruction(arguments)`                               | 否                | `str`         | 替换提示词中的 `${var}` 占位符。                                                     |
| `_pre_process(oxy_request)`                                   | 是                | `OxyRequest`  | 在处理前附加短期记忆（以及可选的主 Agent 记忆）。                                       |
| `_before_execute(oxy_request)`                                | 是                | `OxyRequest`  | 注入 `tools_description`、`additional_prompt` 和多模态附件。                           |
| `_execute(oxy_request)`                                       | 是                | `OxyResponse` | **抽象方法** - 具体子类必须实现实际执行逻辑。                                           |   


## 继承
 请参阅 [BaseAgent](./base_agent.md) 类以了解继承的参数和方法。

## 使用方式

`LocalAgent` 类必须被继承使用。
