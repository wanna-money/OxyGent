# 运行时 Oxy 管理

**源文件:** `examples/advanced/demo_oxy_manage.py`

## 概述

本示例演示了如何使用 `oxy_manage_tools` 在运行中的 MAS 中动态创建、移动和删除 Agent 与工具。示例中配置了一个专用的 "doctor_agent",它装备了 `oxy_manage_tools`,充当系统管理员的角色 -- 能够查看当前组织树、创建新 Agent、为其分配工具、在不同父节点之间移动 Oxy 节点,以及移除不再需要的 Agent,所有操作均无需重启系统。

## 前置条件

- 环境变量: `DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`

## 运行方式

```bash
python -m examples.advanced.demo_oxy_manage
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name`(来自环境变量) |
| `math_tools` | `FunctionHub` | 预置数学计算工具 |
| `time_tools` | `FunctionHub` | 预置时间查询工具 |
| `time_agent` | `ReActAgent` | `desc="A tool that can query the time"`、`tools=["time_tools"]` |
| `file_tools` | `FunctionHub` | 预置文件系统操作工具 |
| `file_agent` | `ReActAgent` | `desc="A tool that can operate the file system"`、`tools=["file_tools"]` |
| `oxy_manage_tools` | `FunctionHub` | 预置运行时 Agent/工具组织管理工具 |
| `doctor_agent` | `ReActAgent` | `desc="A system administrator..."`、`tools=["oxy_manage_tools"]` |
| `master_agent` | `ReActAgent` | `is_master=True`、`sub_agents=["time_agent", "file_agent", "doctor_agent"]` |

### 入口函数

`main()` 创建 `MAS` 上下文并启动 Web 服务,通过 `first_query` 列表传入四条顺序执行的命令。`first_query` 参数接受 `list[str]`,每个字符串在 Web UI 加载时按顺序作为初始对话轮次依次执行。

## 核心概念

- **oxy_manage_tools** -- 一个预置的 FunctionHub,提供在运行时检查和修改 Agent/工具组织树的工具。它支持创建新的 Oxy 实例、删除已有实例、在父 Agent 之间移动 Oxy 节点,以及查询当前组织结构 -- 所有操作均在 MAS 运行期间完成。
- **运行时组织结构 CRUD** -- 传统多 Agent 架构在代码中静态定义组织结构。借助 `oxy_manage_tools`,组织结构变为动态的:可以通过自然语言指令让 doctor_agent 实时添加、删除或重新组织 Agent 和工具。
- **first_query 与 list[str]** -- `start_web_service()` 方法的 `first_query` 参数既可以接受单个字符串,也可以接受字符串列表。当传入列表时,每个条目按顺序作为初始查询依次执行,从而实现在 Web UI 打开时自动运行的多步骤脚本化演示。

## 预期行为

1. **创建 math_agent** -- doctor_agent 创建一个名为 `math_agent` 的新 ReActAgent,描述为"A tool that can perform mathematical calculations",为其分配 `math_tools`,并将其作为 `master_agent` 的子 Agent 挂载。此步骤完成后,组织结构中新增一个具备数学计算能力的 Agent。
2. **测试 math_agent** -- master_agent 将查询"What is 2 raised to the power of 9?"委派给新创建的 `math_agent`,后者使用 `math_tools` 计算并返回 `512`。
3. **重新组织时间工具** -- doctor_agent 将 `get_current_time` Oxy 从 `time_agent` 下移动到 `master_agent` 下,然后从组织结构中删除 `time_agent`。这展示了运行时重新组织的能力 -- 工具可以重新分配,冗余的 Agent 可以被移除。
4. **测试重组后的时间工具** -- master_agent 使用现在直接挂载在其下的 `get_current_time` 工具回答"what time it is now",确认重新组织操作成功。
