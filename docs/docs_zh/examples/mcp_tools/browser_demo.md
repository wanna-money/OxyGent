# 浏览器自动化示例

**源文件:** `examples/mcp_tools/browser_demo.py`

## 概述

本示例展示了使用 OxyGent 构建的多智能体浏览器自动化系统。一个主控智能体协调两个专门的子智能体 -- 用于网页抓取/导航的浏览器智能体和用于文件系统操作的文件智能体 -- 来执行搜索网页、提取数据和保存结果到文件等任务。该示例以 `BrowserDemo` 类的形式实现，每个智能体角色都有详细的系统提示词。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- 已安装 OxyGent 包（`pip install -r requirements.txt`）
- Node.js（文件系统 MCP 工具需要通过 `npx` 运行）
- PATH 中可用 `uv`（用于运行浏览器 MCP 服务器）
- `./mcp_servers/browser/server.py` 文件（自定义浏览器 MCP 服务器）
- `./local_file` 目录（用于文件操作）

## 运行方式

```bash
python -m examples.mcp_tools.browser_demo
```

示例启动 Web 服务，默认查询为："搜索'武汉市天气'，提取搜索结果的天气概览数据保存到 `./local_file/weather.txt`"。

## 代码详解

### 配置

```python
def load_config() -> Dict[str, Any]:
```

一个辅助函数，加载并验证必需的环境变量。如果缺少任何变量，会抛出 `ValueError` 并提供清晰的错误信息。`Config.set_agent_llm_model("default_llm")` 设置全局默认 LLM。

### 系统提示词

定义了三个详细的系统提示词：

1. **`MASTER_SYSTEM_PROMPT`**：指导主控智能体进行任务委派、上下文管理和结果整合。包含结构化的 JSON 格式，用于向子智能体委派任务时传递任务上下文、操作详情和错误处理信息。

2. **`BROWSER_SYSTEM_PROMPT`**：指导浏览器智能体进行网页操作、能力评估、登录页面检测和自动处理（使用环境变量凭据），以及内容提取。

3. **`FILE_SYSTEM_PROMPT`**：指导文件智能体进行文件操作、输入验证、数据处理和适当的错误处理。

### BrowserDemo 类

`BrowserDemo` 类封装了整个示例的配置：

- **`__init__`**：加载配置并创建 oxy space。
- **`_create_oxy_space`**：组装所有组件。
- **`_create_http_llm`**：配置 `HttpLLM`，包含详细参数（温度 0.01，信号量 4，重试 3 次，超时 60 秒）。
- **`_create_browser_tools`**：为 `./mcp_servers/browser/server.py` 处的浏览器 MCP 服务器创建 `StdioMCPClient`。
- **`_create_filesystem_tools`**：为 `@modelcontextprotocol/server-filesystem` 包创建 `StdioMCPClient`。
- **`_create_browser_agent`**：带浏览器工具和浏览器专用提示词的 `ReActAgent`。
- **`_create_file_agent`**：带文件系统工具和文件专用提示词的 `ReActAgent`。
- **`_create_master_agent`**：标记为 `is_master=True` 的 `ReActAgent`，子智能体为 `browser_agent` 和 `file_agent`。

### 组件（`oxy_space`）

| 组件 | 类型 | 角色 |
|---|---|---|
| `default_llm` | `HttpLLM` | 共享 LLM（温度 0.01，信号量 4，重试 3 次） |
| `browser_tools` | `StdioMCPClient` | 自定义浏览器 MCP 服务器，用于网页自动化 |
| `file_tools` | `StdioMCPClient` | 文件系统 MCP 服务器，用于文件操作 |
| `browser_agent` | `ReActAgent` | 处理网页导航、抓取和数据提取 |
| `file_agent` | `ReActAgent` | 处理文件读写操作 |
| `master_agent` | `ReActAgent` | 协调浏览器和文件智能体；`is_master=True` |

### 入口

```python
async def main():
    demo = BrowserDemo()
    await demo.run_demo()
```

`run_demo` 方法创建 `MAS` 上下文并启动 Web 服务。

## 核心概念

- **多智能体协调**：主控智能体分解任务并委派给专门的子智能体。主控智能体跟踪进度、传递上下文并整合结果。
- **StdioMCPClient**：通过标准 I/O 连接 MCP 工具服务器。此处使用了两个实例 -- 一个用于自定义浏览器服务器，一个用于官方文件系统服务器。
- **详细系统提示词**：每个智能体接收角色专用的指令，包含结构化输出格式、错误处理指南和能力边界。
- **基于类的示例模式**：将示例封装在类中，使用工厂方法创建每个组件，提供清晰的分离和错误处理。
- **自动登录处理**：浏览器智能体的提示词包含检测登录页面和使用环境变量凭据自动处理的指令，无需提示用户。

## 预期行为

1. Web 界面打开，查询搜索天气信息。
2. `master_agent` 将其分解为两个子任务：搜索网页和保存结果到文件。
3. `browser_agent` 使用浏览器工具导航到搜索引擎，查找天气数据并提取相关信息。
4. `master_agent` 将提取的数据传递给 `file_agent`。
5. `file_agent` 将数据写入 `./local_file/weather.txt`。
6. 最终摘要返回给用户。
