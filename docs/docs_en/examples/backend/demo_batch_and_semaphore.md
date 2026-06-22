# Batch Processing with Concurrency Control

**Source:** `examples/backend/demo_batch_and_semaphore.py`

## Overview

This example demonstrates how to run batch queries through a MAS with concurrency limits (semaphores) on both the LLM and the agent. This pattern is essential for production workloads where you need to process many requests concurrently while respecting rate limits or resource constraints.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`

## How to Run

```bash
python -m examples.backend.demo_batch_and_semaphore
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `semaphore=4` -- limits LLM concurrency to 4 simultaneous requests |
| `chat_agent` | `ChatAgent` | `semaphore=6` -- limits agent concurrency to 6 simultaneous executions |

The semaphore values define the maximum number of concurrent executions allowed for each component. In this configuration, even though the agent allows 6 concurrent calls, each call that invokes the LLM will be further throttled by the LLM's semaphore of 4.

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    outs = await mas.start_batch_processing(["hello"] * 10, return_trace_id=True)
    [print(out) for out in outs]
```

- `start_batch_processing` accepts a list of query strings and processes them concurrently.
- `return_trace_id=True` causes each result to include the trace ID for debugging and tracking purposes.
- The example sends 10 identical `"hello"` queries.

## Key Concepts

- **Semaphore**: An integer parameter on any Oxy component that limits how many concurrent `_execute()` calls can run at once. This maps to a Python `asyncio.Semaphore`.
- **Batch processing**: `MAS.start_batch_processing()` dispatches multiple queries concurrently to the master agent and collects all results.
- **Layered concurrency control**: Semaphores can be set independently on agents and LLMs. The effective concurrency is the minimum of all semaphores in the call chain.

## Expected Behavior

1. The MAS dispatches 10 `"hello"` queries concurrently.
2. At most 6 agent executions run simultaneously (agent semaphore).
3. At most 4 LLM calls run simultaneously (LLM semaphore).
4. All 10 results (each with a trace ID) are printed to the console once processing completes.
