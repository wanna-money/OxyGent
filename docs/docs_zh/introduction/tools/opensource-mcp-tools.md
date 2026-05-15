# 如何使用开源MCP工具？

在使用MCP的过程中，您可能希望使用外部工具。OxyGent支持如同本地工具一样集成外部的开源工具，您可以使用基于MCP协议的`oxy.StdioMCPClient`引入外部工具。

## 什么是 MCP？

MCP（Model Context Protocol）是一个开放标准协议，用于将 AI 智能体连接到外部工具和数据源。通过 MCP，您可以让智能体使用文件系统、数据库、搜索引擎、浏览器等各种外部功能，而无需自己编写工具代码。

OxyGent 原生支持 MCP 协议，提供三种 MCP 客户端：
- `oxy.StdioMCPClient` — 通过标准输入/输出连接本地 MCP 服务器（最常用）
- `oxy.SSEMCPClient` — 通过 SSE 连接远程 MCP 服务器
- `oxy.StreamableMCPClient` — 通过 Streamable HTTP 连接远程 MCP 服务器

## 前置要求：安装 uv

本文档中的示例使用 `uvx` 命令运行 MCP 工具。`uvx` 是 `uv` 包管理器提供的命令，可以直接运行 Python 包而无需全局安装。

安装 uv：
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 在哪里找到 MCP 工具？

- [MCP Servers 官方列表](https://github.com/modelcontextprotocol/servers) — 官方维护的 MCP 工具集合
- [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) — 社区维护的 MCP 工具列表
- NPM / PyPI 上搜索 `mcp-server-*` — 有大量第三方 MCP 工具包

例如，如果您希望使用工具获取时间，您可以使用`mcp-server-time`工具：

```python
oxy.StdioMCPClient(
    name="time_tools",
    params={
        "command": "uvx",
        "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
    },
),
```

## 完整的可运行样例

以下是可运行的完整代码示例：

```python
import asyncio

from oxygent import MAS, oxy, Config
import os
from oxygent import preset_tools

Config.set_agent_llm_model("default_llm")

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.01},
        semaphore=4,
        timeout=240,
    ),
    oxy.StdioMCPClient(
        name="time_tools",
        params={
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
        },
    ),
    preset_tools.file_tools,
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        tools=["file_tools","time_tools"],
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello!"
        )


if __name__ == "__main__":
    asyncio.run(main())
```

[上一章：注册一个工具](./register-tool.md)
[下一章：使用MCP自定义工具](./custom-mcp-tools.md)
[回到首页](../readme.md)

---

## 相关示例

- [MCP工具使用示例](../../examples/tools/demo_mcp.md) — 演示如何在OxyGent中使用开源MCP工具
- [浏览器MCP工具示例](../../examples/mcp_tools/browser_demo.md) — 演示浏览器类MCP工具的集成
