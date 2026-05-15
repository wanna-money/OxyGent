# TTS（文字转语音）示例

**源文件:** `examples/mcp_tools/tts_demo.py`

## 概述

本示例展示了如何将文字转语音（TTS）MCP 服务与 OxyGent 集成。一个 `ReActAgent` 封装了基于 Microsoft Edge TTS 的自定义 TTS MCP 服务器，提供语音合成功能，支持自动缓存、智能文本分块和音频播放。主控智能体在多任务场景下协调 TTS 智能体。

![TTS Demo](./demo_tts.gif)

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

## TTS 工具 API 参考

### `text_to_speech(text, voice)`

将文本转换为语音并自动播放。

- **参数：**
  - `text` (str, 必需): 要转换的文本内容。
  - `voice` (str, 可选): 声音 ID，默认为 `zh-CN-XiaoxiaoNeural`。
- **返回：** `"Playing cached audio (voice: xxx)"` 或 `"Playing generated audio (voice: xxx)"`；失败时返回错误信息。

### `get_available_voices(language_filter)`

查询 Edge TTS 支持的所有声音，支持按语言过滤。

- **参数：**
  - `language_filter` (str, 可选): 语言过滤器，如 `zh`、`en`、`zh-CN`。省略则返回全部。
- **返回：** 可用声音列表（最多显示 20 个）。

### `stop_audio()`

停止当前正在播放的音频。

- **返回：** `"Audio playback stopped successfully"` 或错误信息。

## 常用语音列表

| 语言 | 声音 ID | 描述 | 性别 |
|------|---------|------|------|
| 中文 | `zh-CN-XiaoxiaoNeural` | 晓晓 | 女声 |
| 中文 | `zh-CN-YunxiNeural` | 云希 | 男声 |
| 中文 | `zh-CN-YunyangNeural` | 云扬 | 男声 |
| 中文 | `zh-CN-XiaoyiNeural` | 晓伊 | 女声 |
| 英文 | `en-US-AriaNeural` | Aria | 女声 |
| 英文 | `en-US-GuyNeural` | Guy | 男声 |
| 英文 | `en-US-JennyNeural` | Jenny | 女声 |

## 技术细节

### 缓存策略

- **缓存目录：** `tts_audio_cache/`（当前工作目录下）
- **缓存键：** 文本内容 + 声音 ID 的 MD5 哈希
- **容量限制：** 最多 50 个文件；超过 7 天的缓存自动删除，超限时删除最旧文件
- **索引文件：** `cache_index.json`

### 文本分块

对于超过 1200 字符的文本，工具按以下优先级智能分块：

1. 在句子结束符（。！？.!?）处分割
2. 在逗号、分号（，；,;）处分割
3. 强制按字符数分割

最小块大小为 50 字符。

### 重试机制

- 最大重试 3 次，指数退避 + 随机抖动
- 基础延迟 1 秒，最大延迟 10 秒

### 音频合并

分块长文本的合并方式：

- **高质量模式**（需要 ffmpeg/pydub）：使用 pydub 合并，块间添加 200ms 间隔
- **简单模式**（无 ffmpeg）：二进制直接拼接

## 故障排除

| 问题 | 错误信息 | 解决方案 |
|------|----------|----------|
| 缺少依赖 | `edge-tts is not installed` | 运行 `pip install edge-tts` |
| 系统不支持 | `Unsupported system: Linux` | 使用 macOS 或 Windows；Linux 暂不支持音频播放 |
| 播放器未找到 | `afplay command not found` (macOS) 或 `PowerShell not available` (Windows) | 检查系统音频设置，重启终端或确认 PowerShell 已安装 |
| 缓存权限 | `Cannot write to cache directory` | 检查 `tts_audio_cache/` 目录权限，运行 `chmod 755 tts_audio_cache/` |
| 网络超时 | `Network timeout` | 检查网络连接；工具会自动重试 3 次，稍后再试 |
