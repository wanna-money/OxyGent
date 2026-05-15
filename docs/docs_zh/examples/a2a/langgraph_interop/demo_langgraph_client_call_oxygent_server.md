# LangGraph 客户端调用 OxyGent A2A 服务端

**源文件:** `examples/a2a/langgraph_interop/demo_langgraph_client_call_oxygent_server.py`

## 概述

本示例构建了一个 LangGraph `StateGraph`，作为 OxyGent A2A 服务端的客户端。图中包含一个节点，通过 HTTP 发起 A2A `message/send` 调用，展示了 LangGraph 的有状态图执行如何将外部 A2A agent 作为图节点集成。

## 前置条件

- Python 3.10+
- 额外依赖包：`pip install langgraph httpx`
- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`（OxyGent 服务端所需）
- **必须先启动 OxyGent A2A 服务端：**
  ```bash
  PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py
  ```

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/langgraph_interop/demo_langgraph_client_call_oxygent_server.py
```

## 代码详解

### 配置

客户端连接到 `http://127.0.0.1:8090/a2a`，即 OxyGent A2A 服务端的默认端点。

### 组件

**`GraphState`** -- 一个包含五个字段的 `TypedDict`：`query`、`answer`、`context_id`、`task_id` 和 `raw_task`。该状态在图中流转，同时捕获 A2A 响应和会话元数据。

**`extract_task_text(task)`** -- 从 A2A 任务中提取文本答案，优先检查 `status.message.parts`，回退到 `artifacts[0].parts`。

**`send_a2a(query, context_id, task_id)`** -- 一个异步函数，构造 A2A `message/send` JSON-RPC 负载并通过 httpx 发送。返回原始任务字典和提取的文本。支持可选的 `contextId` 和 `taskId` 以实现多轮会话。

**`call_node(state)`** -- 图节点函数。使用当前查询和会话状态调用 `send_a2a`，然后返回更新后的 `GraphState`，其中答案和会话标识符从 A2A 响应中填充。

**编译后的图** -- 一个 `StateGraph`，包含单个 `call` 节点连接到 `END`。图被编译为可通过 `ainvoke` 调用的可执行对象。

### 入口

`main()` 协程：
1. 使用初始查询调用图，提问"哪个数字最大：1、5、7"。
2. 打印原始任务 JSON 和提取的答案。

## 核心概念

- **A2A 作为图节点**：将 A2A HTTP 调用包装在 LangGraph 节点中，外部 agent 成为基于图的工作流中的一等参与者。可以添加更多节点进行前后处理或多 agent 编排。
- **有状态的会话跟踪**：`GraphState` 在图调用间传递 `context_id` 和 `task_id`，通过 A2A 协议实现多轮对话。
- **异步图执行**：`ainvoke` 方法异步运行图，这是必要的，因为 A2A 调用本身是异步的。
- **跨框架互操作**：LangGraph 工作流通过框架无关的 A2A 协议消费 OxyGent 驱动的 agent。

## 预期行为

客户端通过 LangGraph 管道向 OxyGent 服务端发送一个数学问题。控制台输出包括：
- `[turn1 raw]` -- OxyGent 服务端返回的完整 A2A 任务 JSON
- `[turn1]` -- 提取的 LLM 答案文本
