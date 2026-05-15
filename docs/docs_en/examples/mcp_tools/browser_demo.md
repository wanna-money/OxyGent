# Browser Automation Demo

**Source:** `examples/mcp_tools/browser_demo.py`

## Overview

This example demonstrates a multi-agent browser automation system using OxyGent. A master agent coordinates two specialized sub-agents -- a browser agent for web scraping/navigation and a file agent for filesystem operations -- to perform tasks like searching the web, extracting data, and saving results to files. The demo is implemented as a `BrowserDemo` class with detailed system prompts for each agent role.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- OxyGent package installed (`pip install -r requirements.txt`)
- Node.js (for the filesystem MCP tool via `npx`)
- `uv` available on PATH (for running the browser MCP server)
- A `./mcp_servers/browser/server.py` file (custom browser MCP server)
- A `./local_file` directory for file operations

## How to Run

```bash
python -m examples.mcp_tools.browser_demo
```

The demo starts a web service with the default query: "Search for 'Wuhan weather', extract the weather overview data from the search results, and save it to `./local_file/weather.txt`."

## Code Walkthrough

### Configuration

```python
def load_config() -> Dict[str, Any]:
```

A helper function that loads and validates required environment variables. Raises a `ValueError` if any are missing, providing clear error messages. `Config.set_agent_llm_model("default_llm")` sets the global default LLM.

### System Prompts

Three detailed system prompts are defined:

1. **`MASTER_SYSTEM_PROMPT`**: Instructs the master agent on task delegation, context management, and result integration. Includes structured JSON format for delegating to sub-agents with task context, operation details, and error handling.

2. **`BROWSER_SYSTEM_PROMPT`**: Instructs the browser agent on web operations, capability assessment, login page detection and automatic handling (using environment variable credentials), and content extraction.

3. **`FILE_SYSTEM_PROMPT`**: Instructs the file agent on file operations, input validation, data processing, and proper error handling.

### BrowserDemo Class

The `BrowserDemo` class encapsulates the entire demo setup:

- **`__init__`**: Loads config and creates the oxy space.
- **`_create_oxy_space`**: Assembles all components.
- **`_create_http_llm`**: Configures the `HttpLLM` with detailed parameters (temperature 0.01, semaphore 4, retries 3, timeout 60s).
- **`_create_browser_tools`**: Creates an `StdioMCPClient` for the browser MCP server at `./mcp_servers/browser/server.py`.
- **`_create_filesystem_tools`**: Creates an `StdioMCPClient` for the `@modelcontextprotocol/server-filesystem` package.
- **`_create_browser_agent`**: A `ReActAgent` with browser tools and the browser-specific prompt.
- **`_create_file_agent`**: A `ReActAgent` with filesystem tools and the file-specific prompt.
- **`_create_master_agent`**: A `ReActAgent` marked `is_master=True` with sub-agents `browser_agent` and `file_agent`.

### Components (`oxy_space`)

| Component | Type | Role |
|---|---|---|
| `default_llm` | `HttpLLM` | Shared LLM (temperature 0.01, semaphore 4, retries 3) |
| `browser_tools` | `StdioMCPClient` | Custom browser MCP server for web automation |
| `file_tools` | `StdioMCPClient` | Filesystem MCP server for file operations |
| `browser_agent` | `ReActAgent` | Handles web navigation, scraping, and data extraction |
| `file_agent` | `ReActAgent` | Handles file read/write operations |
| `master_agent` | `ReActAgent` | Coordinates browser and file agents; `is_master=True` |

### Entry Point

```python
async def main():
    demo = BrowserDemo()
    await demo.run_demo()
```

The `run_demo` method creates a `MAS` context and starts the web service.

## Key Concepts

- **Multi-Agent Coordination**: A master agent decomposes tasks and delegates to specialized sub-agents. The master tracks progress, passes context, and integrates results.
- **StdioMCPClient**: Connects to MCP tool servers via standard I/O. Two instances are used here -- one for a custom browser server and one for the official filesystem server.
- **Detailed System Prompts**: Each agent receives role-specific instructions with structured output formats, error handling guidelines, and capability boundaries.
- **Class-Based Demo Pattern**: Encapsulating the demo in a class with factory methods for each component provides clean separation and error handling.
- **Automatic Login Handling**: The browser agent's prompt includes instructions for detecting login pages and using environment-variable credentials automatically, without prompting the user.

## Expected Behavior

1. The web UI opens with a query to search for weather information.
2. The `master_agent` breaks this into two sub-tasks: search the web and save results to a file.
3. The `browser_agent` uses browser tools to navigate to a search engine, find weather data, and extract relevant information.
4. The `master_agent` passes the extracted data to the `file_agent`.
5. The `file_agent` writes the data to `./local_file/weather.txt`.
6. A final summary is returned to the user.
