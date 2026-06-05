# 如何使用预设的流（Flow）？

对于开发者来说，将常用的工作流封装为预设的 [流 (Flow)] 是非常必要的。

您可以通过继承 `BaseFlow` 类来创建自己的流，并在 `_execute()` 方法中实现流的具体工作逻辑。流接受一个 `oxy.OxyRequest` 作为输入，并以 `oxy.Response` 作为输出，因此能够在 MAS 系统中像正常的 Agent 一样运行，不会发生兼容性问题。

下面以 OxyGent 预设的 `PlanAndSolve` 流为例，演示如何创建一个流。

## PlanAndSolve 流

`PlanAndSolve` 实现了"先规划再执行"的工作流模式。它将复杂任务拆分为多个步骤，由规划智能体生成计划，再由执行智能体逐步完成。

### 工作流程

1. **规划阶段** -- 调用 `planner_agent` 将用户请求分解为有序的步骤列表
2. **执行阶段** -- 逐个执行步骤，每个步骤由 `executor_agent` 完成
3. **重规划（可选）** -- 如果开启 `enable_replanner`，每一步执行后可根据结果动态调整后续计划
4. **结束** -- 所有步骤完成或重规划返回最终响应时输出结果

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | 必填 | 流的名称 |
| `is_master` | `bool` | `False` | 是否作为 MAS 的入口智能体 |
| `planner_agent_name` | `str` | `"planner_agent"` | 负责生成计划的智能体名称 |
| `executor_agent_name` | `str` | `"executor_agent"` | 负责执行每一步的智能体名称 |
| `enable_replanner` | `bool` | `False` | 是否在每步执行后动态调整计划 |
| `max_replan_rounds` | `int` | `30` | 最大执行/重规划轮次 |
| `pre_plan_steps` | `list[str]` | `None` | 预设的计划步骤（跳过规划阶段） |
| `llm_model` | `str` | `"default_llm"` | 备用 LLM 模型名称 |

### 使用示例

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

## Reflexion 流

`Reflexion` 实现了"执行-反思-改进"的迭代工作流模式。它让一个工作智能体完成任务，然后由反思智能体评估结果并提供改进建议，循环迭代直到结果满意或达到最大轮次。

### 工作流程

1. **执行阶段** -- `worker_agent` 根据用户请求执行任务
2. **反思阶段** -- `reflexion_agent` 评估执行结果，判断是否满意
3. **迭代** -- 如果不满意，将反馈传递给 `worker_agent` 重新执行
4. **结束** -- 反思智能体认为结果满意或达到 `max_reflexion_rounds` 时输出最终结果

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | 必填 | 流的名称 |
| `is_master` | `bool` | `False` | 是否作为 MAS 的入口智能体 |
| `worker_agent` | `str` | 必填 | 执行任务的工作智能体名称 |
| `reflexion_agent` | `str` | 必填 | 评估结果的反思智能体名称 |
| `max_reflexion_rounds` | `int` | `3` | 最大反思迭代轮次 |

### 使用示例

```python
oxy.Reflexion(
    name="reflexion_flow",
    is_master=True,
    worker_agent="worker",
    reflexion_agent="evaluator",
    max_reflexion_rounds=3,
)
```

[上一章：创建工作流](./workflow.md)
[下一章：获取记忆和重新生成](./continue-exec.md)
[回到首页](../readme.md)

---

## 相关示例

- [PlanAndSolve流示例](../../examples/flows/plan_and_solve_demo.md) — 展示如何使用PlanAndSolve流进行任务规划与执行
- [Reflexion流示例](../../examples/flows/reflexion_agent_demo.md) — 展示如何使用Reflexion流进行反思与优化
