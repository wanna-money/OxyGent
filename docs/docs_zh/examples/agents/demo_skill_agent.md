# 技能代理

**源文件:** `examples/agents/demo_skill_agent.py`

## 概述

本示例展示了 `SkillAgent`，它从本地目录加载并执行预定义的技能文件。技能是模块化、可复用的任务定义，代理可以发现并调用它们。结合文件查看和 shell 执行工具，`SkillAgent` 可以读取技能定义并执行。这种模式非常适合构建可扩展的代理，只需添加新的技能文件即可扩展其能力。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包
- 包含技能定义文件的 `./skills` 目录（或包含技能文件夹的父目录）

## 运行方式

```bash
python -m examples.agents.demo_skill_agent
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量 |
| `file_tools` | `preset_tools.file_tools` | 内置文件操作工具（提供 `view_text_file` 等） |
| `shell_tools` | `preset_tools.shell_tools` | 内置 shell 执行工具（提供 `execute_shell_command` 等） |
| `skill_agent` | `SkillAgent` | `llm_model="default_llm"`；`tools=["view_text_file", "execute_shell_command"]`；`skills=["./skills"]` |

**`SkillAgent` 的关键参数：**
- `tools=["view_text_file", "execute_shell_command"]` -- 必需的基础工具，使代理能够读取技能文件和执行命令。这些是来自 `file_tools` 和 `shell_tools` FunctionHub 实例的特定工具名称。
- `skills=["./skills"]` -- 指向技能目录的路径列表。每个路径可以是单个技能文件夹或包含多个技能文件夹的父目录。

### 入口函数

```python
await mas.start_web_service(first_query="What skills do you have?")
```

启动 Web 服务，初始查询为询问代理其可用技能的元查询。

## 核心概念

- **`SkillAgent`** -- 一个专门的代理，从文件系统中发现并执行技能定义。技能从 `skills` 参数指定的路径加载。
- **技能目录** -- 技能文件存储在 `./skills`（或任何指定路径）中。每个技能通常定义一个任务，包含指令、所需工具和执行步骤。
- **工具组合** -- `SkillAgent` 在其 `tools` 列表中需要特定的工具名称（而非工具组名称）。此处 `"view_text_file"` 和 `"execute_shell_command"` 分别是从 `preset_tools.file_tools` 和 `preset_tools.shell_tools` 中提取的单个工具。
- **可扩展性** -- 可以通过在技能目录中创建新的技能文件来添加新功能，无需修改代理代码。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 初始查询 "What skills do you have?" 被发送。
3. `SkillAgent` 扫描 `./skills` 目录，发现可用的技能定义，并在响应中列出。
4. 用户随后可以通过名称或描述要求代理执行特定技能。
5. 代理使用 `view_text_file` 读取技能定义，使用 `execute_shell_command` 执行技能中的 shell 步骤。
