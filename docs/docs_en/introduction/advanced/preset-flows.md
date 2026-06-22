# How to Use Preset Flows?

For developers, encapsulating commonly used workflows as preset [Flows] is essential.

You can create your own flow by inheriting from the `BaseFlow` class and implementing the specific work logic of the flow in the `_execute()` method. A flow accepts an `oxy.OxyRequest` as input and outputs an `oxy.Response`, so it can run like a normal Agent within the MAS system without any compatibility issues.

Below, we use OxyGent's preset `PlanAndSolve` flow as an example to demonstrate how to create a flow.

## PlanAndSolve Flow

`PlanAndSolve` implements a "plan first, then execute" workflow pattern. It breaks down complex tasks into multiple steps, where a planner agent generates the plan and an executor agent completes the steps sequentially.

### How It Works

1. **Planning Phase** -- The `planner_agent` decomposes the user request into an ordered list of steps
2. **Execution Phase** -- Steps are executed one by one, each completed by the `executor_agent`
3. **Replanning (Optional)** -- If `enable_replanner` is enabled, the plan can be dynamically adjusted after each step based on results
4. **Completion** -- The final result is output when all steps are done or the replanner returns a direct response

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | required | Name of the flow |
| `is_master` | `bool` | `False` | Whether this flow serves as the MAS entry agent |
| `planner_agent_name` | `str` | `"planner_agent"` | Name of the agent responsible for generating the plan |
| `executor_agent_name` | `str` | `"executor_agent"` | Name of the agent responsible for executing each step |
| `enable_replanner` | `bool` | `False` | Whether to dynamically adjust the plan after each step |
| `max_replan_rounds` | `int` | `30` | Maximum number of execution/replanning rounds |
| `pre_plan_steps` | `list[str]` | `None` | Predefined plan steps (skips the planning phase) |
| `llm_model` | `str` | `"default_llm"` | Fallback LLM model name |

### Usage Example

```python
oxy.PlanAndSolve(
    name="plan_flow",
    is_master=True,
    planner_agent_name="planner",
    executor_agent_name="executor",
    enable_replanner=False,
    max_replan_rounds=30,
)
```

## Reflexion Flow

`Reflexion` implements an "execute-reflect-improve" iterative workflow pattern. A worker agent completes the task, then a reflexion agent evaluates the result and provides improvement suggestions, iterating until the result is satisfactory or the maximum number of rounds is reached.

### How It Works

1. **Execution Phase** -- The `worker_agent` executes the task based on the user request
2. **Reflexion Phase** -- The `reflexion_agent` evaluates the execution result and determines if it is satisfactory
3. **Iteration** -- If not satisfactory, feedback is passed back to the `worker_agent` for re-execution
4. **Completion** -- The final result is output when the reflexion agent is satisfied or `max_reflexion_rounds` is reached

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | required | Name of the flow |
| `is_master` | `bool` | `False` | Whether this flow serves as the MAS entry agent |
| `worker_agent` | `str` | required | Name of the worker agent that executes the task |
| `reflexion_agent` | `str` | required | Name of the reflexion agent that evaluates results |
| `max_reflexion_rounds` | `int` | `3` | Maximum number of reflexion iterations |

### Usage Example

```python
oxy.Reflexion(
    name="reflexion_flow",
    is_master=True,
    worker_agent="worker",
    reflexion_agent="evaluator",
    max_reflexion_rounds=3,
)
```

[Previous: Creating Workflows](./workflow.md)
[Next: Retrieving Memory and Regenerating](./continue-exec.md)
[Back to Home](../readme.md)

---

## Related Examples

- [PlanAndSolve Flow Example](../../examples/flows/plan_and_solve_demo.md) -- Demonstrates how to use the PlanAndSolve flow for task planning and execution
- [Reflexion Flow Example](../../examples/flows/reflexion_agent_demo.md) -- Demonstrates how to use the Reflexion flow for reflexion and optimization
