# FunctionHub Tool Demo

**Source:** `examples/tools/demo_functionhub.py`

## Overview

This example demonstrates how to create custom tools using the `FunctionHub` decorator pattern and attach them to a ReAct agent. A simple joke-telling tool is defined, registered into a `FunctionHub`, and then wired into a `ReActAgent` that can invoke it during reasoning. The agent is launched with a web UI and an initial query asking for a joke.

## Prerequisites

- Environment variables (set in `.env` or shell):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM API
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier (e.g., `gpt-4`)
- Python 3.10+ with project dependencies installed (`pip install -r requirements.txt`)

## How to Run

```bash
python -m examples.tools.demo_functionhub
```

## Code Walkthrough

### Configuration

An `HttpLLM` instance named `"default_llm"` is created using environment variables for the API key, base URL, and model name. No additional LLM parameters are set, so framework defaults apply.

### Components (`oxy_space`)

The `oxy_space` list contains three components:

1. **`HttpLLM("default_llm")`** -- The language model used by the agent for reasoning.
2. **`FunctionHub("joke_tools")`** -- A tool hub that groups one or more Python functions as callable tools. A single tool `joke_tool` is registered via the `@fh_joke_tools.tool()` decorator.
3. **`ReActAgent("joke_agent")`** -- A ReAct-style agent that references `"joke_tools"` in its `tools` list. During execution, the agent can decide to call `joke_tool` as part of its reasoning-action loop.

### Tool Definition

The `joke_tool` function is decorated with `@fh_joke_tools.tool(description="a tool for telling jokes")`. It accepts a `joke_type` parameter (typed with Pydantic `Field` for description metadata) and returns a randomly selected joke from a hardcoded list. The `Field(description=...)` annotation ensures the LLM receives a clear parameter description when the tool schema is injected into the prompt.

### Entry Point

The `main()` coroutine creates a `MAS` (Multi-Agent System) context manager with the `oxy_space`, then starts a web service with the initial query `"Please tell a joke"`. This launches a FastAPI server (default `127.0.0.1:8080`) with a built-in web UI.

## Key Concepts

- **FunctionHub** -- A lightweight way to wrap plain Python functions as agent-callable tools. Each function decorated with `@hub.tool()` becomes discoverable by agents that reference the hub name.
- **Pydantic Field metadata** -- Using `Field(description=...)` on function parameters ensures the LLM receives accurate tool parameter descriptions, improving tool-call accuracy.
- **ReActAgent** -- An agent that follows the Reasoning-Action loop: it reasons about the task, decides which tool to call, observes the result, and repeats until it can produce a final answer.
- **oxy_space** -- The flat list of all Oxy components (LLMs, tools, agents) that the MAS runtime wires together by name references.

## Expected Behavior

1. The web server starts at `http://127.0.0.1:8080`.
2. The agent receives the query "Please tell a joke".
3. The agent reasons that it should use the `joke_tool` and calls it (potentially with a joke type).
4. The tool returns a random joke from the predefined list.
5. The agent presents the joke to the user in the web UI.
