# Preset Tools

---
模块所在位置:

```
oxygent/preset_tools/
├── file_tools.py
├── http_tools.py
├── image_gen_tools.py
├── math_tools.py
├── oxy_manage_tools.py
├── python_tools.py
├── shell_tools.py
├── ssh_tools.py
├── string_tools.py
├── system_tools.py
└── time_tools.py
```

---

## 简介

`preset_tools` 包提供了 11 个内置的 `FunctionHub` 集合，涵盖常用的工具操作。每个模块导出一个 `FunctionHub` 实例，其中包含使用 `@tool` 装饰器修饰的函数，可以直接注册到 Agent 的 `oxy_space` 中。该包在导入时会自动发现并加载所有模块。

---

## file_tools

`FunctionHub(name="file_tools")` — 限定在当前工作目录下的文件操作。

| 工具            | 异步 | 参数                                    | 返回值  | 用途                                      |
| --------------- | ----- | --------------------------------------------- | ------- | -------------------------------------------- |
| `write_file`    | 否    | `path: str`, `content: str`                   | `str`   | 创建或覆盖文件。                  |
| `read_file`     | 否    | `path: str`                                   | `str`   | 读取并返回文件内容。            |
| `delete_file`   | 否    | `path: str`                                   | `str`   | 递归删除文件或目录。      |
| `view_text_file`| 否    | `file_path: str`, `ranges: Optional[list[int]]` | `str` | 查看文件内容，显示行号，支持可选行范围。 |

---

## http_tools

`FunctionHub(name="http_tools")` — HTTP 请求辅助工具。

| 工具        | 异步 | 参数                                                   | 返回值  | 用途                            |
| ----------- | ----- | ------------------------------------------------------------ | ------- | ---------------------------------- |
| `http_get`  | 否    | `url: str`, `headers: Optional[dict]`, `params: Optional[dict]` | `str` | 发送 HTTP GET 请求。             |
| `http_post` | 否    | `url: str`, `data: Optional[dict]`, `headers: Optional[dict]`   | `str` | 发送带 JSON 的 HTTP POST 请求。  |

---

## image_gen_tools

`FunctionHub(name="image_gen_tools")` — 通过外部 API 生成图像。

| 工具        | 异步 | 参数          | 返回值 | 用途                                   |
| ----------- | ----- | ------------------- | ------ | ----------------------------------------- |
| `gen_image` | 否    | `description: str`  | `str`  | 根据给定的文本描述返回 pollinations.ai URL。 |

---

## oxy_manage_tools

`FunctionHub(name="oxy_manage_tools")` — Agent 组织架构的运行时 CRUD 操作。挂载到 master agent 后，即可通过对话管理 Oxy 实例（Agent、工具、LLM）。

| 工具            | 异步 | 参数                                                                                       | 返回值 | 用途                                                      |
| --------------- | ----- | ------------------------------------------------------------------------------------------------ | ------ | ------------------------------------------------------------ |
| `list_oxys`     | 是   | `category_filter: str = ""`                                                                      | `str`  | 列出所有已注册的 Oxy 实例，可按 `agent`、`tool`、`llm` 过滤。 |
| `get_oxy_info`  | 是   | `oxy_name: str`                                                                                  | `str`  | 获取指定 Oxy 实例的详细配置信息。       |
| `create_agent`  | 是   | `agent_name: str`, `agent_type: str`, `desc: str`, `llm_model: str`, `prompt: str`, `sub_agents: str`, `tools: str`, `parent_agent: str` | `str`  | 在运行时创建并注册一个新 Agent。                  |
| `delete_oxy`    | 是   | `oxy_name: str`                                                                                  | `str`  | 删除一个 Oxy 并清理所有父级 Agent 中对它的引用。 |
| `move_oxy`      | 是   | `oxy_name: str`, `from_parent: str`, `to_parent: str`                                           | `str`  | 将子 Agent 或工具从一个父级 Agent 移动到另一个。   |
| `modify_oxy`    | 是   | `oxy_name: str`, `field_name: str`, `field_value: str`                                          | `str`  | 更新现有 Oxy 实例的任意字段。                |

结构性变更（`create_agent`、`delete_oxy`、`move_oxy`，以及 `modify_oxy` 修改结构字段时）会自动发送 SSE 消息以刷新前端组织架构树。

---

## math_tools

`FunctionHub(name="math_tools")` — 数学运算。

| 工具                   | 异步 | 参数                                                    | 返回值  | 用途                                          |
| ---------------------- | ----- | ------------------------------------------------------------- | ------- | ------------------------------------------------ |
| `calc_pi`              | 否    | `prec: int`                                                   | `float` | 计算指定小数精度的圆周率。       |
| `list_operation`       | 否    | `list1: list`, `list2: list`, `operation: str`                | `list`  | 两个列表之间的逐元素二元运算。 |
| `calculate_expression` | 否    | `expression: str`                                             | `str`   | 通过 AST 安全地计算数学表达式。       |

---

## python_tools

`FunctionHub(name="python_tools")` — Python 代码执行。

| 工具              | 异步 | 参数                                                                      | 返回值 | 用途                                    |
| ----------------- | ----- | ------------------------------------------------------------------------------- | ------ | ------------------------------------------ |
| `run_python_code` | 否    | `code: str`, `variable_to_return: Optional[str]`, `safe_globals`, `safe_locals` | `str`  | 通过 `exec()` 执行 Python 代码，可选返回指定变量。 |

---

## shell_tools

`FunctionHub(name="shell_tools")` — Shell 命令执行。

| 工具                    | 异步 | 参数                                                 | 返回值 | 用途                                                    |
| ----------------------- | ----- | ---------------------------------------------------------- | ------ | ---------------------------------------------------------- |
| `run_shell_command`     | 否    | `args: list[str]`, `tail: int = 10`, `base_dir: Optional[str]` | `str` | 同步运行 Shell 命令；返回最后 `tail` 行。 |
| `execute_shell_command` | 是   | `command: str`, `timeout: int = 300`                       | `str`  | 异步运行 Shell 命令，支持超时。    |

---

## ssh_tools

`FunctionHub(name="ssh_tools", timeout=600)` — 通过 SSH 远程执行命令。

| 工具       | 异步 | 参数                            | 返回值 | 用途                                              |
| ---------- | ----- | ------------------------------------- | ------ | ---------------------------------------------------- |
| `ssh_tool` | 是   | `shell_command: str`, `oxy_request`   | `str`  | 通过 `oxy_request` 全局数据中的 SSH 通道发送命令。 |

---

## string_tools

`FunctionHub(name="string_tools")` — 字符串分析工具。

| 工具             | 异步 | 参数   | 返回值 | 用途                                  |
| ---------------- | ----- | ------------ | ------ | ---------------------------------------- |
| `extract_emails` | 是   | `text: str`  | `str`  | 从文本中提取电子邮件地址。       |
| `extract_urls`   | 是   | `text: str`  | `str`  | 从文本中提取 URL。                  |
| `validate_email` | 是   | `email: str` | `str`  | 验证字符串是否符合电子邮件格式。 |

---

## system_tools

`FunctionHub(name="system_tools")` — 系统信息。

| 工具               | 异步 | 参数 | 返回值 | 用途                                               |
| ------------------ | ----- | ---------- | ------ | ----------------------------------------------------- |
| `get_system_info`  | 是   | （无）     | `str`  | 返回操作系统、版本、架构、处理器和 Python 信息。  |
| `get_system_usage` | 是   | （无）     | `str`  | 返回 CPU 占用率、内存和磁盘使用统计信息。           |

---

## time_tools

`FunctionHub(name="time_tools")` — 时区感知的时间工具。

| 工具               | 异步 | 参数                                                     | 返回值 | 用途                                         |
| ------------------ | ----- | -------------------------------------------------------------- | ------ | ----------------------------------------------- |
| `get_current_time` | 否    | `timezone: str`（IANA 名称，默认 `"Asia/Shanghai"`）         | `str`  | 返回指定时区的当前时间。   |
| `convert_time`     | 否    | `source_timezone: str`, `time: str`, `target_timezone: str`    | `str`  | 将时间从一个时区转换为另一个时区。     |

---

## 用法

```python
from oxygent.preset_tools import time_tools, shell_tools, math_tools

oxy_space = [
    time_tools,
    shell_tools,
    math_tools,
    oxy.ReActAgent(
        name="assistant",
        tool_name_list=["time_tools", "shell_tools", "math_tools"],
        ...
    ),
]
```
