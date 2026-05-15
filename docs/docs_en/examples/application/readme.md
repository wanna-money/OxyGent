# Application Examples

Full application examples that showcase the breadth of OxyGent's features combined in a single multi-agent system.

---

## Examples

### Comprehensive Multi-Agent Demo

**File:** `examples/application/demo.py`

This example is a comprehensive demonstration of OxyGent's core capabilities assembled into one multi-agent application. It combines multiple tool types and agent patterns: three `StdioMCPClient` instances provide time querying (via `mcp-server-time`), file operations (via `@modelcontextprotocol/server-filesystem`), and math operations (via a custom `mcp_servers/math_tools.py`). An inline `FunctionHub` defines a `joke_tool` that returns random jokes. A `ChatAgent` ("intent_agent") uses a built-in intention recognition prompt. The system features three specialized agents coordinated by a master `ReActAgent`: a `time_agent` with custom input preprocessing (`func_process_input`) and `trust_mode=False`, a `file_agent` for filesystem operations, and a `WorkflowAgent` ("math_agent") that runs a custom `func_workflow` function. The workflow function demonstrates advanced OxyGent APIs including accessing short memory at both agent and master levels, sending SSE messages via `send_message`, cross-agent calls via `oxy_request.call()`, direct LLM invocation with custom parameters, and dynamic query parsing. The master agent applies a custom output formatting function (`func_format_output`) that prefixes responses with "Answer: ".

**Key Components:**
- `HttpLLM` -- LLM backend with low temperature for deterministic behavior
- `ChatAgent` ("intent_agent") -- agent using the built-in `INTENTION_PROMPT` for intent classification
- `FunctionHub` -- inline tool hub with a `joke_tool` demonstrating the `@fh.tool` decorator pattern
- `StdioMCPClient` ("time_tools") -- MCP client for timezone-aware time queries
- `StdioMCPClient` ("file_tools") -- MCP client for local filesystem operations
- `StdioMCPClient` ("math_tools") -- MCP client for mathematical computations (e.g., computing Pi)
- `ReActAgent` ("master_agent") -- orchestrator with custom `func_format_output` and sub-agent delegation
- `ReActAgent` ("time_agent") -- time query agent with custom `func_process_input` and non-trust mode
- `ReActAgent` ("file_agent") -- file operation agent
- `WorkflowAgent` ("math_agent") -- agent with a custom `func_workflow` showcasing memory access, SSE messaging, cross-agent calls, and direct LLM invocation
- `MAS` -- runtime container launching the web service with a Pi calculation query

**[Detailed Guide →](./demo.md)**

---
