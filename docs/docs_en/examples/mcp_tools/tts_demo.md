# TTS (Text-to-Speech) Demo

**Source:** `examples/mcp_tools/tts_demo.py`

## Overview

This example demonstrates how to integrate a Text-to-Speech (TTS) MCP service with OxyGent. A `ReActAgent` wraps a custom TTS MCP server powered by Microsoft Edge TTS, providing speech synthesis with automatic caching, intelligent text chunking, and audio playback. A master agent coordinates the TTS agent for multi-task scenarios.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- OxyGent package installed (`pip install -r requirements.txt`)
- Additional Python packages: `edge-tts`, `pydub`
- Optional: `ffmpeg` installed (for high-quality audio merging)
  - macOS: `brew install ffmpeg`
  - Linux: `apt install ffmpeg`
- Operating system: **macOS or Windows only** (audio playback limitation)
- A `./mcp_servers/tts_tools.py` file (the TTS MCP server)

## How to Run

```bash
python -m examples.mcp_tools.tts_demo
```

The demo starts a web service with a welcome message and TTS capabilities.

## Code Walkthrough

### Configuration

```python
Config.set_agent_llm_model("default_llm")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TTS_TOOLS_PATH = os.path.join(PROJECT_ROOT, "mcp_servers", "tts_tools.py")
```

Computes the absolute path to the TTS MCP server script by resolving relative to the project root. This ensures the path is correct regardless of the working directory.

### Components (`oxy_space`)

| Component | Type | Role |
|---|---|---|
| `default_llm` | `HttpLLM` | Shared language model |
| `tts_tools` | `StdioMCPClient` | MCP client for the TTS server, using the current Python interpreter (`sys.executable`) |
| `tts_agent` | `ReActAgent` | TTS specialist agent with detailed system prompt about available voices and capabilities |
| `master_agent` | `ReActAgent` | Coordinator agent; `is_master=True`, delegates to `tts_agent` |

### TTS MCP Client

```python
oxy.StdioMCPClient(
    name="tts_tools",
    params={
        "command": sys.executable,
        "args": [TTS_TOOLS_PATH],
    },
)
```

Uses `sys.executable` (the current Python interpreter) to run the TTS MCP server, ensuring it runs in the same virtual environment with all dependencies available.

### TTS Agent System Prompt

The `tts_agent` has a detailed `system_prompt` that documents:

- **Speech Playback**: `text_to_speech(text, voice)` -- converts text to speech and plays it.
- **Audio Control**: `stop_audio()` -- stops current playback; `get_available_voices(language_filter)` -- lists available voices.
- **Key Features**: Automatic caching in `tts_audio_cache/`, fixed 1200-character text chunking, cache reuse for identical text+voice combinations.
- **Popular Voices**: Chinese (XiaoxiaoNeural, YunxiNeural) and English (AriaNeural, GuyNeural).

### Entry Point

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello! I'm your TTS assistant...",
            welcome_message="Hi, I'm OxyGent with TTS and auto-caching capabilities...",
        )
```

Starts the web service with both a `first_query` (automatically sent) and a `welcome_message` (displayed in the UI before any interaction).

## Key Concepts

- **StdioMCPClient with `sys.executable`**: Running an MCP server using the same Python interpreter ensures environment consistency. This is a common pattern for Python-based MCP servers.
- **Audio Caching**: The TTS system automatically caches generated audio files, reusing them for identical text+voice combinations to avoid redundant synthesis.
- **Text Chunking**: Long texts are automatically split into 1200-character chunks for processing, then merged for playback.
- **`system_prompt` vs `prompt`**: The `system_prompt` parameter provides role-specific instructions that are separate from the default agent prompt template. It is used here to give the TTS agent detailed knowledge of its tool capabilities.

## Expected Behavior

1. The web UI opens with a welcome message about TTS capabilities.
2. Users can type text and ask the agent to read it aloud.
3. The `master_agent` routes TTS requests to `tts_agent`.
4. The `tts_agent` calls `text_to_speech` on the TTS MCP server.
5. Audio is generated (or served from cache), and playback begins on the host machine.
6. Users can also query available voices or stop playback.
