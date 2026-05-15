# OxyGent API 文档

## Agents
---
+ [BaseOxy](./agent/base_oxy.md)
+ [BaseFlow](./agent/base_flow.md)
+ [BaseAgent](./agent/base_agent.md)
+ [LocalAgent](./agent/local_agent.md)
+ [ChatAgent](./agent/chat_agent.md)
    + [RAGAgent](./agent/rag_agent.md)
+ [ReActAgent](./agent/react_agent.md)
    + [ShellUseAgent](./agent/shell_use_agent.md)
    + [SkillAgent](./agent/skill_agent.md)
+ [ParallelAgent](./agent/parallel_agent.md)
+ [WorkflowAgent](./agent/workflow_agent.md)
+ [PlanAndSolveAgent](./agent/plan_and_solve_agent.md)
+ [RemoteAgent](./agent/remote_agent.md)
    + [SSEOxyGent](./agent/sse_oxy_agent.md)
    + [A2AClientAgent](./agent/a2a_client_agent.md)

## 工具
---
+ [BaseTool](./tools/base_tools.md)
+ [HttpTool](./api_tools/http_tool.md)
+ [FunctionTool](./function_tools/function_tool.md)
+ [FunctionHub](./function_tools/function_hub.md)
+ [MCPTool](./tools/mcp_tool.md)
+ [BaseMCPClient](./tools/base_mcp_client.md)
    + [StdioMCPClient](./tools/stdio_mcp_client.md) 
    + [SSEMCPClient](./tools/sse_mcp_client.md)
    + [StreamableMCPClient](./tools/streamable_mcp_client.md)
+ [BaseBank](./bank_tools/base_bank.md)
    + [BankTool](./bank_tools/bank_tool.md)
    + [BankClient](./bank_tools/bank_client.md)

## 预置工具
---
+ [Preset Tools（10 个 FunctionHub 集合）](./preset_tools.md)

## 流程
---
+ [WorkFlow](./flows/workflow.md)
+ [ParallelFlow](./flows/parallel_flow.md)
+ [PlanAndSolve](./flows/plan_and_solve.md)
+ [Reflexion（+ MathReflexion）](./flows/reflexion.md)

## LLM
---
+ [BaseLLM](./llms/base_llm.md)
+ [RemoteLLM](./llms/remote_llm.md)
    + [HttpLLM](./llms/http_llm.md)
    + [OpenAILLM](./llms/openai_llm.md)
+ [LocalLLM](./llms/local_llm.md)
+ [MockLLM](./llms/mock_llm.md)

## 数据库
---
+ [BaseDB](./databases/base_db.md)
+ [BaseES](./databases/db_es/base_es.md)
    + [JesES](./databases/db_es/jes_es.md)
    + [LocalES](./databases/db_es/local_es.md)
    + [MemoryEs](./databases/db_es/memory_es.md)
+ [BaseRedis](./databases/db_redis/base_redis.md)
    + [JimdbApRedis](./databases/db_redis/jimdb_ap_redis.md)
    + [LocalRedis](./databases/db_redis/local_redis.md)
+ [BaseVectorDB](./databases/db_vector/base_vector_db.md)
    + [VearchDB](./databases/db_vector/vearch_db.md)

## 数据模型
---
+ [OxyRequest / OxyResponse / OxyState](./schemas/oxy.md)
+ [LLMState / LLMResponse](./schemas/llm.md)
+ [Message / Memory](./schemas/memory.md)
+ [Observation / ExecResult](./schemas/observation.md)
+ [SkillMetadata](./schemas/skill.md)
+ [Evaluation（评分模型）](./schemas/evaluation.md)

## MAS 系统模块
---
+ [Config](./config.md)
+ [MAS](./mas.md)
+ [DBFactory](./db_factory.md)
+ [EmbeddingCache](./embedding_cache.md)
+ [OxyFactory](./oxy_factory.md)

## Live Prompt
---
+ [Live Prompt（PromptManager、PromptOptimizer、VersionSync、DynamicAgentManager）](./live_prompt.md)

## Transport
---
+ [A2A Protocol（A2AServerGateway、A2AInMemoryStore）](./transport_a2a.md)
