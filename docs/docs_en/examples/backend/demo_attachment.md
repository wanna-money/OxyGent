# Sending Attachments to a Chat Agent

**Source:** `examples/backend/demo_attachment.py`

## Overview

This example demonstrates how to send file attachments along with a query to a multimodal-capable chat agent. It shows both the programmatic API (`mas.chat_with_agent`) and the web service mode. This pattern is useful when you need the LLM to analyze or summarize the contents of files such as documents, images, or code.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- The LLM endpoint must support multimodal input (the example sets `is_multimodal_supported=True`)
- The file `README.md` must exist in the working directory (it is referenced as an attachment)

## How to Run

```bash
python -m examples.backend.demo_attachment
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `is_multimodal_supported=True` -- enables file/image attachment processing |
| `qa_agent` | `ChatAgent` | Simple chat agent linked to the multimodal LLM |

### Entry Point

The example runs in two phases:

**Phase 1 -- Programmatic call:**

```python
payload = {
    "query": "Introduce the content of the file",
    "attachments": ["README.md"],
}
oxy_response = await mas.chat_with_agent(payload=payload)
print("LLM: ", oxy_response.output)
```

The `attachments` field in the payload accepts a list of file paths. The framework reads the file content and includes it in the LLM request context.

**Phase 2 -- Web service:**

```python
await mas.start_web_service(first_query="Introduce the content of the file")
```

Launches the web UI where users can interactively send queries with attachments.

## Key Concepts

- **Multimodal LLM support**: Setting `is_multimodal_supported=True` on `HttpLLM` enables the model to process file attachments alongside text queries.
- **Attachments in payload**: The `attachments` key in the payload dictionary takes a list of file paths that are bundled into the LLM context.
- **ChatAgent**: A basic conversational agent that forwards the user query (plus any attachments) to the LLM and returns the response.

## Expected Behavior

1. The agent reads the `README.md` file and sends its content along with the query to the LLM.
2. The LLM returns a summary or introduction of the file's content, which is printed to the console.
3. The web service starts and automatically sends the same initial query, displaying the result in the browser.
