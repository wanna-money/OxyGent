# Live Prompt with Shared Prompt Keys

**Source:** `examples/live_prompts/demo_live_prompt.py`

## Overview

This example demonstrates how multiple agents can share the same live prompt via a common `prompt_key`, and how individual agents can opt out of the live prompt system entirely. It sets up three `ChatAgent` instances to illustrate prompt key sharing and the `use_live_prompt` toggle.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`
- Elasticsearch backend (or local fallback) for live prompt storage

## How to Run

```bash
python -m examples.live_prompts.demo_live_prompt
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | `prompt_key` | `use_live_prompt` | Behavior |
|-----------|------|-------------|-------------------|----------|
| `default_llm` | `HttpLLM` | N/A | N/A | LLM with credentials from env vars |
| `chat_agent1` | `ChatAgent` | `"my_prompt"` | `True` (default) | Uses live prompt keyed by `"my_prompt"` |
| `chat_agent2` | `ChatAgent` | `"my_prompt"` | `True` (default) | Shares the same live prompt as `chat_agent1` |
| `chat_agent3` | `ChatAgent` | N/A | `False` | Uses the static code-level prompt only |

### Prompt Key Sharing

`chat_agent1` and `chat_agent2` both set `prompt_key="my_prompt"`. This means:

- They share the same prompt entry in the live prompt store (Elasticsearch).
- When the prompt for key `"my_prompt"` is updated at runtime, **both** agents receive the updated prompt simultaneously.
- Their initial code-level prompt (`"You are a helpful assistant."`) serves as the default value if no live prompt has been configured yet.

### Opting Out of Live Prompts

`chat_agent3` sets `use_live_prompt=False`:

- It always uses its code-level prompt (`"You are a helpful assistant."`) regardless of any changes in the live prompt store.
- It does not participate in the live prompt system at all.

### Entry Point

```python
await mas.start_web_service(first_query="hello")
```

Launches the web service with the initial greeting "hello".

## Key Concepts

- **`prompt_key`** -- A shared identifier that maps multiple agents to the same prompt entry in the live prompt store. Agents with the same `prompt_key` will all use (and be updated by) the same prompt content.
- **Live Prompt System** -- Backed by Elasticsearch (or `LocalEs` fallback), the live prompt system (`oxygent/live_prompt/`) allows runtime prompt updates. Changes propagate to all agents sharing the same `prompt_key` without restarting the service.
- **`use_live_prompt=False`** -- Disables the live prompt system for a specific agent. The agent's prompt is fixed to the value defined in code.
- **`ChatAgent`** -- A conversational agent type that maintains chat context. Unlike `ReActAgent`, it does not follow the Reasoning-Action cycle and does not use tools.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The initial query "hello" is sent to the system.
3. `chat_agent1` and `chat_agent2` both respond using the same prompt. If the live prompt for key `"my_prompt"` is updated via the prompt management API, both agents will reflect the change on subsequent queries.
4. `chat_agent3` always responds using its static prompt `"You are a helpful assistant."`, unaffected by any runtime prompt changes.
