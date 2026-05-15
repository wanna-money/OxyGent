# How to Choose an Agent?

OxyGent provides many types of preset agents. These agents are sufficient to help you build basic MAS (Multi-Agent Systems). Here is a brief introduction:

## `oxy.ChatAgent`

`oxy.ChatAgent` is the most basic conversational agent, with functionality roughly equivalent to the underlying LLM. It supports multi-turn conversation memory, custom prompt configuration, and passing custom parameters to the LLM, making it the go-to choice for simple dialogue scenarios or as a building block in larger systems.

**Use cases:** Q&A systems, customer service bots, personal assistants, content generation (copywriting/summarization), prototyping and proof-of-concept.

**Not suitable for:** Tasks requiring complex reasoning/planning, multi-step workflows, or parallel task processing -- use ReActAgent, WorkflowAgent, or ParallelAgent instead.

| Parameter           | Type  | Default                          | Description              |
|---------------------|-------|----------------------------------|--------------------------|
| `name`              | str   | Required                         | Agent name               |
| `desc`              | str   | Required                         | Agent description        |
| `llm_model`         | str   | Required                         | LLM model identifier     |
| `prompt`            | str   | `"You are a helpful assistant."` | System prompt            |
| `short_memory_size` | int   | Inherited from LocalAgent        | Short-term memory size   |

```python
oxy.ChatAgent(
    name="planner_agent",
    desc="An agent capable of making plans",
    llm_model="default_llm",
    prompt="""
        For a given goal, create a simple and step-by-step executable plan. \
        The plan should be concise, with each step being an independent and complete functional module—not an atomic function—to avoid over-fragmentation. \
        The plan should consist of independent tasks that, if executed correctly, will lead to the correct answer. \
        Ensure that each step is actionable and includes all necessary information for execution. \
        The result of the final step should be the final answer. Make sure each step contains all the information required for its execution. \
        Do not add any redundant steps, and do not skip any necessary steps.
    """.strip(),
)
```

## `oxy.WorkflowAgent`

Built on top of Chat with added [workflow](../advanced/workflow.md) support, this agent allows you to customize the internal process flow.

```python
oxy.WorkflowAgent(
    name='search_agent',
    desc='A tool that can query data',
    sub_agents=['ner_agent', 'nen_agent'],
    func_workflow=data_workflow,
    llm_model='default_llm',
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Agent name |
| `desc` | str | `""` | Agent description |
| `func_workflow` | Callable | `None` | Custom workflow function |
| `sub_agents` | list[str] | `[]` | Names of callable sub-agents |

## `oxy.ReActAgent`

An agent that supports [planning, execution, observation, and error-correction retry](https://www.promptingguide.ai/zh/techniques/react), suitable for complex tasks and commonly used as a master_agent.

```python
oxy.ReActAgent(
    name="master_agent",
    sub_agents=["knowledge_agent", "find_agent", "search_agent"],
    is_master=True,
    llm_model="default_llm",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Agent name |
| `desc` | str | `""` | Agent description |
| `llm_model` | str | `"default_llm"` | LLM model name |
| `max_react_rounds` | int | `16` | Maximum reasoning-action rounds |
| `trust_mode` | bool | `False` | Whether to enable Trust Mode for outputting metadata |
| `is_discard_react_memory` | bool | `True` | Whether to clear reasoning memory on each new query |
| `func_parse_llm_response` | Callable | `None` | Custom LLM output parsing function |
| `func_reflexion` | Callable | `None` | Custom reflexion function |

ReActAgent includes some unique configurable parameters, including:

- `max_react_rounds: int`: Maximum number of ReAct rounds
- `trust_mode: bool`: Whether to [provide response metadata](../advanced/trust-mode.md)
- `func_parse_llm_response: Optional[Callable[[str], LLMResponse]]`: [Handle LLM output](../advanced/handle-output.md)

## `oxy.SSEOxyGent`

An agent that supports [distributed](../multi-agent/distributed.md) deployment.

```python
oxy.SSEOxyGent(
    name='math_agent',
    desc='A tool that can query pi',
    server_url='http://127.0.0.1:8081'
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Agent name |
| `desc` | str | `""` | Agent description |
| `server_url` | str | Required | URL of the remote MAS |

## `oxy.ParallelAgent`

An agent that supports [parallel](../multi-agent/parallel.md) execution.

```python
oxy.ParallelAgent(
    name="analyzer",
    desc="A tool that analyze markdown document",
    permitted_tool_name_list=["text_summarizer", "data_analyser", "document_checker"]
),
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Agent name |
| `desc` | str | `""` | Agent description |
| `permitted_tool_name_list` | list[str] | `[]` | List of agent/tool names to execute in parallel |

## `oxy.PlanAndSolveAgent`

A two-stage agent that separates planning from execution. PlanAndSolveAgent coordinates a planner (typically a ChatAgent) and a solver (typically a ReActAgent). The planner generates a step-by-step plan in JSON format, and the solver completes each step sequentially.

```python
oxy.PlanAndSolveAgent(
    name="master_agent",
    is_master=True,
    planner="planner_agent",
    solver="solver_agent",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Agent name |
| `planner` | str | `"planner_agent"` | Planner agent name |
| `solver` | str | `"executor_agent"` | Solver agent name |
| `max_replan_rounds` | int | `30` | Maximum re-planning rounds |

## `oxy.RAGAgent`

An agent that supports Retrieval-Augmented Generation (RAG). It retrieves external knowledge through a custom `func_retrieve_knowledge` async function and injects the retrieval results into the agent's prompt using named placeholders (e.g., `${knowledge}`).

```python
async def my_retrieve(oxy_request):
    # Implement your retrieval logic here, e.g., query a vector database
    return "Retrieved knowledge content"

oxy.RAGAgent(
    name="rag_agent",
    desc="A knowledge-augmented agent",
    func_retrieve_knowledge=my_retrieve,
    knowledge_placeholder="knowledge",
    prompt="Based on the following knowledge: ${knowledge}\nPlease answer the user's question.",
    llm_model="default_llm",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Agent name |
| `desc` | str | Required | Agent description |
| `func_retrieve_knowledge` | Callable | Required | Knowledge retrieval function |
| `knowledge_placeholder` | str | `"knowledge"` | Name of the knowledge placeholder in the prompt |
| `prompt` | str | Required | Prompt containing the `${knowledge}` placeholder |

## `oxy.ShellUseAgent`

An agent that connects to remote hosts via SSH and autonomously executes shell commands to complete tasks. Suitable for server operations and maintenance, automated deployment, and similar scenarios.

```python
oxy.ShellUseAgent(
    name="shell_agent",
    desc="An agent that can execute shell commands on remote hosts",
    tools=["ssh_tools"],
    max_react_rounds=64,
    is_discard_react_memory=False,
    auth_info={
        "hostname": "your_host",
        "port": 22,
        "username": "your_username",
        "password": "your_password",
    },
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Agent name |
| `desc` | str | `""` | Agent description |
| `auth_info` | dict | `{}` | SSH connection parameters (hostname, port, username, password) |
| `max_react_rounds` | int | `64` | Maximum reasoning-action rounds |

## `oxy.SkillAgent`

An agent that can dynamically load skill definitions from a directory (e.g., `./skills`). Skills are reusable structured task templates that the agent can automatically discover and invoke.

```python
oxy.SkillAgent(
    name="skill_agent",
    desc="An agent that can discover and execute skills",
    tools=["file_tools", "shell_tools"],
    llm_model="default_llm",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Agent name |
| `desc` | str | `""` | Agent description |
| `skills` | list[str] | `None` | List of skill directory paths |

[Previous: Preset Prompts](./select-prompt.md)
[Next: Register a Tool](../tools/register-tool.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Single Agent Example](../../examples/agents/demo_single_agent.md) -- The simplest ChatAgent configuration
- [ReAct Agent Example](../../examples/agents/demo_react_agent.md) -- ReActAgent with reflection mechanism
- [Workflow Agent Example](../../examples/agents/demo_workflow_agent.md) -- WorkflowAgent orchestrating sub-agents
- [Parallel Agent Example](../../examples/agents/demo_parallel.md) -- ParallelAgent for parallel execution
- [Plan-and-Solve Agent Example](../../examples/agents/demo_plan_and_solve_agent.md) -- PlanAndSolveAgent's two-stage planning and execution
- [RAG Agent Example](../../examples/agents/demo_rag_agent.md) -- Retrieval-Augmented Generation Agent
- [Shell Use Agent Example](../../examples/agents/demo_shell_use_agent.md) -- ShellUseAgent for remote command execution
- [Skill Agent Example](../../examples/agents/demo_skill_agent.md) -- SkillAgent for dynamic skill loading
- [Hierarchical Multi-Agent Example](../../examples/agents/demo_hierarchical_agents.md) -- Master-subordinate Agent hierarchy
- [Heterogeneous Agent Collaboration Example](../../examples/agents/demo_heterogeneous_agents.md) -- Mixing different types of Agents
- [Distributed Agent Example](../../examples/distributed/app_master_agent.md) -- SSEOxyGent distributed deployment
