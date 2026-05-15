# 快速上手

本节将带您在 5 分钟内运行第一个 OxyGent 智能体。

## 前提条件

- 已安装 Python 3.10+
- 已安装 OxyGent（参见 [安装指南](./install.md)）
- 拥有一个 LLM API Key（支持 OpenAI、DeepSeek、通义千问等任何 OpenAI 兼容接口）

## 第一步：设置环境变量

在项目根目录创建 `.env` 文件（OxyGent 启动时会自动加载）：

```
DEFAULT_LLM_API_KEY=your_api_key
DEFAULT_LLM_BASE_URL=your_base_url
DEFAULT_LLM_MODEL_NAME=your_model_name
```

或者直接在终端中导出：

```bash
export DEFAULT_LLM_API_KEY="your_api_key"
export DEFAULT_LLM_BASE_URL="your_base_url"
export DEFAULT_LLM_MODEL_NAME="your_model_name"
```

> OxyGent 使用 `python-dotenv` 在启动时自动加载项目根目录下的 `.env` 文件。

## 第二步：创建并运行你的第一个智能体

创建一个文件 `my_first_agent.py`：

```python
import asyncio
import os

from oxygent import MAS, oxy

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    oxy.ChatAgent(
        name="my_agent",
        llm_model="default_llm",
        prompt="You are a helpful assistant.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        payload = {"query": "Hello! What can you do?"}
        oxy_response = await mas.chat_with_agent(payload=payload)
        print("LLM: ", oxy_response.output)


if __name__ == "__main__":
    asyncio.run(main())
```

运行：

```bash
python my_first_agent.py
```

你应该会看到类似如下的输出：

```
LLM:  Hello! I'm a helpful assistant. I can answer questions, ...
```

## 第三步：启动 Web UI

将 `chat_with_agent` 替换为 `start_web_service`，即可启动内置的 Web 界面：

```python
import asyncio
import os

from oxygent import MAS, oxy

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    oxy.ChatAgent(
        name="my_agent",
        llm_model="default_llm",
        prompt="You are a helpful assistant.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello",
            welcome_message="Hi, I'm OxyGent. How can I assist you?",
        )


if __name__ == "__main__":
    asyncio.run(main())
```

运行后，浏览器会自动打开 `http://127.0.0.1:8080`，你可以在 Web UI 中与智能体对话。

> 如果需要修改端口，可以在 `start_web_service` 中传入 `port=8082`，或通过 `Config.set_server_port(8082)` 进行全局设置。

## 第四步：使用命令行交互

如果你更喜欢在终端中对话，可以使用 `start_cli_mode`：

```python
import asyncio
import os

from oxygent import MAS, oxy

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    oxy.ChatAgent(
        name="my_agent",
        llm_model="default_llm",
        prompt="You are a helpful assistant.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_cli_mode(first_query="Hello")


if __name__ == "__main__":
    asyncio.run(main())
```

运行后，你可以在终端中持续输入问题与智能体对话。输入 `reset` 可重置会话。

## 常见问题

### 为什么系统启动后报 404？

请检查环境变量是否正确配置。不同模型的 `base_url` 格式不同，详见 [选择 LLM](../agents/select-llm.md)。

### 如何获得帮助？

- 在 GitHub 提交 Issue
- 查看 [完整教程目录](../readme.md)

---

[上一章：安装 OxyGent](./install.md)
[下一章：设置 Config](../getting-started/config.md)
[回到首页](../readme.md)

---

## 相关示例

- [单 Agent 示例](../../examples/agents/demo_single_agent.md) — 最简单的 ChatAgent 配置
- [Ollama 本地模型示例](../../examples/llms/demo_ollama.md) — 使用 Ollama 部署的本地模型
- [流式输出 Chat Agent 示例](../../examples/agents/demo_chat_agent_stream.md) — 流式输出的 ChatAgent
