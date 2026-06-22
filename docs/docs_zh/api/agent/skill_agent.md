# SkillAgent
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

`SkillAgent` 是一个轻量级的技能感知 Agent，直接从指定的目录路径加载技能。每个技能由一个包含 frontmatter 元数据（名称、描述）的 `SKILL.md` 文件定义。在初始化过程中，Agent 从配置的路径发现技能，并将其元数据注入系统提示词，使 LLM 能够感知可用的技能。

## 参数


| 参数       | 类型 / 允许的值           | 默认值                   | 描述                                                                                                                      |
| --------- | --------------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `skills`  | `Optional[list[str]]` | `None`               | 技能目录路径列表。每个路径可以指向包含 `SKILL.md` 的文件夹，或包含技能子文件夹的父目录。  |
| `prompt`  | `Optional[str]`       | `SYSTEM_PROMPT_SKILLS` | 使用包含 `${skill_list}` 占位符的技能感知系统提示词覆盖默认提示词。                                                     |

## 方法


| 方法                              | 协程（async）        | 返回值          | 用途（简要）                                                                            |
| --------------------------------- | ----------------- | ------------- | ------------------------------------------------------------------------------------------------- |
| `init()`                          | 是                | `None`        | 从路径发现技能、构建技能提示词，然后调用父类 init。                                          |
| `_discover_skills()`              | 是                | `None`        | 扫描配置的路径以查找 `SKILL.md` 文件，并将元数据加载到 `_skills_metadata` 中。               |
| `_build_skill_prompt()`           | 是                | `None`        | 从已发现的元数据构建格式化的技能条目，用于提示词注入。                                        |
| `_before_execute(oxy_request)`    | 是                | `OxyRequest`  | 在执行之前将 `skill_list` 变量注入到请求参数中。                                            |

## 属性


| 属性             | 类型          | 描述                                        |
| -------------- | ----------- | --------------------------------------------- |
| `skills_count` | `int`       | 已发现的唯一技能数量。                          |
| `skill_names`  | `list[str]` | 所有已发现技能名称的排序列表。                    |

## 继承
 请参阅 [ReActAgent](./react_agent.md) 类以了解继承的参数和方法。

## 使用方式

`SkillAgent` 的简单用法如下：

```python
oxy.SkillAgent(
    name="skill_agent",
    desc="An agent with skill awareness",
    llm_model="default_llm",
    skills=["./skills/weather", "./skills/code_review"],
    tools=["time_tools"],
),
```

每个技能目录应包含一个带有 frontmatter 的 `SKILL.md` 文件：

```markdown
---
name: weather
description: Query current weather for any city
---

Instructions for using the weather skill...
```
