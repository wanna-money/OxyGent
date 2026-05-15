# SkillAgent
---
The position of the class is:


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

## Introduction

`SkillAgent` is a lightweight skill-aware agent that loads skills directly from specified directory paths. Each skill is defined by a `SKILL.md` file with frontmatter metadata (name, description). During initialization, the agent discovers skills from the configured paths and injects their metadata into the system prompt, giving the LLM awareness of available skills.

## Parameters


| Parameter | Type / Allowed value  | Default              | Description                                                                                                                         |
| --------- | --------------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `skills`  | `Optional[List[str]]` | `None`               | List of skill directory paths. Each path can point to a folder with `SKILL.md` or a parent directory containing skill subfolders.   |
| `prompt`  | `Optional[str]`       | `SYSTEM_PROMPT_SKILLS` | Overrides the default prompt with a skill-aware system prompt containing a `${skill_list}` placeholder.                           |

## Methods


| Method                            | Coroutine (async) | Return Value  | Purpose (concise)                                                                                 |
| --------------------------------- | ----------------- | ------------- | ------------------------------------------------------------------------------------------------- |
| `init()`                          | Yes               | `None`        | Discover skills from paths, build skill prompt, then call parent init.                            |
| `_discover_skills()`              | Yes               | `None`        | Scan configured paths for `SKILL.md` files and load metadata into `_skills_metadata`.             |
| `_build_skill_prompt()`           | Yes               | `None`        | Build formatted skill entries from discovered metadata for prompt injection.                       |
| `_before_execute(oxy_request)`    | Yes               | `OxyRequest`  | Inject the `skill_list` variable into the request arguments before execution.                     |

## Properties


| Property       | Type        | Description                                   |
| -------------- | ----------- | --------------------------------------------- |
| `skills_count` | `int`       | Number of unique skills discovered.           |
| `skill_names`  | `List[str]` | Sorted list of all discovered skill names.    |

## Inherited
 Please refer to the [ReActAgent](./react_agent.md) class for inherited parameters and methods.

## Usage

A simple usage of `SkillAgent` is like:

```python
oxy.SkillAgent(
    name="skill_agent",
    desc="An agent with skill awareness",
    llm_model="default_llm",
    skills=["./skills/weather", "./skills/code_review"],
    tools=["time_tools"],
),
```

Each skill directory should contain a `SKILL.md` file with frontmatter:

```markdown
---
name: weather
description: Query current weather for any city
---

Instructions for using the weather skill...
```
