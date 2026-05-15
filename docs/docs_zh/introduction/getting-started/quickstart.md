# 快速上手

> 五分钟内构建你的第一个智能体，添加工具，编排多智能体系统。

---

## 1. 安装

确保你的 Python 版本 >= 3.10，然后安装 OxyGent：

```bash
pip install -r requirements.txt
```

在项目根目录创建 `.env` 文件，OxyGent 启动时会通过 `dotenv` 自动加载：

```
DEFAULT_LLM_API_KEY=your_api_key
DEFAULT_LLM_BASE_URL=your_base_url
DEFAULT_LLM_MODEL_NAME=your_model_name
```

> 支持任何 OpenAI 兼容的 API（DeepSeek、通义千问、智谱等），只需填入对应的 base_url 和 model_name。

---

## 2. 创建第一个智能体

最小示例：一个能对话的 ChatAgent，只需 10 行代码。

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
    ),
]

async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        result = await mas.chat_with_agent(payload={"query": "你好！"})
        print(result.output)

asyncio.run(main())
```

**要点：**

- `oxy_space` 是组件列表，包含 LLM 和 Agent。
- 组件之间通过 `name` 互相引用，如 `llm_model="default_llm"`。
- `is_master=True` 标记入口智能体，用户消息首先到达它。
- `MAS` 是运行时容器，使用 `async with` 管理生命周期。

---

## 3. 添加工具

ChatAgent 只能对话，不能调用外部能力。通过 `FunctionHub` 注册工具，并切换到 `ReActAgent`，智能体就能推理并调用工具。

```python
import asyncio
import os
from oxygent import MAS, oxy
from oxygent.oxy.function_tools.function_hub import FunctionHub

# 创建工具集
calculator_hub = FunctionHub(name="calculator")

@calculator_hub.tool(description="两个数相加")
def add(a: float, b: float) -> float:
    return a + b

@calculator_hub.tool(description="两个数相乘")
def multiply(a: float, b: float) -> float:
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
    ),
]

async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        result = await mas.chat_with_agent(payload={"query": "3.14 乘以 2 再加 10 等于多少？"})
        print(result.output)

asyncio.run(main())
```

**要点：**

- `FunctionHub` 是工具容器，用 `@hub.tool()` 装饰器注册 Python 函数。
- `ReActAgent` 会自动推理何时调用工具、调用哪个工具，并将结果整合为最终回答。
- Agent 通过 `tools=["calculator"]` 引用工具集的 `name`，无需传递 Python 对象。

---

## 4. 多智能体协作

当任务涉及多个领域时，可以创建多个子智能体，由 master 智能体统一调度。

```python
import asyncio
import os
from oxygent import MAS, oxy, preset_tools

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    # 内置工具集
    preset_tools.time_tools,
    preset_tools.math_tools,
    # 子智能体：各司其职
    oxy.ReActAgent(
        name="time_agent",
        desc="查询时间的智能体",
        tools=["time_tools"],
    ),
    oxy.ReActAgent(
        name="math_agent",
        desc="进行数学计算的智能体",
        tools=["math_tools"],
    ),
    # 主智能体：分发任务
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        sub_agents=["time_agent", "math_agent"],
    ),
]

async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        result = await mas.chat_with_agent(
            payload={"query": "现在几点了？另外帮我算一下 123 * 456"}
        )
        print(result.output)

asyncio.run(main())
```

**要点：**

- `sub_agents` 列表声明子智能体，master 根据用户意图自动分发任务。
- 每个子智能体有独立的 `desc`（描述），master 根据描述判断应该调度谁。
- `preset_tools` 是 OxyGent 内置的常用工具集（时间、文件、数学、Shell 等）。

---

## 5. 启动 Web UI

将 `chat_with_agent()` 替换为 `start_web_service()`，即可启动带可视化界面的 Web 服务：

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="你好，请问有什么可以帮你？",
            welcome_message="欢迎使用 OxyGent 多智能体系统！",
        )

asyncio.run(main())
```

启动后访问 `http://127.0.0.1:8080`，即可在浏览器中与智能体对话。

除 Web UI 外，MAS 还支持其他启动模式：

| 模式 | 方法 | 用途 |
|------|------|------|
| Web 服务 | `start_web_service()` | 可视化界面 + REST API |
| 命令行 | `start_cli_mode()` | 终端交互式对话 |
| 批处理 | `start_batch_processing(querys)` | 批量并发执行 |
| 编程式 | `chat_with_agent(payload)` | 嵌入到应用代码中 |

---

## 下一步

恭喜你完成了快速上手教程！接下来可以深入了解：

- [OxyGent 概念总览](./overview.md) -- 理解核心架构
- [设置 Config](./config.md) -- 自定义全局配置
- [注册本地工具](../tools/register-tool.md) -- 更多工具注册方式
- [创建多智能体系统](../multi-agent/multi-agent-system.md) -- 复杂协作场景

---

[上一篇: 运行 Demo](./demo.md)
[下一篇: 设置 Config](./config.md)
[返回首页](../readme.md)
