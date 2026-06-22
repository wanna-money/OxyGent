# RAG (Retrieval-Augmented Generation) Agent

**Source:** `examples/agents/demo_rag_agent.py`

## Overview

This example demonstrates how to build a Retrieval-Augmented Generation (RAG) agent using OxyGent's `RAGAgent`. It uses a custom knowledge retrieval function to inject external knowledge into the agent's prompt before the LLM generates an answer. This pattern is ideal for question-answering systems that need to ground their responses in specific, retrieved data (e.g., from a database, vector store, or API).

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`

## How to Run

```bash
python -m examples.agents.demo_rag_agent
```

## Code Walkthrough

### Hook Functions

#### `func_retrieve_knowledge(oxy_request: OxyRequest) -> str`

An async retrieval function registered via `func_retrieve_knowledge`. It is called before the LLM invocation to fetch relevant knowledge:

1. Extracts the user query via `oxy_request.get_query()`.
2. Prints the query for debugging.
3. Returns a hardcoded string: `"Pi is 3.141592653589793238462643383279502."`.

In a production system, this function would query a vector database, search engine, or knowledge base to retrieve contextually relevant information.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars |
| `qa_agent` | `RAGAgent` | `llm_model="default_llm"`; `prompt` with `${knowledge}` placeholder; `knowledge_placeholder="knowledge"`; `func_retrieve_knowledge=func_retrieve_knowledge` |

The `RAGAgent`'s prompt contains a template variable `${knowledge}`:

```
You are a helpful assistant! You can refer to the following knowledge to answer the questions:
${knowledge}
```

At runtime, the `RAGAgent` calls `func_retrieve_knowledge`, and the returned string replaces the `${knowledge}` placeholder in the prompt before it is sent to the LLM.

### Entry Point

```python
await mas.start_web_service(
    first_query="Please calculate the 20 positions of Pi",
)
```

Launches the web service with a Pi-related initial query.

## Key Concepts

- **RAG pattern** -- Retrieval-Augmented Generation separates knowledge retrieval from generation. The retrieval function provides context, and the LLM generates a response grounded in that context.
- **`knowledge_placeholder`** -- the name of the template variable in the prompt (here `"knowledge"`) that gets replaced with the retrieved content.
- **`func_retrieve_knowledge`** -- the async function that performs the actual retrieval. It receives the full `OxyRequest` so it can access the query, memory, and other context.
- **Prompt templating** -- the `${knowledge}` syntax in the prompt is replaced at runtime, allowing dynamic context injection.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The initial query "Please calculate the 20 positions of Pi" is sent.
3. The `RAGAgent` calls `func_retrieve_knowledge`, which returns the hardcoded Pi value.
4. The prompt is assembled with the Pi knowledge injected into the `${knowledge}` placeholder.
5. The LLM generates an answer referencing the retrieved Pi digits.
6. The response is displayed in the web UI, showing the first 20 decimal positions of Pi based on the provided knowledge.
