# Mixture of Agents (MoA)

**Source:** `examples/agents/demo_mixture_of_agents.py`

## Overview

This example demonstrates the Mixture of Agents (MoA) pattern using the `team_size` parameter. Setting `team_size=N` on an agent causes N parallel instances to process the same query concurrently, producing an ensemble of responses that are aggregated into a single answer. Combined with a higher temperature setting, this creates diverse yet high-quality responses. This pattern is ideal for improving response reliability and quality through ensemble methods.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`

## How to Run

```bash
python -m examples.agents.demo_mixture_of_agents
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars; `llm_params={"temperature": 0.7}` |
| `qa_agent` | `ChatAgent` | `llm_model="default_llm"`; `team_size=4` |

The two critical settings are:

- **`temperature=0.7`** -- a moderately high temperature encourages diversity across the parallel instances. Each instance will generate a somewhat different response to the same query.
- **`team_size=4`** -- creates 4 parallel instances of `qa_agent`. All 4 process the same input concurrently, and their responses are aggregated into a single final answer.

### Entry Point

```python
await mas.start_web_service(first_query="What is the Agent?")
```

Launches the web service with a conceptual question that benefits from multi-perspective answers.

## Key Concepts

- **Mixture of Agents (MoA)** -- an ensemble technique where multiple agent instances independently process the same query. The diverse outputs are then synthesized into a single, more robust answer.
- **`team_size`** -- the number of parallel agent instances to create. When `team_size > 1`, the framework automatically runs N copies of the agent concurrently and aggregates results.
- **Temperature for diversity** -- setting `temperature=0.7` (instead of a low value like 0.01) ensures that each parallel instance generates a meaningfully different response, making the ensemble more valuable.
- **Aggregation** -- the framework handles the aggregation of multiple responses automatically, combining the best elements from each instance's output.
- **Minimal configuration** -- achieving MoA requires only setting `team_size` on an existing agent and adjusting the temperature. No additional agents or orchestration logic is needed.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The query "What is the Agent?" is sent.
3. Four parallel instances of `qa_agent` process the query simultaneously.
4. Each instance generates a somewhat different response due to `temperature=0.7`.
5. The four responses are aggregated into a single comprehensive answer.
6. The aggregated answer is displayed in the web UI, typically richer and more balanced than any single instance's response.
