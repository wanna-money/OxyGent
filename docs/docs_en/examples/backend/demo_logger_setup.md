# Setting Up Custom Logging

**Source:** `examples/backend/demo_logger_setup.py`

## Overview

This example demonstrates how to configure custom logging in OxyGent using the `setup_logging` utility. It shows how to obtain a logger instance and use it inside agent hook functions for debugging and monitoring request processing. This is useful for production deployments where you need structured logging with consistent formatting.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`

## How to Run

```bash
python -m examples.backend.demo_logger_setup
```

## Code Walkthrough

### Configuration

```python
from oxygent.log_setup import setup_logging
logger = setup_logging()
```

The `setup_logging()` function initializes and returns a configured logger instance. This logger uses the OxyGent logging configuration (format, level, handlers).

### Hook Functions

```python
def update_query(oxy_request: OxyRequest) -> OxyRequest:
    query = oxy_request.get_query()
    logger.info(f"The current query is: {query}")
    return oxy_request
```

The `update_query` function is a `func_process_input` hook that logs the incoming query at the INFO level before the agent processes it. This enables request tracing in the application logs.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | Standard LLM credentials from environment |
| `master_agent` | `ChatAgent` | `func_process_input=update_query` -- logs each incoming query |

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="hello")
```

## Key Concepts

- **setup_logging**: A utility from `oxygent.log_setup` that initializes the OxyGent logging system and returns a logger you can use in custom code.
- **Logging in hooks**: Hook functions like `func_process_input` are ideal places to add logging, as they execute at well-defined points in the request lifecycle.
- **OxyRequest.get_query()**: Retrieves the current query string from the request, useful for logging and debugging.

## Expected Behavior

1. The logger is initialized at module load time.
2. When the web service starts and processes the initial query `"hello"`, the hook logs: `The current query is: hello`.
3. Each subsequent query entered through the web UI is also logged at the INFO level.
4. The log output uses the format and handlers configured by `setup_logging()`.
