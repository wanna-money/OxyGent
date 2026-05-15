# Bank ReAct Agent -- Autonomy Mode

**Source:** `examples/banks/demo_bank_react_agent_autonomy.py`

## Overview

This example shows a **ReActAgent** that connects to a remote tool bank via `BankClient` and operates in **autonomy mode** -- the agent decides on its own when and how to call bank-provided tools based on the user's query. Unlike the "rigid" mode, the bank tools are registered in the agent's `banks` list (not `preceding_oxy`), giving the agent full control over tool invocation.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- OxyGent package installed (`pip install -r requirements.txt`)
- A **bank server** running at `http://127.0.0.1:8090` exposing user-profile tools

## How to Run

1. Start the bank server on port 8090.
2. Run:

```bash
python -m examples.banks.demo_bank_react_agent_autonomy
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Role |
|---|---|---|
| `default_llm` | `HttpLLM` | Language model with temperature 0.01, semaphore 4 |
| `time_tools` | `StdioMCPClient` | MCP time query tool (Asia/Shanghai timezone) |
| `qa_agent` | `ReActAgent` | Q&A agent with autonomous tool use |
| `remote_user_profile_banks` | `BankClient` | Client connecting to bank server at `http://127.0.0.1:8090` |

### Agent Configuration

The `qa_agent` is a `ReActAgent` with:
- **`tools=["time_tools"]`**: Direct MCP tools the agent can call.
- **`banks=["remote_user_profile_banks"]`**: Bank client whose tools become available to the agent. The agent autonomously decides whether to call bank tools based on the query.

This is the **autonomy** pattern: the agent sees all available tools (both direct tools and bank tools) in its tool descriptions and uses ReAct reasoning to decide which tools to invoke.

### Request Filter

```python
def func_filter(payload):
    payload["group_data"] = {"user_pin": "002"}
    return payload
```

Injects user identity (`user_pin: "002"`) into all requests for bank data scoping.

### Entry Point

```python
async def main():
    async with MAS(oxy_space=oxy_space, func_filter=func_filter) as mas:
        await mas.start_web_service(first_query="Who I am")
```

## Key Concepts

- **Autonomy Mode**: The agent has bank tools available and decides autonomously when to use them via ReAct reasoning, rather than having tools called automatically before the agent processes the query.
- **BankClient**: Connects to a remote FastAPI-based tool bank server, making its tools available as if they were local tools.
- **Mixed Tool Sources**: The agent combines tools from different sources -- `StdioMCPClient` for time queries and `BankClient` for user-profile operations -- demonstrating OxyGent's unified tool interface.

## Expected Behavior

1. The web UI opens with the query "Who I am".
2. The `qa_agent` uses ReAct reasoning to determine it needs user-profile information.
3. It autonomously calls the user-profile retrieval tool from the bank.
4. It may also use the time tool if relevant.
5. The agent synthesizes the retrieved information into a natural language response.
