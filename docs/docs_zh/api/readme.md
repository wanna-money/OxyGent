# OxyGent API 参考文档

> 所有 OxyGent 组件的详细类文档。每个页面包含参数、方法、继承层次和使用示例。

## Agents
---
+ [BaseOxy](./agent/base_oxy.md) — 所有 OxyGent 组件的通用基类
+ [BaseFlow](./agent/base_flow.md) — 执行流程的基类
+ [BaseAgent](./agent/base_agent.md) — 所有智能体的基类
+ [LocalAgent](./agent/local_agent.md) — 本地运行的 LLM 智能体
+ [ChatAgent](./agent/chat_agent.md) — 单轮对话智能体
    + [RAGAgent](./agent/rag_agent.md) — 检索增强生成智能体
+ [ReActAgent](./agent/react_agent.md) — 推理+行动循环，支持工具调用
    + [ShellUseAgent](./agent/shell_use_agent.md) — SSH 远程命令执行
    + [SkillAgent](./agent/skill_agent.md) — 动态加载技能的智能体
+ [ParallelAgent](./agent/parallel_agent.md) — 并行子任务执行
+ [WorkflowAgent](./agent/workflow_agent.md) — 自定义步骤式工作流
+ [PlanAndSolveAgent](./agent/plan_and_solve_agent.md) — 先规划后执行
+ [RemoteAgent](./agent/remote_agent.md) — 连接其他进程中的智能体
    + [SSEOxyGent](./agent/sse_oxy_agent.md) — 基于 SSE 的分布式智能体
    + [A2AClientAgent](./agent/a2a_client_agent.md) — A2A 协议客户端智能体

## 工具
---
+ [BaseTool](./tools/base_tools.md) — 所有工具的基类
+ [HttpTool](./api_tools/http_tool.md) — HTTP API 包装工具
+ [FunctionTool](./function_tools/function_tool.md) — 单个 Python 函数工具
+ [FunctionHub](./function_tools/function_hub.md) — Python 函数工具集合
+ [MCPTool](./tools/mcp_tool.md) — MCP 协议工具包装器
+ [BaseMCPClient](./tools/base_mcp_client.md) — MCP 客户端基类
    + [StdioMCPClient](./tools/stdio_mcp_client.md) — 基于 stdio 的 MCP 传输
    + [SSEMCPClient](./tools/sse_mcp_client.md) — 基于 SSE 的 MCP 传输
    + [StreamableMCPClient](./tools/streamable_mcp_client.md) — 基于 Streamable HTTP 的 MCP
+ [BaseBank](./bank_tools/base_bank.md) — 工具银行基类
    + [BankTool](./bank_tools/bank_tool.md) — 服务端工具银行
    + [BankClient](./bank_tools/bank_client.md) — 远程工具银行客户端

## 预置工具
---
+ [Preset Tools（10 个 FunctionHub 集合）](./preset_tools.md) — 内置工具：file、math、time、shell、python、http、image_gen、ssh、string、system

## 流程
---
+ [WorkFlow](./flows/workflow.md) — 顺序步骤执行
+ [ParallelFlow](./flows/parallel_flow.md) — 并发步骤执行
+ [PlanAndSolve](./flows/plan_and_solve.md) — 分解 → 规划 → 求解
+ [Reflexion（+ MathReflexion）](./flows/reflexion.md) — 自我反思与重试循环

## LLM
---
+ [BaseLLM](./llms/base_llm.md) — 所有 LLM 集成的基类
+ [RemoteLLM](./llms/remote_llm.md) — 远程 API LLM 基类
    + [HttpLLM](./llms/http_llm.md) — 通过 HTTP API 调用模型
    + [OpenAILLM](./llms/openai_llm.md) — 通过 OpenAI SDK 调用模型
+ [LocalLLM](./llms/local_llm.md) — 本地加载 HuggingFace 模型
+ [MockLLM](./llms/mock_llm.md) — 测试用模拟模型

## 数据库
---
+ [BaseDB](./databases/base_db.md) — 数据库接口基类
+ [BaseES](./databases/db_es/base_es.md) — Elasticsearch 基类
    + [JesES](./databases/db_es/jes_es.md) — 京东 Elasticsearch
    + [LocalES](./databases/db_es/local_es.md) — 基于文件的本地 ES 回退
    + [MemoryEs](./databases/db_es/memory_es.md) — 内存 ES（测试用）
+ [BaseRedis](./databases/db_redis/base_redis.md) — Redis 基类
    + [JimdbApRedis](./databases/db_redis/jimdb_ap_redis.md) — 京东 Redis
    + [LocalRedis](./databases/db_redis/local_redis.md) — 基于文件的本地 Redis 回退
+ [BaseVectorDB](./databases/db_vector/base_vector_db.md) — 向量数据库基类
    + [VearchDB](./databases/db_vector/vearch_db.md) — Vearch 向量数据库

## 数据模型
---
+ [OxyRequest / OxyResponse / OxyState](./schemas/oxy.md) — 核心请求/响应类型
+ [LLMState / LLMResponse](./schemas/llm.md) — LLM 交互类型
+ [Message / Memory](./schemas/memory.md) — 对话历史与记忆
+ [Observation / ExecResult](./schemas/observation.md) — 工具执行结果
+ [SkillMetadata](./schemas/skill.md) — 技能定义元数据
+ [Evaluation（评分模型）](./schemas/evaluation.md) — 评分与评估类型

## MAS 系统模块
---
+ [Config](./config.md) — 全局配置单例
+ [MAS](./mas.md) — 多智能体系统运行时容器
+ [DBFactory](./db_factory.md) — 数据库连接工厂
+ [EmbeddingCache](./embedding_cache.md) — Embedding 向量缓存
+ [OxyFactory](./oxy_factory.md) — 组件反序列化工厂

## Live Prompt
---
+ [Live Prompt](./live_prompt.md) — PromptManager、PromptOptimizer、VersionSync、DynamicAgentManager

## Transport
---
+ [A2A Protocol](./transport_a2a.md) — A2AServerGateway、A2AInMemoryStore
