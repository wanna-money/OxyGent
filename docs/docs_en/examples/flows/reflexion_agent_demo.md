# Reflexion Agent Demo

**Source:** `examples/flows/reflexion_agent_demo.py`

## Overview

This example demonstrates the **Reflexion** flow pattern in OxyGent, where an agent iteratively refines its answers through self-evaluation. The demo registers two reflexion workflows -- a general-purpose reflexion loop and a math-specific reflexion loop -- along with a master agent that routes questions to the appropriate workflow. Both workflows follow the same iterative pattern: generate an answer, evaluate its quality, and refine until satisfactory or a maximum number of rounds is reached.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- OxyGent package installed (`pip install -r requirements.txt`)

## How to Run

```bash
python -m examples.flows.reflexion_agent_demo
```

The demo starts a web service (default `127.0.0.1:8080`) with the initial query "Calculate the area of a circle with radius 5."

## Code Walkthrough

### Configuration

```python
Config.set_agent_llm_model("default_llm")
```

Sets the default LLM model name that all agents will use. The actual LLM is configured as an `HttpLLM` in the `oxy_space` list with a low temperature (0.01) for deterministic output and a concurrency semaphore of 4.

### Components (`oxy_space`)

| Component | Type | Role |
|---|---|---|
| `default_llm` | `HttpLLM` | Shared language model for all agents |
| `worker_agent` | `ReActAgent` | Generates initial answers for general questions |
| `reflexion_agent` | `ChatAgent` | Evaluates answer quality and suggests improvements |
| `math_expert_agent` | `ChatAgent` | Solves mathematical problems with detailed steps |
| `math_checker_agent` | `ChatAgent` | Validates mathematical solutions for correctness |
| `general_reflexion` | `Reflexion` | Built-in Reflexion flow using `worker_agent` and `reflexion_agent` |
| `math_reflexion` | `MathReflexion` | Built-in MathReflexion flow for math-specific validation |
| `master_agent` | `ReActAgent` | Routes questions to `general_reflexion` or `math_reflexion` |

The `general_reflexion` node is marked `is_master=True`, meaning it serves as the default entry point. It references `worker_agent` as the answer generator and `reflexion_agent` as the evaluator, with up to 3 reflexion rounds.

### Workflow Functions

Two async workflow functions are defined but serve as reference implementations illustrating the reflexion pattern manually:

1. **`reflexion_workflow`** -- General-purpose reflexion loop:
   - Calls `worker_agent` to produce an initial answer.
   - Sends the answer plus the original question to `reflexion_agent` for evaluation.
   - Parses the evaluation for "Satisfactory" / "Unsatisfactory".
   - If unsatisfactory, extracts improvement suggestions and appends them to the query for the next round.
   - Repeats up to `max_iterations` (3) times.

2. **`math_reflexion_workflow`** -- Math-specific reflexion loop:
   - Calls `math_expert_agent` to solve the problem.
   - Sends the solution to `math_checker_agent` for verification against correctness criteria (calculation steps, completeness, clarity).
   - Parses the result for "Pass" / "Fail".
   - If failed, extracts correction suggestions and repeats.

Note: In production, the built-in `Reflexion` and `MathReflexion` flow classes handle this loop automatically. The manual functions show the underlying logic.

### Entry Point

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="Calculate the area of a circle with radius 5.")
```

Creates a `MAS` instance, registers all components, and starts the web service. The `first_query` is automatically sent when the web UI loads.

## Key Concepts

- **Reflexion Pattern**: An iterative self-improvement loop where an agent generates an answer, a critic evaluates it, and feedback is incorporated into subsequent attempts. This mimics how humans revise drafts.
- **Reflexion vs. MathReflexion**: `Reflexion` is general-purpose; `MathReflexion` uses domain-specific verification criteria (calculation correctness, step completeness).
- **`is_master=True`**: Marks the component as the entry point for incoming user queries in the MAS.
- **`max_reflexion_rounds`**: Controls the maximum number of evaluate-and-improve iterations before returning the best available answer.
- **`oxy_request.call()`**: The mechanism for one Oxy component to invoke another by name, passing arguments and receiving an `OxyResponse`.

## Expected Behavior

1. The web UI opens and sends the math query.
2. The `master_agent` routes the question to the appropriate reflexion workflow.
3. The worker/expert agent generates an initial answer (e.g., area = pi * 25 = 78.54).
4. The evaluator/checker agent reviews the answer for quality/correctness.
5. If the answer passes evaluation, it is returned immediately. Otherwise, the loop continues with feedback incorporated.
6. The final answer is displayed in the web UI, annotated with how many reflexion rounds were needed.
