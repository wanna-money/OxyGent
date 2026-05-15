# OxyGent A2A Demo 说明

本文档描述 `examples/a2a` 下已调整后的目录结构、每个 Demo 的验证目标，以及跨框架互通演示方式。

## 1. 根目录（OxyGent 基础能力）

- `demo_a2a_oxygent_server.py`
- `demo_a2a_oxygent_client.py`
- `demo_a2a_oxygent_stream_client.py`
- `demo_a2a_oxygent_task_followup_client.py`

能力说明：
- `demo_a2a_oxygent_server.py`
  - 验证 OxyGent 作为 A2A Server 的最小启动能力
  - 对外提供 `/.well-known/agent.json` 和 A2A 请求入口
- `demo_a2a_oxygent_client.py`
  - 验证 OxyGent 作为 A2A Client 的最小调用链路
  - 展示单轮请求与 `context_id/task_id` 回传
- `demo_a2a_oxygent_stream_client.py`
  - 验证 OxyGent Client -> OxyGent Server 的流式消费能力
  - 重点观察流式增量输出与最终聚合结果
- `demo_a2a_oxygent_task_followup_client.py`
  - 验证 `context_id + reference_task_ids` 的 task 追问能力
  - 展示上下文下跨 task 的多轮关联语义

## 2. `agentscope_interop/`

- `demo_agentscope_client_call_oxygent_server.py`
- `demo_oxygent_client_call_agentscope_server.py`

能力说明：
- `demo_agentscope_client_call_oxygent_server.py`
  - 验证 AgentScope Client -> OxyGent Server
- `demo_oxygent_client_call_agentscope_server.py`
  - 验证 OxyGent Client -> AgentScope Server

该目录核心价值：
- 验证 OxyGent 在异构框架中的协议兼容性
- 验证 card 解析、流式/非流式消息路径可互通

## 3. `google_sdk_interop/`

- `demo_a2a_sdk_call_oxygent.py`
- `demo_a2a_sdk_stream_call_oxygent.py`

能力说明：
- `demo_a2a_sdk_call_oxygent.py`
  - 验证标准 A2A SDK 调用 OxyGent Server（非流式）
- `demo_a2a_sdk_stream_call_oxygent.py`
  - 验证标准 A2A SDK 调用 OxyGent Server（流式）

该目录核心价值：
- 证明 OxyGent A2A Server 与"框架无关 SDK"直接兼容

## 4. `langchain_interop/`

- `demo_langchain_a2a_server.py`
- `demo_langchain_client_call_oxygent_server.py`
- `demo_oxygent_client_call_langchain_server.py`

能力说明：
- `demo_langchain_a2a_server.py`
  - 启动 LangChain A2A Server 侧示例
- `demo_langchain_client_call_oxygent_server.py`
  - 验证 LangChain Client -> OxyGent Server
- `demo_oxygent_client_call_langchain_server.py`
  - 验证 OxyGent Client -> LangChain Server

## 5. `langgraph_interop/`

- `demo_langgraph_a2a_server.py`
- `demo_langgraph_client_call_oxygent_server.py`
- `demo_oxygent_client_call_langgraph_server.py`

能力说明：
- `demo_langgraph_a2a_server.py`
  - 启动 LangGraph A2A Server 侧示例
- `demo_langgraph_client_call_oxygent_server.py`
  - 验证 LangGraph Client -> OxyGent Server
- `demo_oxygent_client_call_langgraph_server.py`
  - 验证 OxyGent Client -> LangGraph Server

## 6. OxyGent A2A 能力地图（通过 Demo 可感知）

1. 基础协议能力：
- Agent Card 暴露与解析
- `message/send` 请求/响应

2. 任务与会话能力：
- `context_id/task_id` 透传
- `reference_task_ids` 追问关联
- `tasks/get` 轮询终态（在对应 client demo 中体现）

3. 流式能力：
- `message/stream` 事件流消费
- 增量输出与最终输出聚合

4. 跨框架互通能力：
- OxyGent 与 AgentScope / LangChain / LangGraph 双向互通
- OxyGent Server 被通用 A2A SDK 直接调用

---

## 相关示例

- [A2A 示例总览](../../examples/a2a/readme.md) — A2A 相关示例的完整列表与运行说明

---

[下一篇: A2A 设计与能力](./design.md)
[返回首页](../readme.md)
