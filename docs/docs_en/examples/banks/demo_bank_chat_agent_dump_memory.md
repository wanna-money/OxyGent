# Bank Chat Agent with Memory Dump

**Source:** `examples/banks/demo_bank_chat_agent_dump_memory.py`

## Overview

This example demonstrates how to use a **BankClient** to connect to a remote tool bank server, and how to implement a post-processing callback that asynchronously deposits conversation history (query-answer pairs) back into the bank after each response. The `ChatAgent` retrieves user-profile context from the bank before answering, and the `dump_memory` callback stores the interaction for future reference.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- OxyGent package installed (`pip install -r requirements.txt`)
- A **bank server** running at `http://127.0.0.1:8090` that exposes user-profile retrieval (`user_profile_retrieve`) and deposit (`user_profile_deposit`) tools

## How to Run

1. Start the bank server on port 8090 (see bank server examples in the repository).
2. Run this client:

```bash
python -m examples.banks.demo_bank_chat_agent_dump_memory
```

## Code Walkthrough

### Callback Function

```python
async def dump_memory(oxy_response: OxyResponse) -> OxyResponse:
```

A post-processing callback (`func_process_output`) that:

1. Extracts the original query and the agent's answer from the response.
2. Serializes them as a JSON object.
3. Calls the `user_profile_deposit` tool on the bank server asynchronously via `oxy_request.call_async()` with `is_send_message=False` (fire-and-forget, no SSE message sent to the user).
4. Returns the original `OxyResponse` unchanged.

### Components (`oxy_space`)

| Component | Type | Role |
|---|---|---|
| `default_llm` | `HttpLLM` | Language model with temperature 0.01, semaphore 4 |
| `qa_agent` | `ChatAgent` | Main Q&A agent; uses bank tools and preceding context |
| `remote_user_profile_banks` | `BankClient` | Client connecting to the bank server at `http://127.0.0.1:8090` |

### Agent Configuration Details

The `qa_agent` is configured with several key parameters:

- **`banks=["remote_user_profile_banks"]`**: Registers the bank client so its tools become available.
- **`preceding_oxy=["user_profile_retrieve"]`**: Before the agent processes the query, it automatically calls `user_profile_retrieve` from the bank to fetch relevant context.
- **`preceding_placeholder="preceding_text"`**: The retrieval result is injected into the prompt at `${preceding_text}`.
- **`func_process_output=dump_memory`**: After each response, the `dump_memory` callback stores the Q&A pair.

### Request Filter

```python
def func_filter(payload):
    payload["group_data"] = {"user_pin": "002"}
    return payload
```

A filter function passed to `MAS` that injects `group_data` (user identifier `user_pin: "002"`) into every incoming request payload. This allows the bank server to scope data retrieval and storage to a specific user.

### Entry Point

```python
async def main():
    async with MAS(oxy_space=oxy_space, func_filter=func_filter, name="temp_app") as mas:
        await mas.start_web_service(first_query="Who I am")
```

Creates a named MAS instance (`temp_app`) with the filter function, and starts the web service. The initial query "Who I am" triggers user-profile retrieval from the bank.

## Key Concepts

- **BankClient**: A client component that connects to a remote tool bank (FastAPI-based server) and exposes its tools to agents. The bank server can host any number of tools (retrieval, deposit, search, etc.).
- **Preceding Oxy**: The `preceding_oxy` mechanism automatically invokes specified tools before the agent processes the user query. Results are injected into the prompt via placeholders, providing contextual information.
- **`func_process_output`**: A post-processing hook on the agent that receives the `OxyResponse` and can perform side effects (like memory storage) before the response is returned to the user.
- **`call_async` with `is_send_message=False`**: Fires an asynchronous tool call without blocking the response pipeline or sending progress messages to the frontend.
- **`func_filter`**: A global request filter on the MAS that can inject metadata (e.g., user identity) into all incoming requests.

## Expected Behavior

1. The web UI opens with the query "Who I am".
2. Before answering, `user_profile_retrieve` is called from the bank to fetch profile data for user `002`.
3. The retrieved profile data is injected into the agent's prompt as `${preceding_text}`.
4. The `qa_agent` answers based on the retrieved profile context.
5. After the response is generated, `dump_memory` asynchronously stores the query-answer pair back to the bank via `user_profile_deposit`.
6. On subsequent queries, the stored history enriches future retrievals.
