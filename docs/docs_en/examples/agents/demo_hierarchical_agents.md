# Hierarchical Multi-Agent System

**Source:** `examples/agents/demo_hierarchical_agents.py`

## Overview

This example demonstrates a hierarchical multi-agent architecture where a master `ReActAgent` delegates tasks to specialized sub-agents, each with their own MCP tools. The master agent coordinates a `time_agent` and a `file_agent`, enabling complex workflows that span multiple tool domains (e.g., get the current time and save it to a file). This pattern is essential for building systems where tasks require chaining multiple specialized capabilities.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`
- `uvx` installed (for `mcp-server-time`)
- `npx` / Node.js installed (for `@modelcontextprotocol/server-filesystem`)
- A `./local_file` directory should exist (used as the filesystem sandbox for the file MCP server)

## How to Run

```bash
python -m examples.agents.demo_hierarchical_agents
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars |
| `time_tools` | `StdioMCPClient` | `params.command="uvx"`, `params.args=["mcp-server-time", "--local-timezone=Asia/Shanghai"]` |
| `file_tools` | `StdioMCPClient` | `params.command="npx"`, `params.args=["-y", "@modelcontextprotocol/server-filesystem", "./local_file"]` |
| `master_agent` | `ReActAgent` | `is_master=True`; `sub_agents=["time_agent", "file_agent"]`; `llm_model="default_llm"` |
| `time_agent` | `ReActAgent` | `desc="A tool for time query"`; `tools=["time_tools"]`; `llm_model="default_llm"` |
| `file_agent` | `ReActAgent` | `desc="A tool for file operation."`; `tools=["file_tools"]`; `llm_model="default_llm"` |

### Entry Point

```python
await mas.start_web_service(
    first_query="Get what time it is and save in `log.txt` under `/local_file`",
)
```

Launches the web service with a compound query that requires both time retrieval and file writing.

## Key Concepts

- **Hierarchical delegation** -- the master agent does not directly use any tools; instead, it decomposes the task and delegates to specialized sub-agents, each with their own tool sets.
- **`is_master=True`** -- explicitly marks the master agent. The `MAS` runtime routes all incoming queries to this agent.
- **Homogeneous sub-agent types** -- unlike the heterogeneous example, here all agents (master and sub-agents) are `ReActAgent` instances, but they differ in their assigned tools and descriptions.
- **MCP tool isolation** -- each sub-agent only has access to its designated MCP tools, enforcing separation of concerns.
- **Multi-step compound tasks** -- the initial query requires the master to first invoke the `time_agent`, then pass the result to `file_agent`, demonstrating sequential multi-agent coordination.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The compound query is sent: "Get what time it is and save in `log.txt` under `/local_file`".
3. The master agent decomposes the task:
   - First, it calls `time_agent` to get the current time.
   - Then, it calls `file_agent` to write the time into `log.txt` under the `./local_file` directory.
4. The `time_agent` uses the `mcp-server-time` tools to retrieve the current time (Asia/Shanghai timezone).
5. The `file_agent` uses the `@modelcontextprotocol/server-filesystem` tools to create/write the file.
6. The final result confirms both operations completed, and the file `./local_file/log.txt` contains the current time.
