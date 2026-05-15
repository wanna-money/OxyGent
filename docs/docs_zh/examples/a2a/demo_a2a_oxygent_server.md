# A2A OxyGent 服务端

**源文件:** `examples/a2a/demo_a2a_oxygent_server.py`

## 概述

本示例启动一个内置 A2A（Agent-to-Agent）协议端点的 OxyGent MAS（多智能体系统）。它配置了一个基于 HTTP LLM 的 `ChatAgent`，并在 8090 端口上以 A2A 兼容服务器的形式对外暴露。其他 A2A 客户端——无论是 OxyGent 原生客户端还是基于 Google A2A SDK 的客户端——都可以向该服务器发送消息。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- 已安装依赖：`pip install -r requirements.txt`

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py
```

服务器启动后运行在 `http://127.0.0.1:8090`，A2A 端点位于 `/a2a` 路径下。

## 代码详解

### 配置

两个常量控制服务器绑定：

- `PORT = 8090` -- FastAPI Web 服务的 HTTP 端口。
- `A2A_BASE_PATH = "/a2a"` -- 所有 A2A 协议端点的 URL 前缀（如 `/a2a/.well-known/agent.json`、`/a2a/` 用于消息发送）。

`Config.set_server_port(PORT)` 在 MAS 启动前将默认端口（8080）覆盖为 8090。

### 组件（`oxy_space`）

`oxy_space` 列表定义了两个 Oxy 组件：

1. **`HttpLLM`**（`name="default_llm"`）-- 基于 HTTP 的 LLM 客户端，从环境变量读取配置，为智能体提供语言模型后端。

2. **`ChatAgent`**（`name="master_agent"`）-- 使用 `default_llm` 的对话智能体。标记为 `is_master=True`，使其成为 MAS 接收外部消息的默认入口。

### 入口

`main()` 协程：

1. 通过 `Config.set_server_port(PORT)` 设置服务端口。
2. 创建 `MAS` 实例，设置 `enable_a2a_server=True` 和 `a2a_base_path=A2A_BASE_PATH`，指示 MAS 在 FastAPI 应用上挂载 A2A 协议路由。
3. 调用 `mas.start_web_service(first_query="A2A MAS server is running.")`  启动 Web 服务。`first_query` 参数会触发一条初始自检消息。

脚本通过 `asyncio.run(main())` 作为顶层入口启动。

## 核心概念

- **A2A 协议**：Agent-to-Agent 是一种智能体间通信协议。OxyGent 原生实现了该协议，允许任何 A2A 兼容的客户端与 MAS 交互。
- **`enable_a2a_server`**：MAS 构造函数标志，启用后会在 Web 服务中添加 A2A 端点（智能体卡片、消息发送、流式传输、任务管理）。
- **`a2a_base_path`**：控制 A2A 端点的 URL 前缀，使其可以与标准 OxyGent Web UI 和聊天 API 共存。
- **Master Agent**：标记为 `is_master=True` 的智能体将接收所有通过 `MAS.chat_with_agent()` 路由的顶层消息。

## 预期行为

启动后，服务器：

1. 打印启动日志，并在 `http://127.0.0.1:8090` 提供 OxyGent Web UI。
2. 在 `http://127.0.0.1:8090/a2a/.well-known/agent.json` 暴露 A2A 智能体卡片。
3. 在 `http://127.0.0.1:8090/a2a/` 接受 A2A `message/send` 和 `message/stream` 请求。
4. 将传入的 A2A 消息路由到 `master_agent`，由配置的 LLM 生成响应。
5. 持续运行直到手动终止（Ctrl+C）。
