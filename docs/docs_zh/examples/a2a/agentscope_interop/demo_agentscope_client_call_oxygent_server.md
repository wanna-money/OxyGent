# AgentScope 客户端调用 OxyGent A2A 服务端

**源文件:** `examples/a2a/agentscope_interop/demo_agentscope_client_call_oxygent_server.py`

## 概述

本示例使用 AgentScope 内置的 `A2AAgent` 类调用 OxyGent A2A 服务端。它展示了 AgentScope agent 如何通过构造指向 OxyGent 服务端的 `AgentCard` 并通过 AgentScope 原生的 `Msg` 接口发送消息来实现与 OxyGent 的互操作。这是最简单的 AgentScope 作为客户端的示例。

## 前置条件

- Python 3.10+
- 额外依赖包：`pip install agentscope a2a`
- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`（OxyGent 服务端所需）
- **必须先启动 OxyGent A2A 服务端：**
  ```bash
  PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py
  ```

## 运行方式

```bash
PYTHONPATH=. python examples/a2a/agentscope_interop/demo_agentscope_client_call_oxygent_server.py
```

## 代码详解

### 配置

客户端目标为 `http://127.0.0.1:8090/a2a`，即 OxyGent A2A 服务端的默认地址。`AgentCard` 配置了 `streaming=False` 以使用非流式的 `message/send` 路径，避免 AgentScope 演示运行时中的异步流关闭竞态条件。

### 组件

**`build_oxygent_agent_card()`** -- 使用官方 `a2a.types` 模型创建 `AgentCard`。该卡片描述了远程 OxyGent 服务端的端点、能力和技能。卡片传递给 `A2AAgent`，使其知道在哪里以及如何通信。

**`A2AAgent`** -- AgentScope 内置的 A2A 互操作 agent 类。使用 Agent Card 初始化后，自动处理：
- 基于 Agent Card 的端点发现
- A2A 消息格式化和发送
- 响应解析

**`Msg`** -- AgentScope 的标准消息类型。客户端创建一个 `role="user"` 的 `Msg` 并包含查询内容，然后通过 `await agent(msg)` 调用模式传递给 `A2AAgent`。

### 入口

`main()` 协程：
1. 使用 OxyGent Agent Card 实例化一个 `A2AAgent`。
2. 创建一条用户消息，提问"哪个数字最大：1、5、7"。
3. 发送消息并等待响应。
4. 打印响应文本内容。
5. 包含一个简短的 `asyncio.sleep(0.1)` 以确保干净退出。

## 核心概念

- **AgentScope A2AAgent**：一个原生 AgentScope 组件，封装了 A2A 协议通信。接受一个 `AgentCard` 并暴露与 AgentScope 消息传递模式兼容的可调用接口。
- **AgentCard 作为连接描述符**：`AgentCard` 作为远程 agent 的完整描述 -- 包括 URL、能力和技能。通过手动构造一个，任何 A2A 服务端都可以被访问。
- **非流式简化**：示例故意设置 `streaming=False` 以避免演示运行时中的异步复杂性。生产部署可以启用流式传输。
- **跨框架互操作**：AgentScope 通过 A2A 协议原生消费 OxyGent 托管的 agent，只需 Agent Card 作为配置。

## 预期行为

客户端向 OxyGent 服务端发送一个数学问题。控制台输出包括：
- `[turn1]` -- OxyGent 服务端返回的 LLM 生成的答案（实际答案取决于配置的 LLM）。

交互为单轮，不涉及多轮会话管理。
