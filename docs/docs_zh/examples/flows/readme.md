# Flow 示例

本目录包含了 OxyGent 基于 Flow 的编排模式示例，通过反思循环和计划-求解管道等结构化多步流程来协调多个 Agent 协同工作。

---

## 示例列表

### Reflexion 流程

**文件:** `examples/flows/reflexion_agent_demo.py`

演示了 Reflexion 和 MathReflexion 流程模式，用于迭代式自我改进 Agent 输出。示例定义了两种反思工作流：（1）通用 `Reflexion` 流程，由 `worker_agent`（ReActAgent）生成初始答案，`reflexion_agent`（ChatAgent）评估质量。如果反思 Agent 判定答案"不满意"，会提取改进建议并反馈给工作 Agent 重新尝试，最多循环 `max_reflexion_rounds=3` 次。（2）专门用于数学问题的 `MathReflexion` 流程，使用 `math_expert_agent` 生成解题方案，`math_checker_agent` 验证正确性，采用类似的"通过/不通过"反馈循环。顶层的主 ReActAgent 根据问题类型将查询路由到相应的反思流程，使系统能够通过迭代质量改进来处理通用问题和数学专项任务。

**核心组件:**
- `Reflexion` -- 通用反思流程，可配置工作 Agent 和评估 Agent
- `MathReflexion` -- 数学专用反思流程
- `ReActAgent` -- 同时用作工作 Agent 和主路由 Agent
- `ChatAgent` -- 用作反思评估器、数学专家和数学检查器 Agent
- `HttpLLM` -- 底层语言模型，使用低温度参数以获得确定性输出

**[详细文档 →](./reflexion_agent_demo.md)**

---

### Plan-and-Solve 流程

**文件:** `examples/flows/plan_and_solve_demo.py`

演示了 PlanAndSolve 流程，将复杂任务的执行分离为规划阶段和逐步执行阶段。`planner_agent`（ChatAgent）为给定目标生成简洁的分步计划。`executor_agent`（ReActAgent）逐步执行每个步骤，可以访问多个专业化子 Agent（`time_agent`、`file_agent`、`math_agent`）以及一个讲笑话的 FunctionHub 工具。其中 `math_agent` 本身是一个 WorkflowAgent，具有自定义的 `func_workflow`，展示了如何访问短期记忆、发送中间消息、调用子 Agent 以及调用 MCP 工具（用于计算圆周率）。PlanAndSolve 流程协调整个循环：规划器创建计划，执行器处理每个步骤，可选的重新规划器可在执行过程中更新计划（本示例通过 `enable_replanner=False` 禁用了此功能）。配置通过 `config.json` 加载，时间、文件系统和数学的 MCP 工具通过 StdioMCPClient 连接。系统以一个结合了时间查询和文件写入的示例查询启动。

**核心组件:**
- `PlanAndSolve` -- 协调规划器和执行器 Agent 的编排流程
- `ChatAgent` -- 作为规划器 Agent
- `ReActAgent` -- 作为执行器和专业化子 Agent
- `WorkflowAgent` -- 数学 Agent 的自定义工作流，使用 `func_workflow`
- `FunctionHub` -- 笑话工具，展示了流程中自定义函数工具的使用
- `StdioMCPClient` -- 时间、文件系统和数学的 MCP 工具服务器
- `Config.load_from_json()` -- 从 JSON 文件加载配置

**[详细文档 →](./plan_and_solve_demo.md)**
