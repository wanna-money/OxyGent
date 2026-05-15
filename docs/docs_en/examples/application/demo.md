# Multi-Agent Application with Custom Workflow, MCP Tools, and Hooks

**Source:** `examples/application/demo.py`

## Overview

This is a comprehensive example that demonstrates many core OxyGent features in a single application: MCP tool clients (time, filesystem, math), a custom `FunctionHub` tool, a `WorkflowAgent` with a programmatic workflow function, input/output hook functions, and a master `ReActAgent` coordinating multiple sub-agents. It showcases how to build a real-world multi-agent system with tool calling, inter-agent communication, and message formatting.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`
- Node.js and `npx` (for the filesystem MCP server)
- `uvx` (for the time MCP server: `mcp-server-time`)
- `uv` (for the math MCP server from `./mcp_servers/math_tools.py`)
- A `./local_file` directory for the filesystem MCP tool to operate on

## How to Run

```bash
python -m examples.application.demo
```

## Code Walkthrough

### Configuration

```python
Config.set_agent_llm_model("default_llm")
```

Sets the global default LLM model name.

### Custom FunctionHub Tool

```python
fh = oxy.FunctionHub(name="joke_tools")

@fh.tool(description="a tool for telling jokes")
async def joke_tool(joke_type: str = Field(description="The type of the jokes")):
    ...
```

Defines a simple joke-telling tool that returns a random joke from a hardcoded list. Demonstrates how to register an async function with typed, described parameters using `pydantic.Field`.

### Hook Functions

#### `update_query(oxy_request: OxyRequest) -> OxyRequest`

A **pre-processing input hook** (`func_process_input`) attached to `time_agent`. Before the agent executes, this function:

1. Logs the shared data and user queries (both master-level and current-level).
2. Injects the callee name into the request arguments (`oxy_request.arguments["who"]`).
3. Returns the modified request.

#### `format_output(oxy_response: OxyResponse) -> OxyResponse`

A **post-processing output hook** (`func_format_output`) attached to `master_agent`. After the master agent produces a response, this function prefixes the output with `"Answer: "`.

### Workflow Function

```python
async def workflow(oxy_request: OxyRequest):
```

A custom workflow function attached to `math_agent` via `func_workflow`. This is the core of the `WorkflowAgent` -- instead of using the ReAct loop, the agent executes this function directly. The workflow:

1. **Retrieves conversation history** -- `get_short_memory()` for agent-level history and `get_short_memory(master_level=True)` for user-level history.
2. **Sends a custom SSE message** -- `send_message()` pushes a message to the frontend.
3. **Calls another agent** -- `oxy_request.call(callee="time_agent", ...)` demonstrates inter-agent communication.
4. **Calls an LLM directly** -- `oxy_request.call(callee="default_llm", ...)` sends raw messages to the LLM with custom parameters.
5. **Conditional tool call** -- Extracts numbers from the user query. If found, calls the `calc_pi` tool (from `math_tools`) to compute pi to that many decimal places. Otherwise, returns a default response.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `temperature=0.01`, `semaphore=4` |
| `intent_agent` | `ChatAgent` | Uses `INTENTION_PROMPT` for intent classification |
| `joke_tools` | `FunctionHub` | Custom joke-telling tool |
| `time_tools` | `StdioMCPClient` | `mcp-server-time` with `Asia/Shanghai` timezone |
| `file_tools` | `StdioMCPClient` | `@modelcontextprotocol/server-filesystem` on `./local_file` |
| `math_tools` | `StdioMCPClient` | Local `./mcp_servers/math_tools.py` via `uv run` |
| `master_agent` | `ReActAgent` | `is_master=True`, `sub_agents=[time, file, math]`, `func_format_output`, `timeout=100` |
| `time_agent` | `ReActAgent` | `tools=["time_tools"]`, `func_process_input=update_query`, `trust_mode=False`, `timeout=10` |
| `file_agent` | `ReActAgent` | `tools=["file_tools"]` |
| `math_agent` | `WorkflowAgent` | `func_workflow=workflow`, `sub_agents=["time_agent"]`, `tools=["math_tools"]`, `is_retain_master_short_memory=True` |

### Entry Point

```python
await mas.start_web_service(
    first_query="Please calculate the 20 positions of Pi",
    welcome_message="Hi, I'm OxyGent. How can I assist you?",
)
```

Starts the web service with a custom welcome message and an initial query that triggers the math agent's workflow.

## Key Concepts

- **WorkflowAgent** -- An agent type that executes a user-defined `func_workflow` function instead of the standard ReAct reasoning loop. This gives full programmatic control over the agent's behavior.
- **`oxy_request.call()`** -- The core inter-agent communication primitive. Agents and tools can call each other by name, passing arguments and receiving `OxyResponse` objects.
- **`oxy_request.send_message()`** -- Pushes custom messages to the frontend via SSE (Server-Sent Events) during agent execution.
- **`func_process_input` / `func_format_output`** -- Hook functions that transform the request before execution and the response after execution, respectively.
- **`trust_mode=False`** -- When disabled on `time_agent`, the agent asks for user confirmation before executing tool calls.
- **`is_retain_master_short_memory=True`** -- The `math_agent` retains conversation history from the master (user) level, giving the workflow access to the full conversation context.
- **StdioMCPClient** -- Connects to an MCP server via standard I/O (stdin/stdout). Each MCP client wraps an external tool server as an OxyGent tool.
- **`semaphore`** -- The LLM has `semaphore=4`, allowing up to 4 concurrent LLM requests.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080` with the welcome message "Hi, I'm OxyGent. How can I assist you?".
2. The first query "Please calculate the 20 positions of Pi" is sent automatically.
3. The master agent routes this to `math_agent`.
4. The `math_agent` workflow executes:
   - Logs conversation history.
   - Sends a custom SSE message to the frontend.
   - Calls `time_agent` to get the current time in Asia/Shanghai.
   - Calls `default_llm` directly with a simple greeting.
   - Extracts the number "20" from the query and calls `calc_pi` to compute pi to 20 decimal places.
5. The result is formatted by `format_output` (prefixed with "Answer: ") and displayed in the web UI.
