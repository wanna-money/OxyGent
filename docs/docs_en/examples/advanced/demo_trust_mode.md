# Trust Mode

**Source:** `examples/advanced/demo_trust_mode.py`

## Overview

This example demonstrates the `trust_mode` parameter on a ReActAgent, which controls whether tool calls from the LLM are executed without verification. Two identical agents are configured -- one in normal mode and one in trust mode -- so you can observe the behavioral difference when both answer the same time query.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Node.js runtime (for `uvx` to run the MCP time server)

## How to Run

```bash
python -m examples.advanced.demo_trust_mode
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from environment |
| `time_tools` | `StdioMCPClient` | `command="uvx"`, `args=["mcp-server-time", "--local-timezone=Asia/Shanghai"]` |
| `normal_agent` | `ReActAgent` | `tools=["time_tools"]`, `llm_model="default_llm"`, `trust_mode=False` |
| `trust_agent` | `ReActAgent` | `tools=["time_tools"]`, `llm_model="default_llm"`, `trust_mode=True` |

Both agents share the same LLM and the same MCP time tool. The only difference is the `trust_mode` flag.

### Entry Point

`main()` creates a `MAS` context and directly calls each agent via `mas.call()` with the same query `"What is the current time"`:

1. Calls `normal_agent` and prints the result.
2. Calls `trust_agent` and prints the result.

Note: This example uses `mas.call()` (programmatic invocation) instead of `mas.start_web_service()`, so it runs as a CLI script without launching a web server.

## Key Concepts

- **trust_mode=False (Normal Mode)** -- The agent's tool call decisions go through the standard ReAct verification loop. The LLM decides to call a tool, the framework executes it, and the LLM reflects on the observation before producing the final answer.
- **trust_mode=True (Trust Mode)** -- Tool calls are executed with less overhead, trusting the LLM's decisions more directly. This can reduce latency and token usage for well-understood, low-risk tool calls.
- **StdioMCPClient** -- Connects to an MCP server via stdio. Here it launches `mcp-server-time` to provide timezone-aware time queries.
- **mas.call()** -- A direct programmatic way to invoke a specific named agent, as an alternative to `chat_with_agent()` or the web service.

## Expected Behavior

1. The script prints `=== normal mode test ===` followed by the current time as returned by the normal agent.
2. The script prints `=== trust mode test ===` followed by the current time as returned by the trust agent.
3. Both agents should return the correct current time in Asia/Shanghai timezone, but the trust mode agent may complete faster due to reduced verification overhead.
