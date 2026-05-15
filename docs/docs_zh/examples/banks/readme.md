# Bank 工具示例

本目录包含了 OxyGent Bank 系统的使用示例，展示如何将 Agent 与远程工具服务器连接，实现动态工具发现和跨服务工具调用。

---

## 示例列表

### ReAct Agent 对接 Bank（刚性模式）

**文件:** `examples/banks/demo_bank_react_agent_rigid.py`

演示了一个通过 `preceding_oxy` 机制将远程 BankClient 作为数据源（而非自主工具）的 ReActAgent。在每次执行前，Agent 自动调用 `user_profile_retrieve` Bank 工具，并通过 `${preceding_text}` 占位符将检索结果注入到提示词中。这种"刚性"模式意味着 Agent 总是将用户画像数据检索作为前置步骤，而无需 LLM 自行判断是否调用该工具。`func_filter` 将包含用户标识的 `group_data` 注入到请求负载中。Agent 使用 `oxygent.prompts` 中的 `SYSTEM_PROMPT` 作为基础提示词。

**核心组件:**
- `HttpLLM` -- 语言模型后端
- `ReActAgent` -- 推理 Agent，使用 preceding_oxy 和 preceding_placeholder 实现刚性数据注入
- `BankClient` -- 连接到 `127.0.0.1:8090` 的远程 Bank 服务器，自动发现并注册工具
- `SYSTEM_PROMPT` -- OxyGent 内置系统提示词

**[详细文档 →](./demo_bank_react_agent_rigid.md)**

---

### ReAct Agent 对接 Bank（自主模式）

**文件:** `examples/banks/demo_bank_react_agent_autonomy.py`

展示了一个能自主使用本地 MCP 工具和远程 Bank 工具的 ReActAgent。与刚性模式不同，这里将 BankClient 配置在 Agent 的 `banks` 参数中，由 LLM 在推理循环中自行决定何时调用 Bank 工具。Agent 同时配备了通过 `mcp-server-time` 包提供时间查询功能的 `StdioMCPClient`。这种自主模式允许 Agent 根据需要自由组合本地工具（时间查询）和远程 Bank 工具（用户画像操作）来回答问题。

**核心组件:**
- `HttpLLM` -- 语言模型后端
- `StdioMCPClient` -- 用于时间工具的 MCP stdio 客户端（`mcp-server-time`）
- `ReActAgent` -- 同时使用 `tools` 和 `banks` 实现自主工具选择的推理 Agent
- `BankClient` -- 连接远程 Bank 服务器获取用户画像工具

**[详细文档 →](./demo_bank_react_agent_autonomy.md)**

---

### ReAct Agent 通过 MCP 协议对接 Bank

**文件:** `examples/banks/demo_bank_react_agent_autonomy_by_mcp.py`

展示了将 ReActAgent 与远程 Bank 服务器连接的另一种方式：使用 MCP SSE 协议替代 BankClient HTTP API。远程 Bank 工具通过指向 Bank 服务器 SSE 端点的 `SSEMCPClient` 访问，并直接列在 Agent 的 `tools` 参数中，与本地时间 MCP 工具并列。这意味着 Agent 将远程 Bank 工具与其他 MCP 工具同等对待。当 Bank 服务器暴露 MCP 兼容的 SSE 接口时，这种模式非常实用，它为本地和远程工具提供了统一的工具协议。

**核心组件:**
- `HttpLLM` -- 语言模型后端
- `StdioMCPClient` -- 用于时间工具的 MCP stdio 客户端（`mcp-server-time`）
- `SSEMCPClient` -- 连接远程 Bank 服务器 SSE 端点的 MCP SSE 客户端
- `ReActAgent` -- 使用两个 MCP 客户端作为工具的推理 Agent

**[详细文档 →](./demo_bank_react_agent_autonomy_by_mcp.md)**

---

### Chat Agent 对接 Bank 并回写记忆

**文件:** `examples/banks/demo_bank_chat_agent_dump_memory.py`

演示了一个在回答前检索用户画像数据、在每次响应后将对话历史写回 Bank 的 ChatAgent。Agent 使用 `preceding_oxy` 调用 `user_profile_retrieve` 并通过 `${preceding_text}` 将结果注入提示词。生成响应后，自定义的 `func_process_output` 回调（`dump_memory`）将查询-回答对序列化，并异步存入 `user_profile_deposit` Bank 工具。这形成了一个读写闭环：Agent 读取用户画像数据来辅助回答，同时将交互历史写回以供未来检索，从而实现跨对话的持久化用户记忆系统。

**核心组件:**
- `HttpLLM` -- 语言模型后端
- `ChatAgent` -- 使用 preceding_oxy 进行数据检索、func_process_output 进行后处理的对话 Agent
- `BankClient` -- 连接远程 Bank 服务器，提供检索和存储两种工具
- `dump_memory` -- 自定义输出钩子，将对话历史写回 Bank

**[详细文档 →](./demo_bank_chat_agent_dump_memory.md)**
