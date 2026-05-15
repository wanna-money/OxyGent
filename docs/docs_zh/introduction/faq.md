# 常见问题解答 (FAQ)

---

## 1. ChatAgent 和 ReActAgent 有什么区别？

`ChatAgent` 是最基础的对话智能体，每次请求只进行一次 LLM 调用，不支持工具调用。适用于纯对话场景。

`ReActAgent` 实现了 ReAct（Reasoning and Acting）范式，能够在推理和行动之间交替循环：LLM 先思考（Thought），然后决定调用哪个工具（Action），获取结果（Observation），再继续思考，直到得出最终答案。适用于需要调用工具或子智能体的任务。

简单规则：不需要工具用 `ChatAgent`，需要工具用 `ReActAgent`。

---

## 2. FunctionHub 和 MCP 工具如何选择？

**FunctionHub** 适用于将本地 Python 函数注册为工具。直接在代码中定义，零网络开销，调试方便。

```python
hub = oxy.FunctionHub(name="my_tools")

@hub.tool(description="查询天气")
def get_weather(city: str) -> str:
    return f"{city} 晴天"
```

**MCP 工具**（StdioMCPClient / SSEMCPClient / StreamableMCPClient）适用于接入外部工具服务器，特别是社区已有的 MCP 服务（如文件系统、数据库、浏览器等）。工具运行在独立进程中，支持跨语言。

简单规则：自己写的 Python 函数用 FunctionHub，接入外部服务用 MCP。

---

## 3. 没有 Elasticsearch 和 Redis 能用吗？

**可以。** OxyGent 在没有外部数据库时会自动降级为本地实现：

- Elasticsearch -> `LocalEs`（基于本地文件存储）或 `MemoryEs`（纯内存）
- Redis -> `LocalRedis`（基于本地队列）

本地模式完全满足开发调试需求。生产环境建议配置 Elasticsearch 以支持对话持久化和追踪查询，配置 Redis 以支持 SSE 消息队列。

---

## 4. 支持哪些 LLM？

OxyGent 通过 `HttpLLM` 支持所有兼容 OpenAI Chat Completions API 的模型，包括但不限于：

- OpenAI（GPT-4o、GPT-4、GPT-3.5 等）
- DeepSeek
- 通义千问（Qwen）
- 智谱 AI（GLM）
- Anthropic Claude（通过兼容层）
- 各类本地部署的开源模型（vLLM、Ollama 等）

此外还提供：
- `OpenAILLM`：使用 OpenAI 官方 SDK，支持更多高级特性。
- `LocalLLM`：直接加载 HuggingFace 模型到本地运行，无需 API。
- `MockLLM`：返回固定内容的模拟模型，用于单元测试。

---

## 5. 如何部署到生产环境？

推荐步骤：

1. **配置外部数据库**：设置 Elasticsearch 和 Redis 连接，确保对话持久化和 SSE 消息可靠传递。
2. **使用 Config 管理配置**：通过 `config.json` 分环境管理参数（`default` / `production`），通过 `APP_ENV` 环境变量切换。
3. **启动 Web 服务**：`start_web_service()` 基于 FastAPI + Uvicorn，可直接在生产环境使用。
4. **反向代理**：在前面部署 Nginx 或网关，处理 HTTPS、负载均衡等。
5. **监控追踪**：利用 Elasticsearch 中存储的 trace 数据进行监控和告警。

```python
# 生产环境示例
Config.load_from_json("config.json")  # 加载配置文件

async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(host="0.0.0.0", port=8080)
```

---

## 6. 如何调试智能体？

OxyGent 提供多层调试手段：

- **Web UI 可视化**：`start_web_service()` 内置调试界面，可实时查看智能体的思考过程、工具调用和中间结果。
- **CLI 模式**：`start_cli_mode()` 在终端中交互，日志直接输出到控制台。
- **日志系统**：OxyGent 内置结构化日志，每次执行自动记录 trace_id、输入输出、耗时等信息。
- **Elasticsearch 追踪**：配置 ES 后，所有执行记录可在 ES 中查询回溯。
- **MockLLM**：使用 `MockLLM` 替代真实 LLM，在不消耗 API 配额的情况下测试流程。

---

## 7. Workflow 和 Flow 有什么区别？

**Flow**（`BaseFlow`）是流程的抽象基类，所有智能体（`BaseAgent`）和预设流程都继承自它。Flow 定义了"包含多步执行逻辑"的组件。

**Workflow** 是一种具体的 Flow 实现，允许你自定义执行步骤序列。适用于固定流程的场景，如"先检索 -> 再总结 -> 最后格式化"。

此外还有其他预设 Flow：
- `PlanAndSolve`：先让 LLM 制定计划，再逐步执行。
- `Reflexion`：执行后自我反思，不满意则重做。
- `MathReflexion`：针对数学任务的反思流程。

---

## 8. 智能体之间能互相调用吗？

**能。** 通过 `sub_agents` 参数声明子智能体，master 智能体可以在推理过程中调用子智能体。子智能体本身也可以有自己的子智能体和工具，形成多层级的组织结构。

```python
oxy_space = [
    oxy.ReActAgent(name="researcher", desc="负责信息检索", tools=["search_tools"]),
    oxy.ReActAgent(name="writer", desc="负责内容撰写"),
    oxy.ReActAgent(
        name="master",
        is_master=True,
        sub_agents=["researcher", "writer"],
    ),
]
```

master 智能体会根据用户意图自动判断调度哪个子智能体。子智能体的 `desc` 是 master 做出调度决策的关键依据。

---

## 9. 如何管理记忆和上下文？

OxyGent 提供多种记忆管理机制：

- **短期记忆**：每轮对话的上下文自动维护，通过 `Config.set_agent_short_memory_size(n)` 控制保留轮数。
- **ReAct 记忆**：ReActAgent 的推理链（Thought/Action/Observation）可选择保留或丢弃（`is_discard_react_memory` 参数）。
- **记忆 Token 控制**：通过 `memory_max_tokens` 限制上下文长度，防止超出模型窗口。
- **共享数据**：`OxyRequest.shared_data` 在同一调用链的所有组件之间共享，适合传递结构化上下文。
- **全局数据**：`MAS.global_data` 在所有请求之间共享，适合存放全局配置或缓存。
- **续接执行**：通过 `from_trace_id` 从历史对话继续，保持上下文连贯。

---

## 10. 如何跨进程连接智能体？

OxyGent 提供两种跨进程通信方案：

### SSEOxyGent（OxyGent 内部协议）

将远程 OxyGent 服务作为本地智能体使用。远程服务通过 `start_web_service()` 暴露 SSE 接口，本地通过 `SSEOxyGent` 连接。

```python
# 远程服务（进程 A）
async with MAS(oxy_space=[...]) as mas:
    await mas.start_web_service(port=8081)

# 本地引用（进程 B）
oxy_space = [
    oxy.SSEOxyGent(name="remote_agent", server_url="http://localhost:8081"),
    oxy.ReActAgent(name="master", is_master=True, sub_agents=["remote_agent"]),
]
```

### A2AClientAgent（Google A2A 协议）

连接任何支持 A2A（Agent-to-Agent）协议的外部服务，实现跨框架互操作。

```python
oxy_space = [
    oxy.A2AClientAgent(
        name="external_agent",
        server_url="http://external-service:8080",
    ),
    oxy.ReActAgent(name="master", is_master=True, sub_agents=["external_agent"]),
]
```

---

[返回首页](./readme.md)
