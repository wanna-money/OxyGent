# 什么是 A2A？

A2A（Agent-to-Agent）是由 Google 提出的开放协议，旨在实现不同框架、不同组织构建的智能体之间的互操作通信。

---

## 核心思想

随着智能体系统的普及，不同团队使用不同框架构建的智能体需要协作完成复杂任务。A2A 协议定义了智能体之间发现、通信和协作的标准方式，使得来自不同系统的智能体可以像调用本地组件一样互相调用。

### 核心概念

| 概念 | 说明 |
|------|------|
| Agent Card | 智能体名片，描述智能体的能力、技能和通信端点，通过 `/.well-known/agent.json` 暴露 |
| Task | 任务，一次交互的完整生命周期（已提交 / 进行中 / 已完成 / 失败等状态） |
| Message | 消息，客户端和服务端之间交换的通信单元 |
| Artifact | 产物，任务执行过程中产生的输出结果 |

### 工作流程

```
┌─────────────┐                     ┌─────────────┐
│  Agent A     │  1. 发现 Agent Card  │  Agent B     │
│ （A2A 客户端）│ ──────────────────► │ （A2A 服务端）│
│              │                     │              │
│              │  2. 发送消息         │              │
│              │ ──────────────────► │              │
│              │                     │  3. 执行任务  │
│              │  4. 返回结果/流式更新 │              │
│              │ ◄────────────────── │              │
└─────────────┘                     └─────────────┘
```

1. **发现**：客户端获取服务端的 Agent Card，了解对方能力。
2. **发送**：客户端通过 `message/send` 或 `message/stream` 发送请求。
3. **执行**：服务端接收请求，执行任务。
4. **返回**：服务端返回结果，支持同步响应和 SSE 流式更新。

---

## OxyGent 的 A2A 支持

OxyGent 同时支持 A2A 的服务端和客户端角色。

### 作为 A2A 服务端

任何 OxyGent MAS 都可以一键开启 A2A 服务端能力，将内部智能体暴露给外部 A2A 客户端：

```python
async with MAS(oxy_space=oxy_space, enable_a2a_server=True) as mas:
    await mas.start_web_service()
```

MAS 会自动生成 Agent Card 并注册 A2A 协议端点，外部客户端通过 `/.well-known/agent.json` 即可发现并调用。

### 作为 A2A 客户端

通过 `A2AClientAgent` 连接任何 A2A 兼容的外部服务：

```python
oxy_space = [
    oxy.A2AClientAgent(
        name="external_agent",
        desc="外部翻译服务",
        server_url="http://translation-service:8080",
    ),
    oxy.ReActAgent(
        name="master",
        is_master=True,
        sub_agents=["external_agent"],
    ),
]
```

`A2AClientAgent` 会自动发现 Agent Card，支持同步请求和流式响应，对上层智能体完全透明--使用方式与本地子智能体一致。

### 设计理念

OxyGent 对 A2A 的实现遵循"协议网关"思路：A2A 不是一种新的智能体类型，而是一层协议适配。服务端将 A2A 请求转换为 MAS 内部调用，客户端将 A2A 响应转换为标准的 `OxyResponse`。最大化复用现有框架能力，最小化接入成本。

---

[返回首页](../readme.md)
