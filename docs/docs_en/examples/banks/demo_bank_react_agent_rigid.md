# Bank ReAct Agent -- Rigid Mode

**Source:** `examples/banks/demo_bank_react_agent_rigid.py`

## Overview

This example demonstrates the **rigid** (deterministic) pattern for integrating bank tools with a `ReActAgent`. Instead of letting the agent autonomously decide when to call bank tools, the `preceding_oxy` mechanism automatically invokes the `user_profile_retrieve` tool before the agent processes every query. The retrieval result is injected into the agent's prompt, ensuring the agent always has user context available without relying on its own reasoning to fetch it.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- OxyGent package installed (`pip install -r requirements.txt`)
- A **bank server** running at `http://127.0.0.1:8090` exposing user-profile retrieval tools

## How to Run

1. Start the bank server on port 8090.
2. Run:

```bash
python -m examples.banks.demo_bank_react_agent_rigid
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Role |
|---|---|---|
| `default_llm` | `HttpLLM` | Language model with temperature 0.01, semaphore 4 |
| `qa_agent` | `ReActAgent` | Q&A agent with rigid preceding context injection |
| `remote_user_profile_banks` | `BankClient` | Client connecting to bank server at `http://127.0.0.1:8090` |

### Agent Configuration -- The Rigid Pattern

```python
oxy.ReActAgent(
    name="qa_agent",
    llm_model="default_llm",
    prompt=SYSTEM_PROMPT + "\nYou can refer to the following information to answer the question:\n${preceding_text}",
    preceding_oxy=["user_profile_retrieve"],
    preceding_placeholder="preceding_text",
)
```

Key parameters:

- **`preceding_oxy=["user_profile_retrieve"]`**: Before every query, the system automatically calls the `user_profile_retrieve` tool from the bank. This is not optional; it happens for every request.
- **`preceding_placeholder="preceding_text"`**: The retrieval result replaces `${preceding_text}` in the prompt.
- **`prompt`**: Extends the default `SYSTEM_PROMPT` with a section that references the preceding text, ensuring the agent knows to use the retrieved context.

This is the "rigid" approach because the tool call is hardcoded into the agent lifecycle, not subject to the agent's reasoning.

### Request Filter

```python
def func_filter(payload):
    payload["group_data"] = {"user_pin": "002"}
    return payload
```

Injects user identity for bank data scoping.

### Entry Point

```python
async def main():
    async with MAS(oxy_space=oxy_space, func_filter=func_filter) as mas:
        await mas.start_web_service(first_query="Who I am")
```

## Key Concepts

- **Rigid vs Autonomy Mode**: In rigid mode, bank tools are called deterministically via `preceding_oxy` before every query. In autonomy mode, the agent decides when to call tools. Rigid mode is more predictable and ensures context is always available; autonomy mode is more flexible but depends on the LLM's reasoning.
- **Preceding Oxy**: A mechanism that automatically invokes specified tools before the agent's main processing loop. Results are injected into the prompt via named placeholders.
- **`SYSTEM_PROMPT`**: The default system prompt imported from `oxygent.prompts`, extended with a section for preceding context. This provides the agent with its base instructions plus retrieved information.

## Expected Behavior

1. The web UI opens with the query "Who I am".
2. Before the agent processes the query, `user_profile_retrieve` is automatically called from the bank for user `002`.
3. The retrieved profile data is injected into the prompt at `${preceding_text}`.
4. The `qa_agent` answers using both the system prompt instructions and the retrieved user profile.
5. Every subsequent query will also trigger automatic profile retrieval, ensuring consistent context.
