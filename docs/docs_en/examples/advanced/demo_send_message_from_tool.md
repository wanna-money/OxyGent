# Send Message from Tool (with Task Interruption)

**Source:** `examples/advanced/demo_send_message_from_tool.py`

## Overview

This example demonstrates how a tool function can send messages directly to the user (via SSE/web UI) and interrupt the agent's task mid-execution. This is useful when a tool produces a result that should be immediately surfaced to the user without waiting for the agent's full reasoning cycle to complete.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`

## How to Run

```bash
python -m examples.advanced.demo_send_message_from_tool
```

## Code Walkthrough

### FunctionHub and Tool Definition

```python
fh_math_tools = oxy.FunctionHub(name="math_tools")

@fh_math_tools.tool(description="A tool that can calculate the value of pi.")
async def calc_pi(
    prec: int = Field(description="how many decimal places"),
    oxy_request: OxyRequest = Field(description="The oxy request"),
) -> float:
```

A `FunctionHub` named `math_tools` is created, and a `calc_pi` tool is registered on it. The tool:

1. Accepts `prec` (precision / number of decimal places) and `oxy_request` (injected by the framework).
2. Calculates Pi using the Ramanujan series with Python's `Decimal` for arbitrary precision.
3. **Sends a message directly to the frontend:** `await oxy_request.send_message({"type": "answer", "content": result})` -- this pushes the result to the web UI immediately via SSE.
4. **Interrupts the agent's task:** `await oxy_request.break_task()` -- this stops the agent from continuing its ReAct loop after this tool returns.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from environment |
| `math_tools` | `FunctionHub` | Contains the `calc_pi` tool |
| `master_agent` | `ReActAgent` | `tools=["math_tools"]`, `llm_model="default_llm"` |

### Entry Point

`main()` creates a `MAS` context and starts the web service with `first_query="Please calculate the 20 positions of Pi"`.

## Key Concepts

- **oxy_request.send_message()** -- Sends a message payload directly to the frontend (web UI via SSE). The message dict can contain `type` and `content` fields. This allows tools to communicate results to the user in real-time.
- **oxy_request.break_task()** -- Interrupts the current agent task, preventing further ReAct iterations. After this call, the agent's execution stops and the tool's message becomes the final output.
- **FunctionHub** -- A container for registering Python functions as tools via the `@fh.tool()` decorator. Functions can use Pydantic `Field` annotations for parameter descriptions.
- **OxyRequest Injection** -- By including `oxy_request: OxyRequest` as a parameter, the framework automatically injects the current request context into the tool function.

## Expected Behavior

1. The web service starts on `127.0.0.1:8080`.
2. The master agent receives the Pi query and calls the `calc_pi` tool with `prec=20`.
3. The tool calculates Pi, sends the result directly to the web UI, and interrupts the task.
4. The user sees the Pi value in the web UI immediately, without the agent producing a separate final answer.
