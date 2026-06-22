# Bank ReAct Agent -- Autonomy via MCP

**Source:** `examples/banks/demo_bank_react_agent_autonomy_by_mcp.py`

## Overview

This example is a variant of the autonomy-mode bank agent that uses **SSEMCPClient** instead of `BankClient` to connect to the remote tool bank. The bank tools are exposed as MCP tools over SSE (Server-Sent Events), and the agent treats them identically to any other MCP tool. This demonstrates OxyGent's ability to consume bank tools through the MCP protocol rather than the native BankClient interface.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- OxyGent package installed (`pip install -r requirements.txt`)
- A **bank server running as an MCP SSE endpoint** at `http://127.0.0.1:8000/sse` (note: different port and protocol from the BankClient examples)
- `uvx` available on PATH (for `mcp-server-time`)

## How to Run

1. Start the bank server with MCP SSE support on port 8000.
2. Run:

```bash
python -m examples.banks.demo_bank_react_agent_autonomy_by_mcp
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Role |
|---|---|---|
| `default_llm` | `HttpLLM` | Language model with temperature 0.01, semaphore 4 |
| `time_tools` | `StdioMCPClient` | MCP time query tool (Asia/Shanghai timezone) |
| `qa_agent` | `ReActAgent` | Q&A agent with autonomous tool use |
| `remote_user_profile_banks` | `SSEMCPClient` | MCP client connecting to bank server via SSE at `http://127.0.0.1:8000/sse` |

### Key Difference: SSEMCPClient vs BankClient

In this example, the bank tools are accessed via `SSEMCPClient` instead of `BankClient`:

```python
oxy.SSEMCPClient(
    name="remote_user_profile_banks",
    sse_url="http://127.0.0.1:8000/sse",
)
```

The bank tools are registered in the agent's `tools` list (not `banks`):

```python
oxy.ReActAgent(
    name="qa_agent",
    tools=["time_tools", "remote_user_profile_banks"],
    ...
)
```

This means the agent sees bank tools as regular MCP tools, making them indistinguishable from other tool sources.

### Request Filter

```python
def func_filter(payload):
    payload["group_data"] = {"user_pin": "002"}
    return payload
```

Same user-scoping filter as other bank examples.

### Entry Point

```python
async def main():
    async with MAS(oxy_space=oxy_space, func_filter=func_filter) as mas:
        await mas.start_web_service(first_query="Who I am")
```

## Key Concepts

- **SSEMCPClient**: An MCP client that communicates with a tool server over Server-Sent Events (SSE). This is an alternative to `StdioMCPClient` (which uses standard I/O) and is suitable for remote servers.
- **MCP as a Universal Tool Protocol**: By exposing bank tools as MCP endpoints, the agent can consume them through the same interface used for any MCP tool, demonstrating protocol-level interoperability.
- **Tools vs Banks**: In this example, the MCP client is listed in `tools` rather than `banks`. The agent treats the bank's tools as standard MCP tools, giving it the same autonomous decision-making over their use.

## Expected Behavior

1. The web UI opens with the query "Who I am".
2. The `qa_agent` uses ReAct reasoning and sees both time tools and user-profile tools in its tool list.
3. It autonomously decides to call the user-profile retrieval tool via MCP SSE.
4. The agent returns a response based on the retrieved profile for user `002`.
