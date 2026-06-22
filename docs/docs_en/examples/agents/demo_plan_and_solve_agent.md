# Plan-and-Solve Agent

**Source:** `examples/agents/demo_plan_and_solve_agent.py`

## Overview

This example demonstrates the Plan-and-Solve pattern in OxyGent, where a `PlanAndSolveAgent` orchestrates two specialized agents: a planner (`ChatAgent`) that creates and updates task plans, and an executor (`ReActAgent`) that carries out individual steps. The planner generates a JSON-formatted plan, and the executor processes one step at a time, with the plan dynamically updated after each step. This pattern is ideal for complex, multi-step tasks that benefit from explicit planning and adaptive re-planning.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`

## How to Run

```bash
python -m examples.agents.demo_plan_and_solve_agent
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
| `planner_agent` | `ChatAgent` | Custom `prompt` with `{past_plan}` and `{past_steps}` template variables for iterative plan refinement; outputs JSON list format |
| `time_tools` | `preset_tools.time_tools` | Built-in time utility tools |
| `file_tools` | `preset_tools.file_tools` | Built-in file operation tools |
| `executor_agent` | `ReActAgent` | `additional_prompt` instructing it to execute only the current step; `tools=["time_tools", "file_tools"]` |
| `master_agent` | `PlanAndSolveAgent` | `is_master=True`; `planner_agent="planner_agent"`; `executor_agent="executor_agent"` |

The **planner's prompt** is designed for iterative planning:

```
The origin plan is:
{past_plan}

We have finished the following steps:
{past_steps}

Please update the plan considering the mentioned information.
...
Please reply in JSON list format only, nothing else
```

The `{past_plan}` and `{past_steps}` placeholders are filled by the `PlanAndSolveAgent` at each iteration to provide the planner with context about what has been done and what remains.

The **executor's `additional_prompt`** constrains it to execute only one step at a time: "You should only execute the current step, and do not execute other steps in our plan. Do not execute more than one step continuously or skip any step."

### Entry Point

```python
await mas.start_web_service(
    first_query="What time is it now? Please save it into time.txt."
)
```

Launches the web service with a compound query requiring time retrieval and file writing.

## Key Concepts

- **Plan-and-Solve pattern** -- separates planning from execution. The planner creates a structured plan, the executor handles one step, then the planner re-plans based on progress.
- **`PlanAndSolveAgent`** -- the orchestrator that loops between the planner and executor agents until the plan is complete.
- **`planner_agent` / `executor_agent`** -- the two required sub-components. The planner must output a JSON list of steps; the executor must be capable of performing individual steps.
- **Iterative re-planning** -- after each step completes, the planner receives the updated context (`past_plan` + `past_steps`) and can adjust the remaining plan.
- **`preset_tools`** -- `time_tools` and `file_tools` are built-in FunctionHub tools that provide time queries and file I/O respectively.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The query "What time is it now? Please save it into time.txt." is sent.
3. The `PlanAndSolveAgent` orchestration begins:
   - The planner creates an initial plan, e.g., `["Get the current time", "Save the time to time.txt"]`.
   - The executor performs step 1: uses `time_tools` to get the current time.
   - The planner re-plans with the completed step context, producing the remaining plan.
   - The executor performs step 2: uses `file_tools` to write the time to `time.txt`.
4. The final result confirms both steps completed and the time has been saved.
5. A `time.txt` file is created with the current time.
