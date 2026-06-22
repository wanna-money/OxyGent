# SFT Data Evaluation and Evolution (Batch Processing)

**Source:** `examples/agents/demo_evaluate_and_evolve.py`

## Overview

This example demonstrates how to use OxyGent for batch data processing -- specifically, reviewing Supervised Fine-Tuning (SFT) training data for quality. A `ChatAgent` with a detailed evaluation prompt reviews LLM node data retrieved from Elasticsearch, determines whether each sample qualifies as a high-quality SFT positive example, and the results are parsed to filter and export a clean JSONL training dataset. This pattern is ideal for data quality pipelines, automated content review, and any batch AI evaluation task.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`
- An Elasticsearch instance with existing LLM node data (populated by previous OxyGent runs), or the local ES fallback with stored data

## How to Run

```bash
python -m examples.agents.demo_evaluate_and_evolve
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars; `semaphore=4` (max 4 concurrent requests); `is_save_data=False` |
| `sft_agent` | `ChatAgent` | `prompt=sft_prompt` (detailed SFT review instructions); `llm_model="default_llm"`; `is_save_data=False` |

Both components have `is_save_data=False` to avoid storing the review process itself back into the database, keeping the data pipeline clean.

### The SFT Evaluation Prompt

The `sft_prompt` instructs the agent to act as a strict SFT data reviewer. For each sample containing `node_id`, `input` (messages array), and `output` (candidate reply), it evaluates four criteria:

1. **Follows system instructions / tool invocation rules** -- the output must comply with any system-specified constraints.
2. **Fulfills user needs and is factually correct** -- logically sound, accurate, properly formatted.
3. **No violations / low-quality content** -- no privacy breaches, offensive language, or filler.
4. **Clear and fluent language** -- smooth and clear.

The output must be a single JSON object:
```json
{
  "node_id": "...",
  "keep": true | false,
  "reason": "<within 20 characters>"
}
```

### Helper Functions

#### `get_llm_node_data(mas)`

An async function that queries Elasticsearch for the 32 most recent LLM node records:

1. Searches the `{mas.name}_node` index for documents where `node_type == "llm"`.
2. Sorts by `create_time` descending, limited to 32 results.
3. For each hit, extracts the `node_id`, `input` (parsed from JSON), and `output`.
4. Returns two lists: `app_node_data` (formatted review items) and `datas` (raw message arrays for the final dataset).

#### `parse_results(to_jsonl_path, datas, results)`

A synchronous function that processes the agent's review results:

1. For each result, extracts the JSON block from the markdown code fence (```json ... ```).
2. If `keep` is `true`, the corresponding raw message data is added to the dataset.
3. Prints a summary of filtered vs. kept samples.
4. Writes the kept samples to the specified JSONL file.

### Entry Point

```python
async def main():
    to_jsonl_path = "./sft_dataset.jsonl"
    async with MAS(oxy_space=oxy_space) as mas:
        app_node_data, datas = await get_llm_node_data(mas)
        results = await mas.start_batch_processing(app_node_data)
        parse_results(to_jsonl_path, datas, results)
```

This uses `mas.start_batch_processing()` instead of `start_web_service()` or `start_cli_mode()`. Batch processing sends all items concurrently (bounded by the LLM's `semaphore=4`) and collects all results.

## Key Concepts

- **Batch processing** -- `mas.start_batch_processing(items)` processes a list of inputs concurrently through the master agent and returns a list of results. No web UI or CLI interaction is involved.
- **`is_save_data=False`** -- prevents the review agent's own interactions from being stored in the database, which would pollute the training data pipeline.
- **`semaphore=4`** -- limits the LLM to 4 concurrent API calls, preventing rate limit issues during batch processing.
- **Data pipeline pattern** -- retrieve data from ES, evaluate with an LLM agent, parse results, export filtered data. This is a complete automated data quality pipeline.
- **SFT data quality** -- the prompt encodes a comprehensive rubric for evaluating whether LLM outputs are suitable for supervised fine-tuning.

## Expected Behavior

1. The script connects to Elasticsearch and retrieves up to 32 recent LLM node records.
2. Each record is sent to the `sft_agent` for quality evaluation (up to 4 in parallel).
3. The agent reviews each sample against the four criteria and outputs a JSON verdict.
4. Results are parsed: samples marked `"keep": true` are retained.
5. A summary is printed: "Filter out X samples and keep Y samples."
6. The kept samples are written to `./sft_dataset.jsonl`.
7. The script exits after processing (no web server is started).
