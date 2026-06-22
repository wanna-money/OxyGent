# A2A OxyGent 任务跟进客户端

**源文件:** `examples/a2a/demo_a2a_oxygent_task_followup_client.py`

## 概述

本示例演示使用 `context_id` 和 `reference_task_ids` 进行多轮 A2A 对话。它向 A2A 服务器依次发送两条消息：第一条提出问题，第二条引用第一个任务来提出后续问题，验证服务器能够在 A2A 任务之间维护对话上下文。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`（服务端需要）
- 先启动 A2A 服务器：`PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py`

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_task_followup_client.py
```

## 代码详解

### 配置

- `SERVER_URL = "http://127.0.0.1:8090/a2a"` -- A2A 服务器端点。
- `Config.set_app_name("demo-a2a-oxygent-task-followup-client")` -- 应用名称，用于追踪。

### 组件（`oxy_space`）

一个组件：

- **`A2AClientAgent.minimal()`**：
  - `name="a2a_client"` -- 智能体标识符。
  - `streaming=False` -- 同步消息发送。
  - `timeout=60` -- 请求超时时间。
  - `enable_task_polling=True` -- 启用自动任务状态轮询，这对于服务器可能需要时间处理上下文的跟进场景很重要。

### 辅助函数：`call_once`

与基础客户端示例类似，但完整支持多轮对话参数：

- `context_id` -- 将同一会话中的消息关联起来。
- `task_id` -- 引用特定的先前任务以便继续对话。
- `reference_task_ids` -- 任务 ID 列表，服务器在处理新消息时应考虑这些任务的上下文。

### 入口

`main()` 协程执行两轮对话：

**第一轮：**
1. 发送查询"哪个数字最大，直接给出结果，1，5，7"。
2. 从响应中提取 `context_id` 和 `task_id`。
3. 验证两个会话标识符均存在；如果缺失则抛出 `RuntimeError`。

**第二轮（间隔1秒后）：**
1. 发送后续问题"哪个数字最小"，使用第一轮的 `context_id`。
2. 传入 `reference_task_ids=[task_id]`，让服务器知道此消息与前一个任务相关。
3. 打印响应，应正确识别原始数字集中的"1"为最小数字，证明上下文得到保留。

## 核心概念

- **`context_id`**：会话标识符，将多个 A2A 任务归入同一对话。服务器使用它来维护对话历史。
- **`reference_task_ids`**：将新任务显式关联到一个或多个先前任务。服务器可以利用这些引用加载先前交互的相关上下文。
- **`enable_task_polling=True`**：启用后，如果初始响应表明任务仍在进行中，客户端智能体将自动轮询服务器以获取任务完成状态。
- **多轮上下文**：A2A 协议支持有状态的对话。通过传递 `context_id` 和 `reference_task_ids`，智能体可以维持连贯的多轮对话。

## 预期行为

运行后（需先启动服务器）：

1. **第一轮**：打印 `[turn1]` 加上答案"7"（最大的数字），以及会话标识符。
2. **第二轮**：打印 `[turn2]` 加上答案"1"（最小的数字），证明服务器正确理解了在第一轮数字集上下文中的后续问题。
3. 两轮共享相同的 `context_id`，但各自拥有独立的 `task_id`。
