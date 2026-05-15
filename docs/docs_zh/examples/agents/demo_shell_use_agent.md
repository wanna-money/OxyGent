# Shell 使用代理（远程 SSH）

**源文件:** `examples/agents/demo_shell_use_agent.py`

## 概述

本示例展示了 `ShellUseAgent`，它通过 SSH 连接到远程机器并自主执行 shell 命令。它使用专门的系统提示词（`SYSTEM_PROMPT_SHELL_USE`）和 OxyGent 内置的 `preset_tools.ssh_tools`，在远程服务器上执行任务，例如克隆 Git 仓库并运行 Python 脚本。这种模式非常适合 DevOps 自动化、服务器管理以及任何需要 LLM 推理引导的远程命令执行场景。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包
- 在指定主机名/端口上可达的 SSH 服务器，且凭证有效
- 远程服务器应已安装 Git 和 Python（用于演示任务）

## 运行方式

```bash
python -m examples.agents.demo_shell_use_agent
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量 |
| `ssh_tools` | `preset_tools.ssh_tools` | 内置 SSH 工具 FunctionHub，用于执行远程命令 |
| `shell_use_agent` | `ShellUseAgent` | `auth_info`（SSH 凭证）；`prompt=SYSTEM_PROMPT_SHELL_USE`；`tools=["ssh_tools"]`；`max_react_rounds=64`；`is_discard_react_memory=False` |

**`auth_info`** 包含 SSH 连接详情：

```python
auth_info={
    "hostname": "127.0.0.1",
    "port": 22,
    "username": "root",
    "password": "admin",
}
```

**关键代理参数：**
- `prompt=SYSTEM_PROMPT_SHELL_USE` -- 从 `oxygent.prompts` 导入的专门系统提示词，指导代理如何有效地与 shell 环境交互。
- `max_react_rounds=64` -- 允许最多 64 轮 ReAct 推理/行动循环，以适应复杂的多步骤 shell 任务。
- `is_discard_react_memory=False` -- 在各轮之间保留所有 ReAct 推理历史，允许代理引用之前的命令和输出。

### 入口函数

```python
await mas.start_web_service(
    first_query="Please run the demo.py from https://github.com/jd-opensource/OxyGent.git"
)
```

启动 Web 服务，任务需要克隆仓库并运行脚本。

## 核心概念

- **`ShellUseAgent`** -- 专为远程 shell 交互设计的代理。它将 SSH 连接与 LLM 驱动的推理相结合，自主执行命令。
- **`auth_info`** -- 直接传递给代理的 SSH 连接凭证。支持 `hostname`、`port`、`username` 和 `password`。
- **`SYSTEM_PROMPT_SHELL_USE`** -- 来自 `oxygent.prompts` 的内置提示词，专为 shell 交互场景定制，为代理提供关于命令执行、错误处理和任务完成的指导。
- **`max_react_rounds`** -- 代理可以执行的最大 ReAct 循环次数。Shell 任务通常需要许多步骤（克隆、安装依赖、运行、调试错误），因此需要较高的限制。
- **`is_discard_react_memory`** -- 设为 `False` 时，代理保留其推理和命令输出的完整历史，这对于后续命令依赖先前结果的 shell 任务至关重要。
- **`preset_tools.ssh_tools`** -- 内置工具，用于通过 SSH 执行命令、捕获输出和管理远程会话。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 查询指示代理从 OxyGent GitHub 仓库运行 `demo.py`。
3. 代理推理各步骤并执行 SSH 命令：
   - 在远程服务器上克隆 Git 仓库。
   - 导航到项目目录。
   - 安装所需依赖。
   - 运行 `demo.py`。
4. 每个命令的输出被观察，代理根据结果或错误调整下一步操作。
5. 最终响应总结执行结果。

**注意：** 默认的 `auth_info` 使用 `127.0.0.1` 和 `root/admin` 凭证。运行前必须将其更新为你实际的 SSH 服务器配置。
