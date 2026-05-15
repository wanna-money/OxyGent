# Bank Tools Examples

These examples demonstrate how to use OxyGent's Bank system to connect agents with remote tool servers, enabling dynamic tool discovery and cross-service tool invocation.

---

## Examples

### ReAct Agent with Bank (Rigid Mode)

**File:** `examples/banks/demo_bank_react_agent_rigid.py`

Demonstrates a ReActAgent that uses a remote BankClient as a data source through the `preceding_oxy` mechanism rather than as an autonomous tool. Before each execution, the agent automatically calls the `user_profile_retrieve` bank tool and injects the retrieved results into its prompt via the `${preceding_text}` placeholder. This "rigid" pattern means the agent always retrieves user profile data as a prerequisite step, without the LLM deciding whether to call the tool. A `func_filter` injects `group_data` with a user identifier into the request payload. The agent uses the `SYSTEM_PROMPT` from `oxygent.prompts` as its base prompt.

**Key Components:**
- `HttpLLM` -- language model backend
- `ReActAgent` -- reasoning agent with preceding_oxy and preceding_placeholder for rigid data injection
- `BankClient` -- connects to a remote bank server at `127.0.0.1:8090` to discover and register tools
- `SYSTEM_PROMPT` -- OxyGent's built-in system prompt

**[Detailed Guide →](./demo_bank_react_agent_rigid.md)**

---

### ReAct Agent with Bank (Autonomy Mode)

**File:** `examples/banks/demo_bank_react_agent_autonomy.py`

Shows a ReActAgent that has autonomous access to both local MCP tools and remote bank tools. Unlike the rigid example, here the BankClient is listed in the agent's `banks` parameter, allowing the LLM to decide when to call bank tools during its reasoning loop. The agent is also equipped with a `StdioMCPClient` providing time-related tools via the `mcp-server-time` package. This autonomy pattern lets the agent freely combine local tools (time queries) and remote bank tools (user profile operations) as needed to answer questions.

**Key Components:**
- `HttpLLM` -- language model backend
- `StdioMCPClient` -- MCP stdio client for time tools (`mcp-server-time`)
- `ReActAgent` -- reasoning agent with both `tools` and `banks` for autonomous tool selection
- `BankClient` -- connects to a remote bank server for user profile tools

**[Detailed Guide →](./demo_bank_react_agent_autonomy.md)**

---

### ReAct Agent with Bank via MCP Protocol

**File:** `examples/banks/demo_bank_react_agent_autonomy_by_mcp.py`

An alternative approach to connecting a ReActAgent with a remote bank server, using the MCP SSE protocol instead of the BankClient HTTP API. The remote bank tools are accessed through an `SSEMCPClient` pointing to the bank server's SSE endpoint, and are listed directly in the agent's `tools` parameter alongside the local time MCP tools. This means the agent treats the remote bank tools identically to any other MCP tool. This pattern is useful when the bank server exposes an MCP-compatible SSE interface, providing a unified tool protocol for both local and remote tools.

**Key Components:**
- `HttpLLM` -- language model backend
- `StdioMCPClient` -- MCP stdio client for time tools (`mcp-server-time`)
- `SSEMCPClient` -- MCP SSE client connecting to the remote bank server's SSE endpoint
- `ReActAgent` -- reasoning agent using both MCP clients as tools

**[Detailed Guide →](./demo_bank_react_agent_autonomy_by_mcp.md)**

---

### Chat Agent with Bank and Memory Dump

**File:** `examples/banks/demo_bank_chat_agent_dump_memory.py`

Demonstrates a ChatAgent that retrieves user profile data before answering and writes conversation history back to the bank after each response. The agent uses `preceding_oxy` to call `user_profile_retrieve` and inject results into its prompt via `${preceding_text}`. After generating a response, the custom `func_process_output` callback (`dump_memory`) serializes the query-answer pair and asynchronously deposits it into the `user_profile_deposit` bank tool. This creates a read-write loop: the agent reads user profile data to inform its answers and writes the interaction history back for future retrieval, enabling a persistent user memory system across conversations.

**Key Components:**
- `HttpLLM` -- language model backend
- `ChatAgent` -- conversational agent with preceding_oxy for data retrieval and func_process_output for post-processing
- `BankClient` -- connects to a remote bank server providing both retrieve and deposit tools
- `dump_memory` -- custom output hook that writes conversation history back to the bank

**[Detailed Guide →](./demo_bank_chat_agent_dump_memory.md)**
