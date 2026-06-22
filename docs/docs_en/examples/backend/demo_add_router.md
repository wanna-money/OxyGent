# Adding Custom FastAPI Routes to MAS

**Source:** `examples/backend/demo_add_router.py`

## Overview

This example demonstrates how to extend the built-in MAS web service with custom FastAPI routes. By passing an `APIRouter` to the `MAS` constructor, you can expose additional HTTP endpoints alongside the default `/chat`, `/sse/chat`, and other MAS endpoints. This is useful when your agent system needs to serve supplementary APIs that agents or external clients can call.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages: `httpx`, `fastapi`

## How to Run

```bash
python -m examples.backend.demo_add_router
```

## Code Walkthrough

### Custom Router

A FastAPI `APIRouter` is created with a single endpoint:

```python
router = APIRouter()

@router.get("/api_name")
def api_name():
    return WebResponse(data={"key": "value"}).to_dict()
```

This defines a `GET /api_name` endpoint that returns a `WebResponse` containing `{"key": "value"}`.

### Workflow Function

The `workflow` function is an async callable that serves as the agent's execution logic. It uses `httpx.AsyncClient` to call the custom `/api_name` endpoint on the same server:

```python
async def workflow(oxy_request: OxyRequest):
    async with httpx.AsyncClient() as client:
        response = await client.get(url="http://127.0.0.1:8080/api_name")
        return response.json()
```

This demonstrates that agents can call custom API routes hosted by the same MAS web service.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | Standard LLM credentials from environment |
| `master_agent` | `WorkflowAgent` | Uses `func_workflow=workflow` to define its execution logic |

### Entry Point

The `MAS` is instantiated with the `routers=[router]` parameter, which registers the custom router with the FastAPI application:

```python
async with MAS(oxy_space=oxy_space, routers=[router]) as mas:
    await mas.start_web_service(first_query="hello")
```

## Key Concepts

- **Custom Routers**: The `MAS` constructor accepts a `routers` parameter (a list of `APIRouter` instances) to mount additional endpoints on the built-in FastAPI server.
- **WorkflowAgent**: An agent type whose logic is entirely defined by a user-supplied async function (`func_workflow`), bypassing LLM-driven reasoning.
- **Self-referencing API calls**: Agents running inside MAS can call the same MAS web service endpoints, enabling modular API-driven architectures.

## Expected Behavior

1. The MAS web service starts on `127.0.0.1:8080`.
2. The custom `/api_name` endpoint becomes available.
3. When the agent processes the initial query `"hello"`, the workflow function calls `GET /api_name` and returns the JSON response `{"key": "value"}`.
4. The web UI opens and displays the result.
