# OxyGent 客户端调用 LangGraph A2A 服务端

**源文件:** `examples/a2a/langgraph_interop/demo_oxygent_client_call_langgraph_server.py`

## 概述

本示例使用 OxyGent 内置的 `A2AClientAgent` 调用远程 LangGraph A2A 服务端。它展示了多轮对话支持：第一次查询后，响应中的 `context_id` 和 `task_id` 被传递到第二次调用中，通过 A2A 协议保持会话连续性。通信使用非流式的 `message/send` 路径，并启用任务轮询。

## 前置条件

- Python 3.10+
- 已安装 OxyGent（`pip install -r requirements.txt`）
- **必须先启动 LangGraph A2A 服务端：**
  ```bash
  PYTHONPATH=. python examples/a2a/langgraph_interop/demo_langgraph_a2a_server.py
  ```

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/langgraph_interop/demo_oxygent_client_call_langgraph_server.py
```

## 代码详解

### 配置

- `SERVER_URL` 设为 `http://127.0.0.1:8102/a2a`，与 LangGraph 服务端地址一致。
- `Config.set_app_name(...)` 设置应用标识。

### 组件

**`A2AClientAgent.minimal(...)`** -- 创建最小化的 A2A 客户端 agent，参数包括：
- `name="langgraph_client"` -- MAS 内部路由使用的 Oxy 名称。
- `server_url` -- LangGraph 服务端的 A2A 端点。
- `streaming=False` -- 使用 `message/send` 方法。
- `enable_task_polling=True` -- 轮询 `tasks/get` 直到任务完成。
- `timeout=60` -- 60 秒 HTTP 超时。

**`call_once(mas, query, context_id, task_id)`** -- 辅助函数，构建指向 `langgraph_client` agent 的 `OxyRequest` 并执行。可选的 `context_id` 和 `task_id` 参数支持多轮会话。

### 入口

`main()` 协程：
1. 设置应用名称。
2. 创建包含单个 `A2AClientAgent` 的 `oxy_space`。
3. 通过异步上下文管理器打开 `MAS`。
4. **第 1 轮**：发送查询，要求服务端介绍自己及所属框架。
5. **第 2 轮**：使用第 1 轮返回的 `context_id` 和 `task_id` 发送后续查询，要求服务端总结上一条回答。
6. 打印每轮的响应和会话标识符。

## 核心概念

- **多轮 A2A 会话**：通过将一次响应中的 `context_id` 和 `task_id` 传递到下一次请求，客户端在 A2A 协议边界上保持了对话上下文。
- **A2AClientAgent**：OxyGent 内置的组件，用于消费任何 A2A 服务端。自动处理 Agent Card 发现、消息格式化和任务生命周期。
- **任务轮询**：启用 `enable_task_polling=True` 后，客户端可以处理在完成前返回中间 `working` 状态的服务端。
- **MAS 生命周期**：`async with MAS(...)` 模式确保所有注册的 Oxy 组件被正确初始化和清理。

## 预期行为

客户端对 LangGraph 服务端执行两轮对话。控制台输出包括：

- `[turn1]` -- 服务端对第一条查询的响应（如 `[LangGraph Server] <查询文本>`）。
- `session:` -- 第 1 轮的 `context_id` 和 `task_id`。
- `[turn2]` -- 服务端对后续查询的响应，使用相同的会话上下文。
- `session:` -- 第 2 轮的会话标识符。

由于演示服务端只是回显输入，第 2 轮的响应会回显后续问题，而非真正总结第 1 轮。
