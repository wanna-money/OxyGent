# OxyGent 概念总览

OxyGent 是一个开源的 Python 多智能体系统 (MAS) 框架。它将 LLM、智能体 (Agent)、工具 (Tool)、流程 (Flow) 统一为模块化的 "Oxy" 组件，通过名称引用的方式组装在一起，帮助您快速构建、运行和迭代多智能体系统。

---

## 核心概念

### oxy_space：组件列表

`oxy_space` 是一个 Python 列表，包含了系统中所有组件——LLM、Agent、Tool。每个组件都有一个 `name`，组件之间通过名称互相引用，而不是通过 Python 对象引用。

```python
oxy_space = [
    oxy.HttpLLM(name="default_llm", ...),        # LLM 组件
    oxy.StdioMCPClient(name="time_tools", ...),   # 工具组件
    oxy.ReActAgent(name="master_agent", ...,       # 智能体组件
        tools=["time_tools"],                       # 通过名称引用工具
        llm_model="default_llm",                    # 通过名称引用 LLM
        is_master=True,
    ),
]
```

### MAS：运行时容器

`MAS` (Multi-Agent System) 是 OxyGent 的运行时容器。它接收 `oxy_space`，将所有组件注册到内部，建立组件之间的引用关系，并提供多种启动方式：

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service()          # Web UI + API 服务
    # 或
    await mas.start_cli_mode()             # 命令行交互
    # 或
    result = await mas.chat_with_agent(    # 编程式调用
        payload={"query": "你好"}
    )
```

### is_master：入口智能体

设置 `is_master=True` 的智能体是用户查询的入口。用户的消息首先到达 master 智能体，由它决定是自己回答还是调用其他子智能体或工具。一个 MAS 中只能有一个 master 智能体。

### 组件类型

```
Oxy (基类)
├── LLM (大语言模型)
│   ├── HttpLLM         — 通过 HTTP API 调用云端模型
│   ├── OpenAILLM       — 使用 OpenAI SDK 调用兼容模型
│   ├── LocalLLM        — 本地加载 HuggingFace 模型
│   └── MockLLM         — 测试用模拟模型
├── Agent (智能体)
│   ├── ChatAgent       — 基础对话（单轮 LLM 调用）
│   ├── ReActAgent      — 推理-行动循环（支持工具调用）
│   ├── WorkflowAgent   — 自定义工作流
│   ├── ParallelAgent   — 并行执行多个子任务
│   ├── PlanAndSolveAgent — 先规划后执行
│   ├── RAGAgent        — 检索增强生成
│   ├── ShellUseAgent   — SSH 远程命令执行
│   ├── SkillAgent      — 动态加载技能
│   └── SSEOxyGent      — 连接远程分布式智能体
└── Tool (工具)
    ├── FunctionHub      — Python 函数工具集
    ├── StdioMCPClient   — MCP 标准输入/输出工具
    ├── SSEMCPClient     — MCP SSE 工具
    └── StreamableMCPClient — MCP Streamable 工具
```

---

## 术语表

| 术语 | 说明 |
|------|------|
| oxy_space | 包含所有组件 (LLM、Agent、Tool) 的 Python 列表 |
| MAS | Multi-Agent System，运行时容器，管理所有组件的生命周期 |
| is_master | 标记入口智能体，接收用户查询的第一个智能体 |
| OxyRequest | 请求对象，在组件之间传递，包含查询内容、上下文、共享数据等 |
| OxyResponse | 响应对象，包含输出结果和状态 |
| trace_id | 追踪标识，标记一次完整的对话或任务链 |
| sub_agents | 子智能体列表，master 智能体可以调度的下级智能体 |
| tools | 智能体可以使用的工具名称列表 |
| llm_model | 智能体内部使用的 LLM 名称 |
| semaphore | 并发控制信号量，限制同时执行的请求数 |
| FunctionHub | 将 Python 函数注册为工具的容器 |
| StdioMCPClient | 通过标准输入/输出协议连接外部工具服务器 |
| preset_tools | OxyGent 内置的工具集（文件、数学、时间、Shell 等） |

---

## 最小运行示例

```python
import asyncio, os
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
        await mas.start_web_service(first_query="你好！")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 接下来

- [安装 OxyGent](./install.md) -- 安装框架
- [快速上手](./quickstart.md) -- 5 分钟构建第一个智能体
- [创建第一个智能体](../agents/create-agent.md) -- 深入了解

---

[下一章：安装 OxyGent](./install.md)
[回到首页](../readme.md)
