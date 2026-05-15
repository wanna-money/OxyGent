# Extending Oxy Components by Subclassing

**Source:** `examples/backend/demo_rewrite_oxy.py`

## Overview

This example demonstrates how to extend OxyGent's built-in components by subclassing. It creates a custom `MyHttpLLM` class that overrides the `_execute` method of `HttpLLM` to implement a fully custom HTTP request to an LLM API. This pattern is useful when you need to customize the LLM request format, add custom headers, handle non-standard API responses, or integrate with LLM providers that have unique API conventions.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python package: `httpx`

## How to Run

```bash
python -m examples.backend.demo_rewrite_oxy
```

## Code Walkthrough

### Custom Component: MyHttpLLM

```python
class MyHttpLLM(oxy.HttpLLM):
    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        headers = {"Content-Type": "application/json"}
        headers.update(self.headers(oxy_request))

        payload = {
            "messages": await self._get_messages(oxy_request),
            "model": self.model_name,
        }
        for k, v in self.llm_params.items():
            payload[k] = v
        for k, v in oxy_request.arguments.items():
            if k == "messages":
                continue
            payload[k] = v

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            http_response = await client.post(
                self.base_url, headers=headers, json=payload
            )
            http_response.raise_for_status()
            data = http_response.json()
            response_message = data["choices"][0]["message"]
            result = response_message.get("content")
            return OxyResponse(state=OxyState.COMPLETED, output=result)
```

The custom class:
1. Builds headers using `Content-Type` plus any headers from the parent class's `headers()` method.
2. Constructs the payload with messages (from the Oxy lifecycle), model name, LLM params, and any extra arguments from the request.
3. Makes a raw HTTP POST request using `httpx`.
4. Parses the OpenAI-compatible response format and extracts the content.
5. Returns an `OxyResponse` with the result.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `MyHttpLLM` | Custom subclass of `HttpLLM` with overridden `_execute` |

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.call(
        callee="default_llm",
        arguments={
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "hello"},
            ],
            "llm_params": {"temperature": 0.2},
        },
    )
```

Instead of using `chat_with_agent`, this example calls the LLM directly via `mas.call()`, demonstrating that any Oxy component can be invoked by name.

## Key Concepts

- **Subclassing Oxy components**: Any Oxy component (`HttpLLM`, `BaseAgent`, `BaseTool`, etc.) can be extended by subclassing and overriding `_execute` (or `execute` for agents).
- **_execute vs execute**: `_execute` is the low-level method in the Oxy lifecycle that contains the core logic. It is wrapped by the Oxy lifecycle hooks (`_pre_process`, `_post_process`, retry logic, etc.).
- **mas.call()**: Directly invokes any registered Oxy component by name, bypassing the agent routing. Useful for testing or building custom orchestration logic.
- **OxyResponse construction**: When building custom components, you must return an `OxyResponse` with an appropriate `OxyState` and output.

## Expected Behavior

1. The MAS initializes with the custom `MyHttpLLM` component.
2. The `mas.call()` invocation sends a chat completion request to the configured LLM API.
3. The custom `_execute` method builds and sends the HTTP request, parses the response, and returns the LLM's reply.
4. The response is returned as an `OxyResponse` with `state=OxyState.COMPLETED`.
