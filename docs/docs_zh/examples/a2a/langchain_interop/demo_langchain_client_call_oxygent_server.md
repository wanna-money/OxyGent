# LangChain 客户端调用 OxyGent A2A 服务端

**源文件:** `examples/a2a/langchain_interop/demo_langchain_client_call_oxygent_server.py`

## 概述

本示例展示了一个基于 LangChain 的客户端向 OxyGent A2A 服务端发送请求。它使用 LangChain 的 `RunnableLambda` 原语进行前处理和后处理，而实际的 A2A 通信通过原始 HTTP（httpx）完成。这展示了 LangChain 管道如何通过 A2A 协议与 OxyGent 实现互操作。

## 前置条件

- Python 3.10+
- 额外依赖包：`pip install langchain-core httpx`
- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`（OxyGent 服务端所需）
- **必须先启动 OxyGent A2A 服务端：**
  ```bash
  PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py
  ```

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/langchain_interop/demo_langchain_client_call_oxygent_server.py
```

## 代码详解

### 配置

客户端连接到 `http://127.0.0.1:8090/a2a`，这是 OxyGent A2A 服务端的默认端点。

### 组件

**`extract_task_text(task)`** -- 从 A2A 任务响应中提取文本答案的工具函数。优先检查 `status.message.parts`，回退到 `artifacts[0].parts`。

**`send_once(client, query, context_id, task_id)`** -- 构造并发送 A2A `message/send` JSON-RPC 请求。构建标准的 A2A 消息信封，角色为 `user`，包含文本部分，以及可选的 `contextId`/`taskId` 用于多轮会话。返回原始任务和提取的文本。

**LangChain Runnables：**
- `pre` -- 一个 `RunnableLambda`，在发送前为查询添加 `[LangChain Client]` 前缀。
- `post` -- 一个 `RunnableLambda`，去除响应文本的首尾空白。

### 入口

`main()` 协程执行一轮对话：
1. 通过 `pre` runnable 对查询进行前处理。
2. 通过 `send_once` 将查询发送到 OxyGent 服务端。
3. 打印原始任务 JSON 和后处理后的文本。

## 核心概念

- **跨框架互操作**：LangChain 管道作为客户端调用 OxyGent 托管的 agent，展示了 A2A 协议可实现无缝的跨框架通信。
- **A2A 消息信封**：客户端构造标准的 A2A JSON-RPC 负载，使用 `message/send` 方法、消息部分和可选的会话标识符。
- **RunnableLambda 作为粘合层**：LangChain runnables 处理前后处理，原始 HTTP 处理 A2A 传输 -- 展示了 A2A 如何融入现有管道。

## 预期行为

当 OxyGent 服务端和本客户端都在运行时，客户端发送一个查询"哪个数字最大：1、5、7"。控制台输出包括：
- `[turn1 raw]` -- OxyGent 服务端返回的完整 A2A 任务 JSON
- `[turn1]` -- 从 LLM 提取并修剪后的答案文本
