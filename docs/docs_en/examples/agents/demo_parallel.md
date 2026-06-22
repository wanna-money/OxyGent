# Parallel Agent (Expert Panel)

**Source:** `examples/agents/demo_parallel.py`

## Overview

This example demonstrates the `ParallelAgent`, which dispatches a single query to multiple expert agents concurrently and aggregates their responses. Four specialized `ChatAgent` instances (technical, business, risk, and legal experts) evaluate a business proposal in parallel, and the `ParallelAgent` collects all their analyses into a unified response. This pattern is ideal for multi-perspective evaluation, expert panels, and any scenario where you need diverse viewpoints on the same input.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`

## How to Run

```bash
python -m examples.agents.demo_parallel
```

## Code Walkthrough

### Configuration

```python
Config.set_agent_llm_model("default_llm")
```

Sets the global default LLM model for all agents.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars |
| `tech_expert` | `ChatAgent` | `prompt`: Senior technical architect; evaluates tech stack, architecture, challenges, resources; outputs feasibility score (1-10) |
| `business_expert` | `ChatAgent` | `prompt`: Business analyst; evaluates market opportunity, business model, ROI, go-to-market strategy; outputs feasibility score (1-10) |
| `risk_expert` | `ChatAgent` | `prompt`: Risk management expert; analyzes technical, market, operational, and compliance risks; rates probability/impact/level |
| `legal_expert` | `ChatAgent` | `prompt`: Legal expert for AI products; analyzes data compliance, AI governance, IP protection, contracts; provides legal risk checklist |
| `expert_panel` | `ParallelAgent` | `permitted_tool_name_list=["tech_expert", "business_expert", "risk_expert", "legal_expert"]`; `is_master=True` |

Each expert agent has a detailed system prompt that constrains it to a specific domain of analysis. The prompts instruct each expert to output structured evaluations with scores and recommendations.

### Entry Point

The `main()` function defines a detailed business query about building an AI customer service system:

```python
query = (
    "We are a mid-sized e-commerce company (50 support staff, 5000+ daily inquiries). "
    "We want to build an AI customer service system that auto-handles 80%+ common questions, "
    ...
    "Please evaluate whether we should proceed."
)
```

This query is sent via `mas.start_web_service(first_query=query)`.

## Key Concepts

- **`ParallelAgent`** -- dispatches the same query to all agents listed in `permitted_tool_name_list` concurrently using `asyncio`, then aggregates the results.
- **`permitted_tool_name_list`** -- the list of agent/tool names that the `ParallelAgent` will invoke in parallel. Despite the name, it works with agents (which are treated as callable tools in OxyGent).
- **Expert specialization** -- each `ChatAgent` is constrained by its prompt to focus on a single evaluation dimension, preventing overlap and ensuring comprehensive coverage.
- **Concurrent execution** -- all four experts process the query simultaneously, significantly reducing total latency compared to sequential execution.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The detailed AI customer service proposal query is sent.
3. The `ParallelAgent` dispatches the query to all four experts concurrently.
4. Each expert generates its domain-specific analysis:
   - **Technical expert**: evaluates tech stack feasibility, architecture, and resource requirements.
   - **Business expert**: assesses market opportunity, ROI, and go-to-market strategy.
   - **Risk expert**: identifies and rates technical, market, operational, and compliance risks.
   - **Legal expert**: analyzes data compliance, AI governance, and IP protection.
5. All four analyses are aggregated into a single comprehensive response displayed in the web UI.
6. The total response time is approximately the duration of the slowest expert (not the sum of all).
