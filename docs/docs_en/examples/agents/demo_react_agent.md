# ReAct Agent with Reflexion

**Source:** `examples/agents/demo_react_agent.py`

## Overview

This example demonstrates a `ReActAgent` with a custom reflexion (self-correction) function. The agent uses the Reasoning-and-Acting (ReAct) pattern, and the reflexion callback validates the agent's output format, forcing it to retry if the response is not a pure number. This pattern is useful when you need structured, constrained outputs from an LLM.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`

## How to Run

```bash
python -m examples.agents.demo_react_agent
```

## Code Walkthrough

### Hook Functions

#### `master_reflexion(response: str, oxy_request: OxyRequest) -> str`

A **reflexion** callback registered via `func_reflexion`. After the agent produces a response, this function validates it:

1. It uses a regex pattern `r"^[-+]?(\d+(\.\d*)?|\.\d+)$"` to check whether the response is a valid number (integer or decimal, optionally signed).
2. If the response does **not** match (i.e., it contains non-numeric text), the function returns the Chinese string `"仅回答数字"` ("Only answer with a number"), which is fed back to the agent as corrective feedback, triggering another attempt.
3. If the response **does** match, the function returns `None` (implicitly), indicating the output is acceptable.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars (default settings) |
| `master_agent` | `ReActAgent` | `llm_model="default_llm"`; `func_reflexion=master_reflexion`; `additional_prompt="请你根据我的问题，给出最优的回答"` (Chinese: "Please give the best answer to my question") |

### Entry Point

```python
await mas.start_web_service(first_query="1+1等于几")
```

Launches the web service with the initial query "1+1等于几" (Chinese: "What does 1+1 equal?").

## Key Concepts

- **ReAct Pattern** -- the agent follows a Reasoning-Action cycle: it reasons about the problem, takes an action (e.g., calling a tool or generating an answer), observes the result, and iterates.
- **Reflexion** -- a self-correction mechanism. When `func_reflexion` returns a non-None string, that string is treated as feedback, and the agent retries with the feedback incorporated into its context.
- **`additional_prompt`** -- appended to the agent's system prompt, providing extra instructions without overriding the base prompt.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The first query "1+1等于几" is sent automatically.
3. The agent attempts to answer. If it responds with text like "1+1等于2" (prose), the reflexion function rejects it and sends feedback "仅回答数字".
4. The agent retries and eventually responds with just `"2"` (a pure number), which passes the reflexion validation.
5. The final clean numeric answer is displayed in the web UI.
