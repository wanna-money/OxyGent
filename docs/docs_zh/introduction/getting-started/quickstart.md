# 快速上手

> 五分钟内构建你的第一个智能体，添加工具，编排多智能体系统。

---

## 前置条件

- **Python 3.10+**
- 已安装 OxyGent（参见 [安装指南](./install.md)）
- 一个 LLM API Key（支持任何 OpenAI 兼容的 API：DeepSeek、通义千问、智谱等）

## 1. 设置环境变量

在项目根目录创建 `.env` 文件，OxyGent 启动时会通过 `python-dotenv` 自动加载：

```
DEFAULT_LLM_API_KEY=your_api_key
DEFAULT_LLM_BASE_URL=your_base_url
DEFAULT_LLM_MODEL_NAME=your_model_name
```

或直接在终端中导出：

```bash
export DEFAULT_LLM_API_KEY="your_api_key"
export DEFAULT_LLM_BASE_URL="your_base_url"
export DEFAULT_LLM_MODEL_NAME="your_model_name"
```

支持任何 OpenAI 兼容的 API（DeepSeek、通义千问、智谱等），只需填入对应的 base_url 和 model_name。

---

## 2. 创建第一个智能体

创建文件 `quickstart.py`：

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
        name="assistant",
        is_master=True,
        llm_model="default_llm",
        prompt="You are a helpful assistant.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        response = await mas.chat_with_agent(payload={"query": "你好！你能做什么？"})
        print("Agent:", response.output)


if __name__ == "__main__":
    asyncio.run(main())
```

运行：

```bash
python quickstart.py
```

预期输出：

```
Agent: 你好！我是一个智能助手，可以回答问题、辅助写作、……
```

**要点：**

- `oxy_space` 是组件列表，包含 LLM 和 Agent。
- 组件之间通过 `name` 互相引用，如 `llm_model="default_llm"`。
- `is_master=True` 标记入口智能体，用户消息首先到达它。
- `MAS` 是运行时容器，使用 `async with` 管理生命周期。

`ChatAgent` 只能进行单轮 LLM 调用，不支持工具。适合简单问答，但复杂任务通常需要工具能力。

---

## 3. 启动 Web UI

将 `chat_with_agent` 替换为 `start_web_service`，即可启动内置 Web 界面：

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="你好！",
            welcome_message="欢迎使用 OxyGent，有什么可以帮你？",
        )
```

启动后浏览器会自动打开 `http://127.0.0.1:8080`，即可在 Web UI 中与智能体对话。

> 修改端口：传入 `port=8082` 参数，或通过 `Config.set_server_port(8082)` 全局设置。

MAS 支持多种启动模式：

| 模式 | 方法 | 用途 |
|------|------|------|
| Web 服务 | `start_web_service()` | 可视化界面 + REST API |
| 命令行 | `start_cli_mode()` | 终端交互式对话 |
| 批处理 | `start_batch_processing(querys)` | 批量并发执行 |
| 编程式 | `chat_with_agent(payload)` | 嵌入到应用代码中 |

---

## 4. 添加工具

通过 `FunctionHub` 注册工具，并切换到 `ReActAgent`，智能体就能推理并调用工具。

```python
import asyncio
import os

from pydantic import Field
from oxygent import MAS, oxy
from oxygent.oxy import FunctionHub

calculator_hub = FunctionHub(name="calculator")


@calculator_hub.tool(description="Add two numbers together")
def add(
    a: float = Field(description="First number"),
    b: float = Field(description="Second number"),
) -> float:
    return a + b


@calculator_hub.tool(description="Multiply two numbers together")
def multiply(
    a: float = Field(description="First number"),
    b: float = Field(description="Second number"),
) -> float:
    return a * b


oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    calculator_hub,
    oxy.ReActAgent(
        name="math_agent",
        is_master=True,
        llm_model="default_llm",
        tools=["calculator"],
        prompt="You are a math assistant. Use the calculator tools to answer math questions.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        response = await mas.chat_with_agent(
            payload={"query": "12.5 加 7.3 等于多少？再把结果乘以 4。"}
        )
        print("Agent:", response.output)


if __name__ == "__main__":
    asyncio.run(main())
```

`ReActAgent` 遵循推理-行动循环（Reasoning + Acting）：先思考该做什么，调用工具，观察结果，循环直到得到答案。

预期输出：

```
Agent: 12.5 + 7.3 = 19.8，乘以 4 等于 79.2。
```

**要点：**
- `FunctionHub` 是工具容器，用 `@hub.tool()` 装饰器注册 Python 函数。
- `ReActAgent` 会自动推理何时调用工具、调用哪个工具，并将结果整合为最终回答。
- Agent 通过 `tools=["calculator"]` 引用工具集的 `name`，无需传递 Python 对象。

---

## 5. 多智能体协作

添加子智能体，由 master 智能体统一调度。master 根据用户意图自动分发任务。

```python
import asyncio
import os

from pydantic import Field
from oxygent import MAS, oxy
from oxygent.oxy import FunctionHub

calculator_hub = FunctionHub(name="calculator")


@calculator_hub.tool(description="Add two numbers together")
def add(
    a: float = Field(description="First number"),
    b: float = Field(description="Second number"),
) -> float:
    return a + b


oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    calculator_hub,
    # 子智能体：处理数学问题
    oxy.ReActAgent(
        name="math_agent",
        desc="A math specialist. Delegates math questions to this agent.",
        llm_model="default_llm",
        tools=["calculator"],
        prompt="You are a math assistant. Use the calculator tools to answer math questions.",
    ),
    # 主智能体：路由查询
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        llm_model="default_llm",
        sub_agents=["math_agent"],
        prompt="You are a helpful assistant. Route math questions to math_agent. Answer other questions directly.",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        response = await mas.chat_with_agent(
            payload={"query": "99 加 1 等于多少？"}
        )
        print("Agent:", response.output)


if __name__ == "__main__":
    asyncio.run(main())
```

master 智能体通过 `desc` 字段将 `math_agent` 视为可调用的工具。当数学问题到来时，master 将其分发给 `math_agent`，后者使用计算器工具，然后返回结果。

**要点：**
- 只有一个智能体设置 `is_master=True`，作为用户请求的入口。
- 通过 `sub_agents` 列表声明子智能体，按名称引用。
- `desc` 字段告诉 master 每个子智能体的能力，master 据此判断应该调度谁。

---

## 下一步

恭喜你完成了快速上手教程！接下来可以深入了解：

- [智能体类型](../agents/agent-types.md) -- ChatAgent、ReActAgent、WorkflowAgent、ParallelAgent 等
- [注册本地工具](../tools/register-tool.md) -- 更多 FunctionHub 用法
- [使用 MCP 工具](../tools/custom-mcp-tools.md) -- 连接外部工具服务器
- [多智能体系统](../multi-agent/multi-agent-system.md) -- 深入了解 master-sub 架构
- [分布式系统](../multi-agent/distributed.md) -- 跨进程智能体通信
- [设置 Config](./config.md) -- 全局配置、LLM 默认值、日志

## 常见问题

### 启动后为什么报 404 错误？

检查环境变量是否正确配置。不同模型可能需要不同的 `base_url` 格式。详见 [选择 LLM](../agents/select-llm.md)。

### 如何获取帮助？

- 在 GitHub 上提交 issue
- 浏览 [完整文档](../readme.md)

[上一章：安装 OxyGent](./install.md)
[下一章：设置 Config](./config.md)
[回到首页](../readme.md)

---

## 相关示例

- [单智能体示例](../../examples/agents/demo_single_agent.md) — 最简 ChatAgent 配置
- [Ollama 本地模型示例](../../examples/llms/demo_ollama.md) — 使用 Ollama 部署本地模型
- [流式输出示例](../../examples/agents/demo_chat_agent_stream.md) — ChatAgent 流式响应
