# Custom Shared Data Schema for Elasticsearch

**Source:** `examples/backend/demo_custom_shared_data_schema.py`

## Overview

This example demonstrates how to define a custom Elasticsearch mapping for the `shared_data` field and populate it during request processing. This is useful when you need to persist structured metadata (such as user identity) alongside conversation traces in Elasticsearch for later querying and analytics.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Elasticsearch instance (or the local fallback `LocalEs` will be used)

## How to Run

```bash
python -m examples.backend.demo_custom_shared_data_schema
```

## Code Walkthrough

### Configuration

```python
Config.set_es_schema_shared_data(
    {
        "properties": {
            "user_pin": {"type": "keyword"},
            "user_name": {"type": "keyword"},
        }
    }
)
```

This call customizes the Elasticsearch mapping for `shared_data`. By declaring `user_pin` and `user_name` as `keyword` fields, you enable exact-match queries and aggregations on these fields in Elasticsearch.

### Hook Functions

```python
def process_input(oxy_request: OxyRequest) -> OxyRequest:
    oxy_request.set_shared_data("user_pin", "123456")
    oxy_request.set_shared_data("user_name", "oxy")
    return oxy_request
```

The `process_input` function is a pre-execution hook (`func_process_input`) that injects user metadata into the request's `shared_data` before the agent executes. This data will be stored in Elasticsearch with the trace.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | Standard LLM credentials from environment |
| `master_agent` | `ReActAgent` | `func_process_input=process_input` -- attaches the pre-processing hook |

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="hello")
```

## Key Concepts

- **Custom ES schema for shared_data**: `Config.set_es_schema_shared_data()` lets you define the Elasticsearch mapping for the `shared_data` field on trace documents, enabling structured storage and querying.
- **shared_data**: A per-request key-value store carried on `OxyRequest`. Data set here is persisted with the trace and accessible by all components in the execution chain.
- **func_process_input**: A hook function that runs before the agent's main execution logic. It receives and returns an `OxyRequest`, allowing you to enrich or transform the request.

## Expected Behavior

1. The ES mapping is configured to include `user_pin` and `user_name` as keyword fields.
2. On each request, the `process_input` hook populates `shared_data` with `user_pin="123456"` and `user_name="oxy"`.
3. The `ReActAgent` processes the query, and the enriched `shared_data` is persisted alongside the trace in Elasticsearch.
4. The web service launches with `"hello"` as the initial query.
