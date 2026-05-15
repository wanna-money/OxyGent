# Plan-and-Solve Demo

**Source:** `examples/flows/plan_and_solve_demo.py`

## Overview

This example demonstrates the **Plan-and-Solve** flow pattern in OxyGent. A planner agent decomposes a complex user request into a step-by-step plan, and an executor agent carries out each step using a rich set of sub-agents and tools -- including time queries, file operations, math computations, and joke telling. The demo also showcases a custom `WorkflowAgent` that mixes programmatic logic with agent calls.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- OxyGent package installed (`pip install -r requirements.txt`)
- Node.js (for the filesystem MCP tool via `npx`)
- `uvx` available on PATH (for the `mcp-server-time` package)
- `uv` available on PATH (for running the custom math MCP server)
- A `config.json` file in the working directory (loaded at startup)
- A `./local_file` directory (used by the filesystem tool)
- A `./mcp_servers` directory containing `math_tools.py`

## How to Run

```bash
python -m examples.flows.plan_and_solve_demo
```

The demo starts a web service with several predefined queries. By default it sends the first query: "What time is it now? Please save it to the file log.txt under the local_file folder."

## Code Walkthrough

### Configuration

```python
Config.load_from_json("./config.json", env="default")
```

Loads configuration from `config.json` using the "default" environment layer. This overrides defaults for LLM, server, and other settings.

### Custom Workflow Function

```python
async def workflow(oxy_request: OxyRequest):
```

A custom workflow function assigned to the `math_agent` `WorkflowAgent`. It:

1. Retrieves short memory (conversation history) at both the agent level and master level.
2. Sends an intermediate message via `oxy_request.send_message("msg")`.
3. Calls `time_agent` to get the current time.
4. Parses the user query for numbers; if found, calls the `pi` math tool to compute pi to that many decimal places.
5. Returns a formatted string with the result.

### Custom FunctionHub Tool

```python
fh = oxy.FunctionHub(name="joke_tools")

@fh.tool(description="A tool that is good at telling jokes")
async def joke_tool(joke_type: str = Field(description="Type of joke")):
```

Defines a `FunctionHub` with a single tool `joke_tool` that returns a random joke from a hardcoded list. This demonstrates how to create custom Python function tools.

### Components (`oxy_space`)

| Component | Type | Role |
|---|---|---|
| `default_llm` | `HttpLLM` | Shared language model |
| `intent_agent` | `ChatAgent` | Intent classification agent (uses `INTENTION_PROMPT`) |
| `joke_tools` (fh) | `FunctionHub` | Custom joke-telling function tool |
| `time_tools` | `StdioMCPClient` | MCP client for time queries (Asia/Shanghai) |
| `file_tools` | `StdioMCPClient` | MCP client for filesystem operations on `./local_file` |
| `math_tools` | `StdioMCPClient` | MCP client for math computations (custom server) |
| `planner_agent` | `ChatAgent` | Creates step-by-step plans from user goals |
| `executor_agent` | `ReActAgent` | Executes individual plan steps using sub-agents and tools |
| `master_agent` | `PlanAndSolve` | Orchestrates planning and execution; marked as `is_master=True` |
| `time_agent` / `time_agent_b` / `time_agent_c` | `ReActAgent` | Agents wrapping the time MCP tool (3 instances) |
| `file_agent` | `ReActAgent` | Agent wrapping the filesystem MCP tool |
| `math_agent` | `WorkflowAgent` | Agent with custom workflow function for math/pi queries |

### Plan-and-Solve Configuration

The `master_agent` (`PlanAndSolve`) is configured with:
- `planner_agent_name="planner_agent"` -- the agent that creates the plan.
- `executor_agent_name="executor_agent"` -- the agent that executes each step.
- `enable_replanner=False` -- disables re-planning after step failures.
- `is_discard_react_memory=True` -- clears ReAct memory between steps to prevent context pollution.

### Entry Point

```python
async def main():
    mas = await MAS.create(oxy_space=oxy_space)
    queries = [...]
    await mas.start_web_service(first_query=queries[0])
```

Uses `MAS.create()` (alternative to async context manager) and starts the web service with the first of several predefined queries.

## Key Concepts

- **Plan-and-Solve**: A two-phase approach where a planner decomposes a complex task into atomic steps, and an executor carries out each step sequentially. This is effective for multi-step tasks that require different tools.
- **WorkflowAgent**: An agent whose execution logic is a custom Python function (`func_workflow`), giving full programmatic control while still participating in the agent hierarchy.
- **FunctionHub**: A decorator-based system for wrapping plain Python functions as Oxy tools callable by agents.
- **StdioMCPClient**: Connects to MCP (Model Context Protocol) tool servers via standard I/O, enabling access to time, filesystem, and math tools.
- **`is_retain_master_short_memory`**: When `True` on the `math_agent`, the agent retains the master-level conversation history, allowing it to reference earlier exchanges.
- **`is_discard_react_memory`**: When `True`, clears the executor's ReAct memory between plan steps to prevent cross-step context leakage.

## Expected Behavior

1. The web UI opens and sends the first query (save current time to a file).
2. The `planner_agent` breaks the query into steps (e.g., "get the current time" then "save to log.txt").
3. The `executor_agent` executes each step by delegating to the appropriate sub-agent (`time_agent` for time, `file_agent` for file I/O).
4. The final result is aggregated and displayed in the web UI.
5. Additional queries (food review, Hive SQL) can be sent interactively to test the system's versatility.
