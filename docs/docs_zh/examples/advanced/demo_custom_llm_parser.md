# 自定义 LLM 响应解析器(XML 格式)

**源文件:** `examples/advanced/demo_custom_llm_parser.py`

## 概述

本示例展示了如何使用 `func_parse_llm_response` 参数将默认的 JSON 格式 LLM 响应解析器替换为自定义的 XML 格式解析器。当使用输出非标准格式的 LLM,或需要对响应解析进行精细控制时,该模式非常有用。

## 前置条件

- 环境变量: `DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Node.js 运行时(用于 `npx` 运行 MCP 文件系统服务器,以及 `uvx` 运行时间服务器)

## 运行方式

```bash
python -m examples.advanced.demo_custom_llm_parser
```

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
```

为所有 Agent 全局设置默认 LLM 模型。

### 自定义 XML 解析器

```python
def parse_llm_response(ori_response: str, oxy_request: OxyRequest = None) -> LLMResponse:
```

该函数替换了默认解析器。它期望 LLM 以下列两种 XML 格式之一输出:

**工具调用格式:**
```xml
<tool>
  <think>推理过程</think>
  <tool_name>工具名称</tool_name>
  <arguments>
    <param1>value1</param1>
  </arguments>
</tool>
```

**回答格式:**
```xml
<answer>
  <think>推理过程</think>
  你的回答内容
</answer>
```

解析器使用 `xml.etree.ElementTree` 解析响应,返回一个 `LLMResponse`,其中:
- `LLMState.TOOL_CALL` -- 当找到 `<tool_name>` 元素时,提取工具名称和参数字典。
- `LLMState.ANSWER` -- 当未找到工具名称时,提取回答文本(去除 `<think>` 内容)。
- `LLMState.ERROR_PARSE` -- 任何解析异常时返回。

### 自定义 Agent 提示词

```python
NOTE_AGENT_PROMPT = """\
You are a helpful note-taking assistant. ...
IMPORTANT: Use the following XML formats for your responses:
...
"""
```

提示词指示 LLM:
1. 作为记事助手,以特定格式记录备忘录。
2. 先获取当前时间(亚洲/上海时区),然后将备忘录保存到 `local_file/note.txt`。
3. 使用上述定义的 XML 响应格式,而非默认的 JSON 格式。
4. `${tools_description}` 占位符在运行时会被自动替换为实际的工具描述。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name`(来自环境变量);`llm_params={"temperature": 0.1}` |
| `time_tools` | `StdioMCPClient` | `command="uvx"`、`args=["mcp-server-time", "--local-timezone=Asia/Shanghai"]` |
| `file_tools` | `StdioMCPClient` | `command="npx"`、`args=["-y", "@modelcontextprotocol/server-filesystem", "./local_file"]` |
| `note_agent` | `ReActAgent` | `prompt=NOTE_AGENT_PROMPT`、`tools=["time_tools", "file_tools"]`、`func_parse_llm_response=parse_llm_response` |
| `master_agent` | `ReActAgent` | `is_master=True`、`sub_agents=["note_agent"]` |

### 入口函数

`main()` 创建 `MAS` 上下文并以 `first_query="Save a memo: team standup at 3 PM in room 618"` 启动 Web 服务。

## 核心概念

- **func_parse_llm_response** -- ReActAgent 上的回调参数,允许用任意自定义函数替换默认的 JSON 响应解析器。该函数接收原始 LLM 输出字符串,必须返回一个 `LLMResponse` 对象。
- **LLMResponse** -- 结构化对象,包含 `state`(TOOL_CALL、ANSWER 或 ERROR_PARSE)、`output`(解析后的内容)和 `ori_response`(原始字符串)。
- **LLMState** -- 定义解析后 LLM 响应可能状态的枚举:`TOOL_CALL`、`ANSWER`、`ERROR_PARSE`。
- **自定义提示词配合 XML 指令** -- 使用自定义解析器时,Agent 的提示词必须指示 LLM 按预期格式输出。
- **${tools_description}** -- 提示词中的模板变量,框架会将其替换为可用工具的实际描述。

## 预期行为

1. Web 服务在 `127.0.0.1:8080` 启动。
2. 主 Agent 将备忘录任务委派给 `note_agent`。
3. 备忘录 Agent 指示 LLM 使用 XML 格式。LLM 首先通过 XML 工具调用 `time_tools` 获取当前时间。
4. LLM 接着通过 XML 工具调用 `file_tools` 将格式化的备忘录保存到 `local_file/note.txt`。
5. 备忘录 Agent 通过 Web UI 向用户返回确认信息。
