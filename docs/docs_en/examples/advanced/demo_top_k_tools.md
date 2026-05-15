# Top-K Tool Retrieval via Vector Similarity

**Source:** `examples/advanced/demo_top_k_tools.py`

## Overview

This example demonstrates the `top_k_tools` feature, which uses vector similarity search to select only the most relevant tools for each query before sending them to the LLM. When an agent has many tools registered, this reduces prompt size and improves tool selection accuracy by presenting only the top N most relevant tools on each turn.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- A Vearch vector database instance (configured in `config.json` under the `test` environment)
- An embedding model (configured in `config.json` for vector similarity computation)
- Node.js runtime (for `npx` to run the MCP filesystem server and `uvx` for the time server)

## How to Run

```bash
python -m examples.advanced.demo_top_k_tools
```

## Code Walkthrough

### Configuration

```python
Config.load_from_json("./config.json", env="test")
```

Loads configuration from `config.json` using the `test` environment overlay. This environment must define Vearch vector database settings (e.g., `vearch.router_url`, `vearch.db_name`) and embedding model configuration required for vector similarity search.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from environment; `llm_params={"temperature": 0.1}` |
| `time_tools` | `StdioMCPClient` | `command="uvx"`, `args=["mcp-server-time", "--local-timezone=Asia/Shanghai"]` |
| `file_tools` | `StdioMCPClient` | `command="npx"`, `args=["-y", "@modelcontextprotocol/server-filesystem", "./local_file"]` |
| `master_agent` | `ReActAgent` | `llm_model="default_llm"`, `tools=["time_tools", "file_tools"]`, `top_k_tools=3` |

The `master_agent` has both `time_tools` and `file_tools` registered, which together may expose many individual tool functions. With `top_k_tools=3`, only the 3 most relevant tools (by vector similarity to the current query) are included in the LLM prompt.

### Entry Point

`main()` creates a `MAS` context and starts the web service with `first_query="What time is it now?"`. For this query, the vector similarity search should rank time-related tools higher than file-related tools.

## Key Concepts

- **top_k_tools** -- An integer parameter on agents that limits the number of tools presented to the LLM per query. Tools are ranked by vector similarity between the query and each tool's description.
- **Vearch** -- A vector database used by the framework for tool retrieval. Tool descriptions are embedded as vectors and stored in Vearch, enabling efficient similarity search.
- **Config.load_from_json()** -- Loads configuration from a JSON file with environment layering. The `env` parameter selects which environment overlay to apply on top of `default` settings.
- **Dynamic Tool Selection** -- Instead of presenting all tools to the LLM (which can overwhelm the context window and degrade selection accuracy), only the most relevant subset is included dynamically per query.

## Expected Behavior

1. The web service starts on `127.0.0.1:8080`.
2. When the user asks "What time is it now?", the framework computes vector similarity between the query and all available tool descriptions.
3. The top 3 most relevant tools are selected and included in the LLM prompt.
4. The LLM selects the appropriate time tool from the narrowed set and returns the current time.
