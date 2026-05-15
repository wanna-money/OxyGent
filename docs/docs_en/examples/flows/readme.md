# Flow Examples

This directory contains examples demonstrating OxyGent's flow-based orchestration patterns, which coordinate multiple agents through structured multi-step processes like reflexion loops and plan-and-solve pipelines.

---

## Examples

### Reflexion Flow

**File:** `examples/flows/reflexion_agent_demo.py`

Demonstrates the Reflexion and MathReflexion flow patterns for iterative self-improvement of agent outputs. The example defines two reflexion workflows: (1) A general `Reflexion` flow that pairs a `worker_agent` (ReActAgent) for generating initial answers with a `reflexion_agent` (ChatAgent) for evaluating quality. If the reflexion agent deems the answer "Unsatisfactory", it extracts improvement suggestions and feeds them back to the worker for another attempt, looping up to `max_reflexion_rounds=3` times. (2) A `MathReflexion` flow specialized for mathematical problems, using a `math_expert_agent` to produce solutions and a `math_checker_agent` to verify correctness, with a similar Pass/Fail feedback loop. A master ReActAgent sits at the top and routes queries to the appropriate reflexion flow based on the question type, enabling the system to handle both general and math-specific tasks with iterative quality improvement.

**Key Components:**
- `Reflexion` -- general-purpose reflexion flow with configurable worker and evaluator agents
- `MathReflexion` -- math-specialized reflexion flow
- `ReActAgent` -- used as both worker agent and master routing agent
- `ChatAgent` -- used as reflexion evaluator, math expert, and math checker agents
- `HttpLLM` -- backing language model with low temperature for deterministic output

**[Detailed Guide →](./reflexion_agent_demo.md)**

---

### Plan-and-Solve Flow

**File:** `examples/flows/plan_and_solve_demo.py`

Demonstrates the PlanAndSolve flow, which separates complex task execution into a planning phase and a stepwise execution phase. A `planner_agent` (ChatAgent) generates a concise step-by-step plan for any given goal. An `executor_agent` (ReActAgent) carries out each step one at a time, having access to multiple specialized sub-agents (`time_agent`, `file_agent`, `math_agent`) and a joke-telling FunctionHub tool. The `math_agent` is itself a WorkflowAgent with a custom `func_workflow` that demonstrates accessing short memory, sending intermediate messages, calling sub-agents, and invoking MCP tools (for computing Pi). The PlanAndSolve flow coordinates the loop: the planner creates the plan, the executor handles each step, and optionally a replanner can update the plan mid-execution (disabled in this example via `enable_replanner=False`). Configuration is loaded from `config.json`, and MCP tools for time, filesystem, and math are connected via StdioMCPClient. The system is launched with a sample query that combines time retrieval with file writing.

**Key Components:**
- `PlanAndSolve` -- orchestration flow that coordinates planner and executor agents
- `ChatAgent` -- serves as the planner agent
- `ReActAgent` -- serves as both the executor and specialized sub-agents
- `WorkflowAgent` -- custom workflow for the math agent with `func_workflow`
- `FunctionHub` -- joke tool demonstrating custom function tools within the flow
- `StdioMCPClient` -- MCP tool servers for time, filesystem, and math
- `Config.load_from_json()` -- loading configuration from a JSON file

**[Detailed Guide →](./plan_and_solve_demo.md)**
