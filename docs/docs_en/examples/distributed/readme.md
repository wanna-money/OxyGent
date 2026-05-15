# Distributed Examples

These examples demonstrate how to build a distributed multi-agent system using OxyGent, where multiple independently deployed agent services communicate with each other via SSE (Server-Sent Events) connections.

---

## Examples

### Master Agent (Gateway)

**File:** `examples/distributed/app_master_agent.py`

This example sets up the master gateway agent that orchestrates a distributed multi-agent system. It defines a `ReActAgent` named `master_agent` (marked with `is_master=True`) that delegates tasks to two sub-agents: a local `file_agent` for querying local files via the `@modelcontextprotocol/server-filesystem` MCP tool, and a remote `math_agent` connected via `SSEOxyGent` pointing to a separate service on port 8081. The master agent uses `HttpLLM` for reasoning and starts a web service with an initial query asking for the first 30 positions of pi.

**Key Components:**
- `HttpLLM` — LLM backend configured via environment variables for reasoning
- `StdioMCPClient` ("file_tools") — MCP client wrapping the filesystem server for local file operations
- `ReActAgent` ("master_agent") — master orchestrator that routes tasks to sub-agents
- `ReActAgent` ("file_agent") — local agent for file queries using the filesystem MCP tool
- `SSEOxyGent` ("math_agent") — remote agent proxy connecting to the math service on port 8081

**[Detailed Guide →](./app_master_agent.md)**

---

### Math Agent Service

**File:** `examples/distributed/app_math_agent.py`

This example deploys a math-focused agent as an independent service on port 8081. It uses a `WorkflowAgent` with a custom `workflow` function that programmatically orchestrates multi-step logic: it first calls a remote `time_agent` (via `SSEOxyGent` on port 8082) to get the current time, then parses the user query to extract a number and calls the `calc_pi` MCP tool to compute pi to that many decimal places. The workflow demonstrates accessing conversation history via `get_short_memory()` at both the agent and master levels, and shows how to chain calls to remote agents and local tools within a single workflow function.

**Key Components:**
- `HttpLLM` — LLM backend for the math agent
- `StdioMCPClient` ("math_tools") — MCP client running the math tools server for pi computation
- `SSEOxyGent` ("time_agent") — remote agent proxy connecting to the time service on port 8082
- `WorkflowAgent` ("math_agent") — master agent with a custom `func_workflow` that chains calls to remote agents and tools
- `Config.set_app_name` / `Config.set_server_port` — configures this service as "app-math" on port 8081

**[Detailed Guide →](./app_math_agent.md)**

---

### Time Agent Service

**File:** `examples/distributed/app_time_agent.py`

This example deploys a simple time-query agent as an independent service on port 8082. It configures a `ReActAgent` named `time_agent` that uses the `mcp-server-time` MCP tool (run via `uvx`) with the `Asia/Shanghai` timezone to answer time-related queries. This is the simplest of the three distributed services and demonstrates how a single-purpose agent can be deployed as a standalone microservice that other agents in the system call remotely via SSE.

**Key Components:**
- `HttpLLM` — LLM backend for reasoning
- `StdioMCPClient` ("time_tools") — MCP client running the `mcp-server-time` server with Shanghai timezone
- `ReActAgent` ("time_agent") — single-purpose agent that answers time queries
- `Config.set_app_name` / `Config.set_server_port` — configures this service as "app-time" on port 8082

**[Detailed Guide →](./app_time_agent.md)**
