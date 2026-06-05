# MAS-Level Hooks: Filter and Interceptor

**Source:** `examples/backend/demo_mas_hook.py`

## Overview

This example demonstrates MAS-level request hooks: `func_filter` for modifying incoming payloads and `func_interceptor` for blocking requests entirely. These hooks run before the request reaches any agent, making them ideal for authentication, authorization, request enrichment, and rate limiting at the gateway level.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`

## How to Run

```bash
python -m examples.backend.demo_mas_hook
```

## Code Walkthrough

### Configuration

```python
Config.set_agent_llm_model("default_llm")
```

Sets the default LLM model name for all agents globally, so individual agents do not need to specify `llm_model`.

### Hook Functions

**Filter function:**
```python
def func_filter(payload):
    print(payload)
    payload["group_data"] = {"user_pin": "123456"}
    return payload
```

The filter function receives the raw incoming payload, prints it for debugging, injects `group_data` with a `user_pin` field, and returns the modified payload. This demonstrates request enrichment -- for example, extracting user identity from a session token and attaching it to the request.

**Interceptor function:**
```python
def func_interceptor(payload):
    print(payload)
    return {"code": 403, "message": "Permission denied."}
```

The interceptor function also receives the payload, but instead of modifying it, returns an error response dictionary. When an interceptor returns a non-`None` value, the request is short-circuited and the returned value is sent back to the client as the response. This demonstrates request blocking for unauthorized access.

**Note:** In this example both hooks are registered simultaneously, meaning the interceptor will block all requests. In practice, you would use conditional logic inside the interceptor (e.g., check authentication tokens) to decide whether to block or allow the request.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | Standard LLM credentials |
| `master_agent` | `ChatAgent` | Uses the globally configured `default_llm` |

### Entry Point

```python
async with MAS(
    oxy_space=oxy_space,
    func_filter=func_filter,
    func_interceptor=func_interceptor,
) as mas:
    await mas.start_web_service(first_query="hello")
```

Both hooks are passed as parameters to the `MAS` constructor.

## Key Concepts

- **func_filter**: A MAS-level hook that modifies the incoming payload before it is processed. It receives and returns the payload dictionary. Use it for request enrichment (adding metadata, normalizing fields). Supports both sync and async functions.
- **func_interceptor**: A MAS-level hook that can short-circuit request processing. If it returns a non-`None` value, that value is returned to the client immediately and the request does not reach any agent. Use it for authentication and authorization. Supports both sync and async functions.
- **Hook execution order**: The interceptor runs before the filter. If the interceptor blocks the request, the filter is not executed.
- **Config.set_agent_llm_model**: Sets a default LLM model name for all agents, reducing boilerplate when all agents share the same model.

> All `func_*` hooks in OxyGent support both sync and async functions. Sync functions are automatically wrapped as async at initialization time.

## Expected Behavior

1. The web service starts on `127.0.0.1:8080`.
2. When a request arrives, the interceptor prints the payload and returns a `403 Permission denied` response.
3. The request never reaches the agent; the client receives the error response directly.
4. To see the filter in action, remove or conditionally bypass the interceptor.
