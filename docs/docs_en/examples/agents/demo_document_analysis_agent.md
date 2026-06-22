# Document Analysis Agent

**Source:** `examples/agents/demo_document_analysis_agent.py`

## Overview

This example demonstrates a `ReActAgent` equipped with preset document processing tools for analyzing various document formats (PDF, Word, Excel, etc.). It combines streaming LLM output with OxyGent's built-in `preset_tools.document_tools`, providing an out-of-the-box document analysis capability. This pattern is useful for building agents that need to parse, extract, and reason over structured documents.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`
- Additional document processing libraries may be required depending on the document types (e.g., `pypdf`, `python-docx`, `openpyxl`)

## How to Run

```bash
python -m examples.agents.demo_document_analysis_agent
```

## Code Walkthrough

### Configuration

```python
Config.set_agent_llm_model("default_llm")
```

Sets the global default LLM model for all agents, so the `document_agent` does not need to specify `llm_model` explicitly.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars; `llm_params={"stream": True}` |
| `document_tools` | `preset_tools.document_tools` | OxyGent's built-in document processing FunctionHub (supports PDF, Word, Excel, etc.) |
| `document_agent` | `ReActAgent` | `desc="A tool that can process and analyze documents (PDF, Word, Excel, etc.)"`; `tools=["document_tools"]` |

The `preset_tools.document_tools` is a pre-built `FunctionHub` that provides document reading and parsing functions. It is included directly in the `oxy_space` list without needing manual configuration.

### Entry Point

```python
await mas.start_web_service(first_query="hello")
```

Launches the web service with a simple greeting as the initial query. Users can then upload or reference documents for analysis.

## Key Concepts

- **`preset_tools`** -- OxyGent provides a set of built-in tool collections (FunctionHub instances) ready to use. `preset_tools.document_tools` includes functions for reading and parsing various document formats.
- **Tool-equipped ReActAgent** -- the agent uses the ReAct pattern to decide when and how to use document tools based on user queries.
- **Streaming + tools** -- combining `stream: True` with tool-calling agents provides responsive output while still leveraging tool capabilities.
- **`Config.set_agent_llm_model()`** -- eliminates the need to set `llm_model` on each agent individually.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The initial query "hello" triggers a general greeting response.
3. When users provide document-related queries (e.g., "Read and summarize this PDF" along with a file path), the agent uses the document tools to parse the file and generates an analysis.
4. The LLM response streams token-by-token to the web UI due to `stream: True`.
5. The agent can handle multiple document types including PDF, Word (.docx), and Excel (.xlsx) files.
