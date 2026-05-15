# OxyGent 客户端调用 LangChain A2A 服务端

**源文件:** `examples/a2a/langchain_interop/demo_oxygent_client_call_langchain_server.py`

## 概述

本示例使用 OxyGent 内置的 `A2AClientAgent` 调用远程 LangChain A2A 服务端。它展示了 OxyGent 消费任意 A2A 兼容服务的标准模式：配置一个 `A2AClientAgent`，将其注册到 `MAS` 中，然后通过 MAS 运行时执行请求。通信使用非流式的 `message/send` 路径，并启用任务轮询。

## 前置条件

- Python 3.10+
- 已安装 OxyGent（`pip install -r requirements.txt`）
- **必须先启动 LangChain A2A 服务端：**
  ```bash
  PYTHONPATH=. python examples/a2a/langchain_interop/demo_langchain_a2a_server.py
  ```

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/langchain_interop/demo_oxygent_client_call_langchain_server.py
```

## 代码详解

### 配置

- `SERVER_URL` 设为 `http://127.0.0.1:8101/a2a`，与 LangChain 服务端地址一致。
- `Config.set_app_name(...)` 设置应用标识，用于日志和追踪。

### 组件

**`A2AClientAgent.minimal(...)`** -- 创建最小化的 A2A 客户端 agent，参数包括：
- `name="langchain_client"` -- MAS 内部路由使用的 Oxy 名称。
- `server_url` -- LangChain 服务端的 A2A 端点。
- `streaming=False` -- 使用 `message/send`（同步）方法。
- `enable_task_polling=True` -- 发送后轮询 `tasks/get` 直到任务到达终态。
- `timeout=60` -- 60 秒 HTTP 超时。

**`call_once(mas, query, context_id, task_id)`** -- 辅助函数，构建指向 `langchain_client` agent 的 `OxyRequest` 并通过 MAS 执行。可选的 `context_id` 和 `task_id` 参数支持多轮会话。

### 入口

`main()` 协程：
1. 设置应用名称。
2. 创建包含单个 `A2AClientAgent` 的 `oxy_space`。
3. 通过异步上下文管理器打开 `MAS`。
4. 发送一条查询，要求服务端介绍自己并说明所属框架。
5. 打印响应输出和会话标识符（`context_id`、`task_id`）。

## 核心概念

- **A2AClientAgent**：OxyGent 内置的组件，用于调用任何 A2A 兼容服务端。自动处理 Agent Card 发现、消息格式化和任务生命周期管理。
- **MAS 作为运行时**：即使只有一个外部调用，agent 也注册在 `MAS` 实例中，由 MAS 管理 Oxy 生命周期（初始化、执行、清理）。
- **任务轮询**：启用 `enable_task_polling=True` 后，客户端可以处理返回 `working` 状态的服务端，并轮询等待任务完成。
- **非流式 A2A**：使用 `message/send` 进行简单的请求-响应交互。

## 预期行为

客户端发送一条中文查询，要求服务端介绍自己。控制台输出包括：
- `[turn1]` -- 服务端的响应，由于演示服务端回显输入，结果为 `[LangChain Server] <查询文本>`。
- `session:` -- 服务端返回的 `context_id` 和 `task_id`，可用于后续对话轮次。
