# TTS（文字转语音）示例

**源文件:** `examples/mcp_tools/tts_demo.py`

## 概述

本示例展示了如何将文字转语音（TTS）MCP 服务与 OxyGent 集成。一个 `ReActAgent` 封装了基于 Microsoft Edge TTS 的自定义 TTS MCP 服务器，提供语音合成功能，支持自动缓存、智能文本分块和音频播放。主控智能体在多任务场景下协调 TTS 智能体。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- 已安装 OxyGent 包（`pip install -r requirements.txt`）
- 额外 Python 包：`edge-tts`、`pydub`
- 可选：安装 `ffmpeg`（用于高质量音频合并）
  - macOS：`brew install ffmpeg`
  - Linux：`apt install ffmpeg`
- 操作系统：**仅支持 macOS 或 Windows**（音频播放限制）
- `./mcp_servers/tts_tools.py` 文件（TTS MCP 服务器）

## 运行方式

```bash
python -m examples.mcp_tools.tts_demo
```

示例启动带有欢迎消息和 TTS 功能的 Web 服务。

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TTS_TOOLS_PATH = os.path.join(PROJECT_ROOT, "mcp_servers", "tts_tools.py")
```

通过相对于项目根目录解析来计算 TTS MCP 服务器脚本的绝对路径。这确保无论工作目录如何，路径都是正确的。

### 组件（`oxy_space`）

| 组件 | 类型 | 角色 |
|---|---|---|
| `default_llm` | `HttpLLM` | 共享语言模型 |
| `tts_tools` | `StdioMCPClient` | TTS 服务器的 MCP 客户端，使用当前 Python 解释器（`sys.executable`） |
| `tts_agent` | `ReActAgent` | TTS 专家智能体，包含关于可用语音和功能的详细系统提示词 |
| `master_agent` | `ReActAgent` | 协调智能体；`is_master=True`，委派给 `tts_agent` |

### TTS MCP 客户端

```python
oxy.StdioMCPClient(
    name="tts_tools",
    params={
        "command": sys.executable,
        "args": [TTS_TOOLS_PATH],
    },
)
```

使用 `sys.executable`（当前 Python 解释器）运行 TTS MCP 服务器，确保在相同的虚拟环境中运行，所有依赖项都可用。

### TTS 智能体系统提示词

`tts_agent` 有一个详细的 `system_prompt`，说明了：

- **语音播放**：`text_to_speech(text, voice)` -- 将文本转换为语音并播放。
- **音频控制**：`stop_audio()` -- 停止当前播放；`get_available_voices(language_filter)` -- 列出可用语音。
- **核心特性**：在 `tts_audio_cache/` 中自动缓存、固定 1200 字符的文本分块、相同文本+语音组合的缓存复用。
- **常用语音**：中文（晓晓-女声 XiaoxiaoNeural、云希-男声 YunxiNeural）和英文（Aria-女声 AriaNeural、Guy-男声 GuyNeural）。

### 入口

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello! I'm your TTS assistant...",
            welcome_message="Hi, I'm OxyGent with TTS and auto-caching capabilities...",
        )
```

启动 Web 服务，同时设置 `first_query`（自动发送）和 `welcome_message`（在任何交互之前显示在界面中）。

## 核心概念

- **StdioMCPClient 与 `sys.executable`**：使用相同的 Python 解释器运行 MCP 服务器确保环境一致性。这是 Python 编写的 MCP 服务器的常见模式。
- **音频缓存**：TTS 系统自动缓存生成的音频文件，对相同的文本+语音组合复用缓存，避免重复合成。
- **文本分块**：长文本自动分割为 1200 字符的块进行处理，然后合并播放。
- **`system_prompt` vs `prompt`**：`system_prompt` 参数提供与默认智能体提示模板分离的角色专用指令。此处用于给 TTS 智能体提供关于其工具能力的详细知识。

## 预期行为

1. Web 界面打开，显示关于 TTS 功能的欢迎消息。
2. 用户可以输入文本并要求智能体朗读。
3. `master_agent` 将 TTS 请求路由到 `tts_agent`。
4. `tts_agent` 调用 TTS MCP 服务器上的 `text_to_speech`。
5. 音频生成（或从缓存提供），主机上开始播放。
6. 用户还可以查询可用语音或停止播放。
