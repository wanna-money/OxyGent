# Custom Agent Input Schema

**Source:** `examples/advanced/demo_custom_agent_input_schema.py`

## Overview

This example demonstrates how to define a custom input schema for a WorkflowAgent so that the master agent knows exactly which arguments to pass when calling it. This pattern is useful when you need a sub-agent (or tool-like agent) to accept structured, validated inputs beyond a simple query string.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`

## How to Run

```bash
python -m examples.advanced.demo_custom_agent_input_schema
```

## Code Walkthrough

### Workflow Function

```python
async def workflow(oxy_request: OxyRequest):
```

A custom async function that receives an `OxyRequest`. It extracts two arguments:

- `query` -- the user's question (printed to stdout).
- `precision` -- how many digits of Pi to return.

The function stores a hardcoded 80-digit Pi string and returns a slice of it truncated to the requested precision.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from environment |
| `master_agent` | `ReActAgent` | `is_master=True`, `sub_agents=["math_agent"]` |
| `math_agent` | `WorkflowAgent` | `desc="A tool for pi query"`, `input_schema={...}`, `func_workflow=workflow` |

The `input_schema` on `math_agent` is a JSON Schema-style dict with two properties:

- `query` (required) -- description: "Query question"
- `precision` (required) -- description: "How many decimal places are there"

This schema is exposed to the master agent's LLM so it can generate the correct structured call.

### Entry Point

`main()` creates a `MAS` context with the oxy_space and starts the web service with `first_query="Please calculate the 20 positions of Pi"`. The master agent receives this query, recognizes that `math_agent` can answer it, and calls it with the appropriate `query` and `precision` arguments.

## Key Concepts

- **input_schema** -- A dict conforming to JSON Schema that declares the expected arguments for a WorkflowAgent. The master agent's LLM uses this schema to generate correctly structured tool calls.
- **WorkflowAgent** -- An agent type that wraps a plain Python async function (`func_workflow`) and exposes it as a callable sub-agent to other agents in the system.
- **OxyRequest.get_arguments()** -- Retrieves a named argument from the request payload that was passed by the calling agent.

## Expected Behavior

1. The web service starts on `127.0.0.1:8080`.
2. The master agent receives the Pi query, identifies `math_agent` as the right sub-agent, and calls it with `query` and `precision` arguments.
3. `math_agent` executes the workflow function and returns the first 20 digits of Pi.
4. The master agent relays the result back to the user through the web UI.
