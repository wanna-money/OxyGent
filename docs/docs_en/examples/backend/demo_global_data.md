# Using Global Data as a Persistent MAS-Level Store

**Source:** `examples/backend/demo_global_data.py`

## Overview

This example demonstrates how to use `global_data` as a persistent, MAS-level key-value store that survives across multiple requests. It implements a custom `CounterAgent` that increments a counter in `global_data` on each invocation, showing how agents can read and write shared state. This pattern is useful for maintaining cross-request state such as counters, caches, or configuration that all agents need to access.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`

## How to Run

```bash
python -m examples.backend.demo_global_data
```

## Code Walkthrough

### Custom Agent: CounterAgent

```python
class CounterAgent(BaseAgent):
    async def execute(self, oxy_request: OxyRequest):
        cnt = oxy_request.get_global_data("counter", 0) + 1
        oxy_request.set_global_data("counter", cnt)

        return OxyResponse(
            state=OxyState.COMPLETED,
            output=f"This MAS has been called {cnt} time(s).",
            oxy_request=oxy_request,
        )
```

`CounterAgent` extends `BaseAgent` and overrides the `execute` method. On each call it:
1. Reads the current counter from `global_data` (defaulting to 0).
2. Increments the counter and writes it back.
3. Returns an `OxyResponse` with the current count.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | Standard LLM credentials (included but not directly used by the counter agent) |
| `master_agent` | `CounterAgent` | `is_master=True` -- marks it as the entry point for `chat_with_agent` |

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    r1 = await mas.chat_with_agent({"query": "first"})
    print(r1.output)  # "This MAS has been called 1 time(s)."

    r2 = await mas.chat_with_agent({"query": "second"})
    print(r2.output)  # "This MAS has been called 2 time(s)."

    print("Current global_data:", mas.global_data)
```

## Key Concepts

- **global_data persistence**: Unlike `shared_data` (per-request), `global_data` persists for the entire lifetime of the MAS instance and is shared across all requests.
- **Custom agent via BaseAgent**: You can create custom agents by extending `BaseAgent` and implementing the `execute` method. This gives full control over the agent's logic without relying on LLM-driven reasoning.
- **OxyResponse**: The standard response object returned by agents. It includes a `state` (e.g., `OxyState.COMPLETED`), an `output` string, and the `oxy_request` for traceability.
- **Reading global_data from MAS**: The `mas.global_data` attribute can be inspected directly to see the current state of the global store.

## Expected Behavior

1. First call: The counter is initialized to 1 and the output reads `"This MAS has been called 1 time(s)."`.
2. Second call: The counter increments to 2 and the output reads `"This MAS has been called 2 time(s)."`.
3. The `mas.global_data` dictionary shows `{"counter": 2}` after both calls complete.
