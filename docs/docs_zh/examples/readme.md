# OxyGent 示例文档

本目录包含所有 OxyGent 示例脚本的文档，按功能领域分类组织。每个子目录涵盖框架的一个特定方面，所有示例均为可直接运行的独立脚本。

---

## 推荐入门

如果你是 OxyGent 新用户，建议先从以下三个示例开始：

| 示例 | 你将学到 |
|------|---------|
| [单智能体](./agents/demo_single_agent.md) | 最简 ChatAgent，自定义提示词与钩子 |
| [ReAct 智能体](./agents/demo_react_agent.md) | 带反思机制的 ReActAgent 与工具调用 |
| [层级多智能体](./agents/demo_hierarchical_agents.md) | 主从 Agent 架构与任务分发 |

---

## 分类目录

| 分类 | 示例数 | 说明 |
| ---- | :----: | ---- |
| [Agent 示例](./agents/readme.md) | 14 | Agent 类型、协作模式与回调钩子 |
| [高级功能](./advanced/readme.md) | 9 | 高级功能：RAG、SFT 数据生成、技能召回、评测 |
| [后端服务](./backend/readme.md) | 14 | Web 服务模式、SSE 流式、异步聊天、批处理 |
| [A2A 协议](./a2a/readme.md) | 20 | Agent-to-Agent 协议：服务端、客户端、流式、多智能体 |
| [工具](./tools/readme.md) | 4 | 工具类型：FunctionTool、HttpTool 与工具检索 |
| [LLM](./llms/readme.md) | 4 | LLM 集成：HttpLLM、OpenAILLM、LocalLLM、MockLLM |
| [流程编排](./flows/readme.md) | 2 | 流程编排：Reflexion 与 MathReflexion |
| [Bank 工具](./banks/readme.md) | 4 | BankTool / BankClient：基于 HTTP 的远程工具服务 |
| [MCP 工具](./mcp_tools/readme.md) | 3 | MCP 协议工具集成（Stdio、SSE、Streamable） |
| [分布式](./distributed/readme.md) | 3 | 基于 SSEOxyGent 的分布式多智能体系统 |
| [电商场景](./ecommerce/readme.md) | 5 | 电商领域：商品搜索、订单追踪、客服 |
| [动态提示词](./live_prompts/readme.md) | 2 | 热加载提示词管理与动态 Agent 更新 |
| [FH 工具集](./fh_tools/readme.md) | 1 | FunctionHub 工具集合 |
| [应用示例](./application/readme.md) | 1 | 完整应用示例 |
| [其他](./other/readme.md) | 1 | 其他示例 |

---

## 快速开始

1. 安装 OxyGent 及其依赖（参见主 README）。
2. 在 `.env` 文件中设置所需的环境变量：
   ```
   DEFAULT_LLM_API_KEY=your_api_key
   DEFAULT_LLM_BASE_URL=your_base_url
   DEFAULT_LLM_MODEL_NAME=your_model_name
   ```
3. 直接运行任意示例：
   ```bash
   python -m examples.agents.demo_single_agent
   ```
