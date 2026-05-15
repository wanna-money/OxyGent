# MCP Tools Examples

Examples demonstrating how to integrate MCP (Model Context Protocol) tool servers with OxyGent agents using `StdioMCPClient`.

---

## Examples

### Browser Automation Demo

**File:** `examples/mcp_tools/browser_demo.py`

This example builds a multi-agent system that combines browser automation with file system operations. A master `ReActAgent` coordinates two specialized sub-agents: a browser agent equipped with a custom browser MCP server (`mcp_servers/browser/server.py` via `StdioMCPClient`) for web navigation, page content extraction, and automated login handling, and a file agent equipped with the `@modelcontextprotocol/server-filesystem` MCP server for reading and writing local files. The demo's default task searches for weather information online and saves the extracted results to a local text file, showcasing cross-agent task delegation with detailed system prompts that govern context passing, error handling, and result integration.

**Key Components:**
- `HttpLLM` -- LLM backend configured from environment variables
- `StdioMCPClient` ("browser_tools") -- launches a custom browser MCP server for web scraping and automation
- `StdioMCPClient` ("file_tools") -- launches the official filesystem MCP server for local file operations
- `ReActAgent` ("browser_agent") -- specialized agent for browser tasks with login-detection logic
- `ReActAgent` ("file_agent") -- specialized agent for file system tasks with input validation
- `ReActAgent` ("master_agent") -- orchestrator that delegates tasks to browser and file sub-agents
- `MAS` -- runtime container that starts the web service UI

**[Detailed Guide →](./browser_demo.md)**

---

### Text-to-Speech (TTS) Demo

**File:** `examples/mcp_tools/tts_demo.py`

This example demonstrates using a custom TTS (Text-to-Speech) MCP server with OxyGent. It creates a `StdioMCPClient` that launches the `mcp_servers/tts_tools.py` server using the current Python interpreter. The TTS agent, a `ReActAgent`, can convert text to speech via Microsoft Edge TTS, stop audio playback, and list available voices. Key features include automatic audio caching in a `tts_audio_cache/` directory, intelligent text chunking for long texts, and support for multiple Chinese and English voice options. A master agent coordinates routing of user requests to the TTS agent.

**Key Components:**
- `HttpLLM` -- LLM backend for agent reasoning
- `StdioMCPClient` ("tts_tools") -- launches the TTS MCP server for speech synthesis and playback
- `ReActAgent` ("tts_agent") -- handles text-to-speech requests with Edge TTS voices
- `ReActAgent` ("master_agent") -- routes user requests to the TTS sub-agent
- `MAS` -- runtime container with web service and welcome message

**[Detailed Guide →](./tts_demo.md)**

---

### Train Ticket Query Demo

**File:** `examples/mcp_tools/demo_train_ticket.py`

This example showcases using a `FunctionHub` tool (imported from `function_hubs/train_ticket_tools.py`) with a `ReActAgent` to build a Chinese railway (12306) ticket query assistant. The FunctionHub provides three tools: `get_stations_of_city` to look up station codes by city name, `get_tickets` to query available train tickets between stations on a given date, and `get_current_date` to resolve relative dates like "tomorrow". The agent operates with `trust_mode=False`, meaning it validates tool calls before execution. The demo starts a web service with a bilingual welcome message explaining sample queries users can try.

**Key Components:**
- `HttpLLM` -- LLM backend with low temperature for precise tool-calling
- `FunctionHub` ("train_ticket_tools") -- Python function tools for 12306 station lookup, ticket querying, and date resolution
- `ReActAgent` ("train_ticket_agent") -- single agent that reasons over and calls the train ticket tools
- `MAS` -- runtime container launching the web service with a sample query

**[Detailed Guide →](./demo_train_ticket.md)**

---
