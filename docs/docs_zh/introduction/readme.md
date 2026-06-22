# OxyGent 中文教程

> 本系列文档将指导您使用 OxyGent 逐步搭建多智能体系统（MAS）。

---

## 选择你的路径

| 你的目标 | 从这里开始 |
|---------|-----------|
| 5 分钟构建第一个智能体 | [快速上手](./getting-started/quickstart.md) |
| 了解核心概念 | [概念总览](./getting-started/overview.md) |
| 了解架构设计 | [架构总览](./getting-started/architecture.md) |
| 给智能体添加工具 | [注册本地工具](./tools/register-tool.md) |
| 使用 MCP 协议工具 | [MCP 开源工具](./tools/opensource-mcp-tools.md) |
| 构建多智能体系统 | [多智能体系统](./multi-agent/multi-agent-system.md) |
| 并行运行智能体 | [并行调用](./multi-agent/parallel.md) |
| 部署为 Web 服务 | [Web API](./backend/web-api.md) |
| 跨进程连接智能体 | [分布式系统](./multi-agent/distributed.md) |
| 与 LangChain / LangGraph 互操作 | [A2A 快速上手](./a2a/demo-guide.md) |
| 生成 SFT 训练数据 | [训练数据](./advanced/training.md) |

---

## 快速开始

| 文档 | 说明 |
|------|------|
| [快速上手](./getting-started/quickstart.md)* | 5 分钟内构建智能体、添加工具、编排多智能体 |
| [OxyGent 概念总览](./getting-started/overview.md)* | 核心概念与术语 |
| [安装 OxyGent](./getting-started/install.md)* | 环境配置与安装 |
| [设置 Config](./getting-started/config.md)* | 配置 LLM、Agent、Server 等参数 |
| [架构总览](./getting-started/architecture.md) | 类层次结构、请求流程与部署模式 |

## 概念入门

| 文档 | 说明 |
|------|------|
| [什么是 ReAct？](./concepts/what-is-react.md) | ReActAgent 背后的推理+行动模式 |
| [什么是 MCP？](./concepts/what-is-mcp.md) | 模型上下文协议，跨语言工具集成 |
| [什么是 A2A？](./concepts/what-is-a2a.md) | Agent-to-Agent 协议，跨框架互操作 |

## 智能体

| 文档 | 说明 |
|------|------|
| [创建第一个智能体](./agents/create-agent.md)* | 注册 LLM 和 Agent |
| [和智能体交流](./agents/chat-with-agent.md) | Web UI、CLI、批处理、API 调用 |
| [选择 LLM](./agents/select-llm.md) | HttpLLM、OpenAILLM、LocalLLM、MockLLM |
| [预设提示词](./agents/select-prompt.md) | 自定义和追加 Prompt |
| [选择智能体种类](./agents/agent-types.md) | ChatAgent、ReActAgent、WorkflowAgent 等 |
| [动态提示词管理](./agents/live-prompts.md) | 运行时热加载 Prompt |

## 工具

| 文档 | 说明 |
|------|------|
| [注册本地工具](./tools/register-tool.md)* | FunctionHub 工具注册 |
| [使用 MCP 开源工具](./tools/opensource-mcp-tools.md)* | 接入社区 MCP 工具 |
| [使用 MCP 自定义工具](./tools/custom-mcp-tools.md)* | Stdio / SSE / Streamable MCP |
| [管理工具调用](./tools/manage-tools.md) | 工具检索、权限控制 |
| [文档工具指南](./tools/document-tools.md) | 文档解析与处理工具 |

## 多智能体系统

| 文档 | 说明 |
|------|------|
| [创建多智能体系统](./multi-agent/multi-agent-system.md)* | 主从 Agent 架构 |
| [Mixture of Agents](./multi-agent/mixture-of-agents.md) | 多 Agent 聚合决策 |
| [并行调用](./multi-agent/parallel.md)* | ParallelAgent 并发执行 |
| [分布式系统](./multi-agent/distributed.md)* | SSEOxyGent 跨进程通信 |

## 高级功能

| 文档 | 说明 |
|------|------|
| [响应元数据](./advanced/trust-mode.md) | Trust Mode 输出结构化元数据 |
| [处理查询和提示词](./advanced/process-input.md)* | func_process_input 钩子 |
| [处理 LLM 输出](./advanced/handle-output.md) | func_parse_llm_response 钩子 |
| [反思重做模式](./advanced/reflexion.md) | Reflexion / MathReflexion 流程 |
| [创建工作流](./advanced/workflow.md)* | Workflow 自定义执行流程 |
| [预设流](./advanced/preset-flows.md) | PlanAndSolve、Reflexion 等内置流 |
| [获取记忆和重新生成](./advanced/continue-exec.md) | 历史上下文与重新执行 |
| [多模态智能体](./advanced/multimodal.md)* | 图片、视频等多模态输入 |
| [检索增强生成 (RAG)](./advanced/rag.md)* | 外部知识检索与注入 |
| [生成训练样本](./advanced/training.md)* | SFT 数据自动生成 |

## 后端服务与调试

| 文档 | 说明 |
|------|------|
| [设置数据库](./backend/database.md) | Elasticsearch / Redis 配置 |
| [设置全局数据](./backend/global-data.md) | MAS 级全局共享数据 |
| [Web API](./backend/web-api.md) | FastAPI 端点与 SSE 流式接口 |
| [评分 API](./backend/rating-api.md) | 对话评分与反馈接口 |
| [可视化界面调试](./backend/debugging.md) | Web UI 调试工具 |

## A2A 协议

| 文档 | 说明 |
|------|------|
| [A2A 快速上手](./a2a/demo-guide.md) | A2A 服务端与客户端示例 |
| [A2A 设计与能力](./a2a/design.md) | A2A 协议架构与互操作 |

---

> 更多实战示例请参考 [示例文档](../examples/readme.md)。
>
> 常见问题？查看 [FAQ](./faq.md)。
