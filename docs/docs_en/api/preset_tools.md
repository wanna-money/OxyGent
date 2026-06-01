# Preset Tools

---
The position of the modules is:

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

## Introduction

The `preset_tools` package provides 11 built-in `FunctionHub` collections that cover common utility operations. Each module exports a `FunctionHub` instance with `@tool`-decorated functions that can be registered directly into an agent's `oxy_space`. The package auto-discovers and loads all modules at import time.

---

## file_tools

`FunctionHub(name="file_tools")` — File operations sandboxed to the current working directory.

| Tool            | Async | Parameters                                    | Return  | Purpose                                      |
| --------------- | ----- | --------------------------------------------- | ------- | -------------------------------------------- |
| `write_file`    | No    | `path: str`, `content: str`                   | `str`   | Create or overwrite a file.                  |
| `read_file`     | No    | `path: str`                                   | `str`   | Read and return a file's content.            |
| `delete_file`   | No    | `path: str`                                   | `str`   | Delete a file or directory recursively.      |
| `view_text_file`| No    | `file_path: str`, `ranges: Optional[list[int]]` | `str` | View file content with line numbers and optional line range. |

---

## http_tools

`FunctionHub(name="http_tools")` — HTTP request helpers.

| Tool        | Async | Parameters                                                   | Return  | Purpose                            |
| ----------- | ----- | ------------------------------------------------------------ | ------- | ---------------------------------- |
| `http_get`  | No    | `url: str`, `headers: Optional[dict]`, `params: Optional[dict]` | `str` | Send HTTP GET request.             |
| `http_post` | No    | `url: str`, `data: Optional[dict]`, `headers: Optional[dict]`   | `str` | Send HTTP POST request with JSON.  |

---

## image_gen_tools

`FunctionHub(name="image_gen_tools")` — Image generation via external APIs.

| Tool        | Async | Parameters          | Return | Purpose                                   |
| ----------- | ----- | ------------------- | ------ | ----------------------------------------- |
| `gen_image` | No    | `description: str`  | `str`  | Return a pollinations.ai URL for the given text description. |

---

## oxy_manage_tools

`FunctionHub(name="oxy_manage_tools")` — Runtime CRUD operations for the agent organization tree. Attach to the master agent to manage Oxy instances (agents, tools, LLMs) through conversation.

| Tool            | Async | Parameters                                                                                       | Return | Purpose                                                      |
| --------------- | ----- | ------------------------------------------------------------------------------------------------ | ------ | ------------------------------------------------------------ |
| `list_oxys`     | Yes   | `category_filter: str = ""`                                                                      | `str`  | List all registered Oxy instances, filterable by `agent`, `tool`, or `llm`. |
| `get_oxy_info`  | Yes   | `oxy_name: str`                                                                                  | `str`  | Get detailed configuration of a specific Oxy instance.       |
| `create_agent`  | Yes   | `agent_name: str`, `agent_type: str`, `desc: str`, `llm_model: str`, `prompt: str`, `sub_agents: str`, `tools: str`, `parent_agent: str` | `str`  | Create and register a new agent at runtime.                  |
| `delete_oxy`    | Yes   | `oxy_name: str`                                                                                  | `str`  | Delete an Oxy and clean up all references from parent agents. |
| `move_oxy`      | Yes   | `oxy_name: str`, `from_parent: str`, `to_parent: str`                                           | `str`  | Move a sub-agent or tool from one parent agent to another.   |
| `modify_oxy`    | Yes   | `oxy_name: str`, `field_name: str`, `field_value: str`                                          | `str`  | Update any field on an existing Oxy instance.                |

Structural changes (`create_agent`, `delete_oxy`, `move_oxy`, and `modify_oxy` on structural fields) automatically send an SSE message to refresh the frontend organization tree.

---

## math_tools

`FunctionHub(name="math_tools")` — Mathematical operations.

| Tool                   | Async | Parameters                                                    | Return  | Purpose                                          |
| ---------------------- | ----- | ------------------------------------------------------------- | ------- | ------------------------------------------------ |
| `calc_pi`              | No    | `prec: int`                                                   | `float` | Compute pi to specified decimal precision.       |
| `list_operation`       | No    | `list1: list`, `list2: list`, `operation: str`                | `list`  | Element-wise binary operation between two lists. |
| `calculate_expression` | No    | `expression: str`                                             | `str`   | Safely evaluate a math expression via AST.       |

---

## python_tools

`FunctionHub(name="python_tools")` — Python code execution.

| Tool              | Async | Parameters                                                                      | Return | Purpose                                    |
| ----------------- | ----- | ------------------------------------------------------------------------------- | ------ | ------------------------------------------ |
| `run_python_code` | No    | `code: str`, `variable_to_return: Optional[str]`, `safe_globals`, `safe_locals` | `str`  | Execute Python code via `exec()` and optionally return a named variable. |

---

## shell_tools

`FunctionHub(name="shell_tools")` — Shell command execution.

| Tool                    | Async | Parameters                                                 | Return | Purpose                                                    |
| ----------------------- | ----- | ---------------------------------------------------------- | ------ | ---------------------------------------------------------- |
| `run_shell_command`     | No    | `args: list[str]`, `tail: int = 10`, `base_dir: Optional[str]` | `str` | Run a shell command synchronously; return last `tail` lines. |
| `execute_shell_command` | Yes   | `command: str`, `timeout: int = 300`                       | `str`  | Run a shell command asynchronously with timeout support.    |

---

## ssh_tools

`FunctionHub(name="ssh_tools", timeout=600)` — Remote command execution over SSH.

| Tool       | Async | Parameters                            | Return | Purpose                                              |
| ---------- | ----- | ------------------------------------- | ------ | ---------------------------------------------------- |
| `ssh_tool` | Yes   | `shell_command: str`, `oxy_request`   | `str`  | Send a command over an SSH channel from `oxy_request` global data. |

---

## string_tools

`FunctionHub(name="string_tools")` — String analysis utilities.

| Tool             | Async | Parameters   | Return | Purpose                                  |
| ---------------- | ----- | ------------ | ------ | ---------------------------------------- |
| `extract_emails` | Yes   | `text: str`  | `str`  | Extract email addresses from text.       |
| `extract_urls`   | Yes   | `text: str`  | `str`  | Extract URLs from text.                  |
| `validate_email` | Yes   | `email: str` | `str`  | Validate if a string matches email format. |

---

## system_tools

`FunctionHub(name="system_tools")` — System information.

| Tool               | Async | Parameters | Return | Purpose                                               |
| ------------------ | ----- | ---------- | ------ | ----------------------------------------------------- |
| `get_system_info`  | Yes   | (none)     | `str`  | Return OS, version, machine, processor, Python info.  |
| `get_system_usage` | Yes   | (none)     | `str`  | Return CPU %, memory, and disk usage stats.           |

---

## time_tools

`FunctionHub(name="time_tools")` — Timezone-aware time utilities.

| Tool               | Async | Parameters                                                     | Return | Purpose                                         |
| ------------------ | ----- | -------------------------------------------------------------- | ------ | ----------------------------------------------- |
| `get_current_time` | No    | `timezone: str` (IANA name, default `"Asia/Shanghai"`)         | `str`  | Return current time in the specified timezone.   |
| `convert_time`     | No    | `source_timezone: str`, `time: str`, `target_timezone: str`    | `str`  | Convert a time from one timezone to another.     |

---

## Usage

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
