# Tool Examples

This directory contains examples demonstrating how to register and use different tool types in OxyGent, including FunctionHub tools, MCP protocol tools, and preset document processing tools.

---

## Examples

### FunctionHub Tool

**File:** `examples/tools/demo_functionhub.py`

Demonstrates how to create a custom tool using FunctionHub and register it with an agent. A `FunctionHub` named `joke_tools` is defined, and a `joke_tool` function is registered onto it via the `@fh.tool()` decorator. The tool accepts a `joke_type` parameter (annotated with Pydantic `Field` for description) and returns a random joke from a hardcoded list. The FunctionHub is then passed into a ReActAgent's `tools` list so the agent can discover and invoke it during reasoning. The system is launched as a web service with an initial query asking for a joke.

**Key Components:**
- `FunctionHub` -- declares a named group of function-based tools
- `@fh.tool()` decorator -- registers an async function as a callable tool with a description
- `ReActAgent` -- reasoning agent that selects and invokes the registered tool
- `HttpLLM` -- backing language model

**[Detailed Guide →](./demo_functionhub.md)**

---

### MCP Tools (Stdio, SSE, Streamable)

**File:** `examples/tools/demo_mcp.py`

Shows how to connect external MCP (Model Context Protocol) tool servers to an agent using different transport types. Three `StdioMCPClient` instances are configured: `time_tools` (launched via `uvx mcp-server-time`), `map_tools` (launched via `npx @amap/amap-maps-mcp-server` with an API key environment variable), and `math_tools` (launched via `uv run` pointing to a local `math_tools.py` MCP server). Commented-out blocks also illustrate `SSEMCPClient` and `StreamableMCPClient` for SSE and streamable HTTP transports respectively. A ReActAgent is wired to the time and math tools and launched with a "What time is it" query.

**Key Components:**
- `StdioMCPClient` -- connects to MCP servers over stdio (subprocess-based)
- `SSEMCPClient` -- connects to MCP servers over Server-Sent Events (commented example)
- `StreamableMCPClient` -- connects to MCP servers over streamable HTTP (commented example)
- `ReActAgent` -- agent that discovers and invokes MCP tools
- `HttpLLM` -- backing language model

**[Detailed Guide →](./demo_mcp.md)**

---

### MCP Tools with Custom Headers

**File:** `examples/tools/demo_mcp_with_headers.py`

Demonstrates three mechanisms for passing HTTP headers to MCP tool servers using `StreamableMCPClient`, which is important for authentication and request customization. The example defines three `oxy_space` configurations: (1) static headers set directly on the `StreamableMCPClient` via the `headers` parameter; (2) dynamic headers from `shared_data` by enabling `is_dynamic_headers=True`, which reads headers from the request's `shared_data["headers"]` at call time; (3) inherited headers from the frontend HTTP request by enabling `is_inherit_headers=True`, which transparently forwards incoming request headers to the MCP server. When multiple header sources are active, the priority order is: frontend request headers > shared_data headers > static client headers.

**Key Components:**
- `StreamableMCPClient` -- MCP client with header customization support
- `headers` -- static header configuration
- `is_dynamic_headers` -- enables runtime headers from shared_data
- `is_inherit_headers` -- enables transparent forwarding of frontend request headers
- `ReActAgent` -- agent utilizing the configured MCP tools

**[Detailed Guide →](./demo_mcp_with_headers.md)**

---

### Document Processing Tools

**File:** `examples/tools/demo_document_tools.py`

A comprehensive demo showcasing OxyGent's preset document processing tools across five sub-examples. (1) Basic document processing: uses `detect_document_format` to identify file types, sizes, and supported operations for PDF/Word/Excel files. (2) Document processing agent: creates a ReActAgent equipped with `preset_tools.document_tools` and a detailed system prompt, enabling it to intelligently select the right tool for each document operation. (3) Batch processing: iterates over all documents in a directory, detects their formats, extracts metadata (e.g., page count, image count for PDFs via `get_pdf_info`), and generates a JSON report. (4) Document analysis agent: an advanced ReActAgent that combines `document_tools` and `file_tools` for deep content analysis and report generation. (5) Direct API usage: prints example code snippets showing how to call document tools directly from Python without an agent, covering PDF text extraction, PDF info, merge, split, Word reading, and Excel reading.

**Key Components:**
- `preset_tools.document_tools` -- built-in document processing FunctionHub (PDF, Word, Excel)
- `preset_tools.file_tools` -- built-in file system tools
- `detect_document_format` -- identifies document type and supported operations
- `get_pdf_info` -- extracts PDF metadata and content statistics
- `ReActAgent` -- agent for intelligent document processing
- `HttpLLM` -- backing language model

**[Detailed Guide →](./demo_document_tools.md)**
