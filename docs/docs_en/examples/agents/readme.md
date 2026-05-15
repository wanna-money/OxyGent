# Agent Examples

This directory contains examples demonstrating various agent types and collaboration patterns in OxyGent. Each example is a self-contained script that can be run directly after setting the required environment variables.

## Examples

### Single Agent
**File:** `examples/agents/demo_single_agent.py`

Demonstrates the simplest possible agent setup: a single ChatAgent backed by an HttpLLM. It showcases the `func_process_input` hook (which appends extra instructions to the user query before it reaches the LLM) and the `func_format_output` hook (which prefixes the response with a label). Short memory is configured globally via `Config.set_agent_short_memory_size(7)` so the agent retains the last 7 turns of conversation context.

**Key Components:** HttpLLM, ChatAgent, func_process_input, func_format_output

**[Detailed Guide →](./demo_single_agent.md)**

---

### Chat Agent with Streaming
**File:** `examples/agents/demo_chat_agent_stream.py`

Shows how to enable streaming (token-by-token) output from a ChatAgent by setting `llm_params={"stream": True}` on the HttpLLM. Terminal display of streamed tokens is turned on with `Config.set_message_is_show_in_terminal(True)`. This is the minimal configuration needed to get real-time streaming responses through the web UI.

**Key Components:** HttpLLM (stream), ChatAgent

**[Detailed Guide →](./demo_chat_agent_stream.md)**

---

### ReAct Agent with Reflexion
**File:** `examples/agents/demo_react_agent.py`

Introduces the ReActAgent with a custom `func_reflexion` callback that validates the agent's output after each reasoning-action cycle. In this example, the reflexion function checks whether the output is a pure number using a regex; if not, it returns corrective feedback ("numbers only") that forces the agent to retry. This pattern is useful for enforcing structured output constraints.

**Key Components:** HttpLLM, ReActAgent, func_reflexion

**[Detailed Guide →](./demo_react_agent.md)**

---

### RAG Agent
**File:** `examples/agents/demo_rag_agent.py`

Demonstrates the RAGAgent, which supports retrieval-augmented generation through a custom `func_retrieve_knowledge` async function. The retrieved knowledge is injected into the agent's prompt via a named placeholder (`${knowledge}`). In this example the retrieval function returns a hardcoded value of Pi, but in production it would query a vector database or search engine.

**Key Components:** HttpLLM, RAGAgent, func_retrieve_knowledge, knowledge_placeholder

**[Detailed Guide →](./demo_rag_agent.md)**

---

### Workflow Agent
**File:** `examples/agents/demo_workflow_agent.py`

Shows the WorkflowAgent, which orchestrates sub-agents, LLMs, and tools from a Python workflow function. The workflow function receives an OxyRequest and can call any registered Oxy component by name using `oxy_request.call()`. This example chains a ChatAgent call, a direct LLM call, and an MCP tool call (calc_pi) to compute Pi to a requested number of decimal places. It also demonstrates accessing short memory and sending intermediate messages.

**Key Components:** HttpLLM, StdioMCPClient, ChatAgent, WorkflowAgent, func_workflow

**[Detailed Guide →](./demo_workflow_agent.md)**

---

### Hierarchical Multi-Agent
**File:** `examples/agents/demo_hierarchical_agents.py`

Builds a hierarchical multi-agent system where a master ReActAgent delegates tasks to specialized sub-agents. The master agent routes queries to either a `time_agent` (equipped with time MCP tools) or a `file_agent` (equipped with filesystem MCP tools). Each sub-agent is itself a ReActAgent with its own tool set. This pattern demonstrates how to decompose complex tasks across a tree of agents.

**Key Components:** HttpLLM, StdioMCPClient (x2), ReActAgent (x3)

**[Detailed Guide →](./demo_hierarchical_agents.md)**

---

### Heterogeneous Agents
**File:** `examples/agents/demo_heterogeneous_agents.py`

Demonstrates mixing different agent types under a single master agent. A ReActAgent serves as the master and delegates to a ChatAgent (`QA_agent` for general knowledge) and a WorkflowAgent (`time_agent` with a programmatic workflow for time queries). This shows that sub-agents do not need to be the same type -- you can freely combine ChatAgent, WorkflowAgent, ReActAgent, and others within one hierarchy.

**Key Components:** HttpLLM, StdioMCPClient, ReActAgent, ChatAgent, WorkflowAgent

**[Detailed Guide →](./demo_heterogeneous_agents.md)**

---

### Parallel Agent
**File:** `examples/agents/demo_parallel.py`

Demonstrates ParallelAgent, which dispatches a single query to multiple expert ChatAgents concurrently and aggregates their responses. Four domain-specific experts (technical architect, business analyst, risk manager, and legal advisor) each evaluate the same business proposal simultaneously. This pattern is ideal for multi-perspective analysis where independent evaluations are needed in parallel.

**Key Components:** HttpLLM, ChatAgent (x4), ParallelAgent

**[Detailed Guide →](./demo_parallel.md)**

---

### Mixture of Agents (MoA)
**File:** `examples/agents/demo_mixture_of_agents.py`

Implements the Mixture of Agents pattern using the `team_size` parameter. Setting `team_size=4` on a ChatAgent causes 4 parallel instances to process the same query concurrently, each producing an independent response. These responses are then automatically aggregated into a single final answer. This ensemble approach improves answer quality through diversity of reasoning, without requiring multiple distinct agent definitions.

**Key Components:** HttpLLM, ChatAgent (team_size=4)

**[Detailed Guide →](./demo_mixture_of_agents.md)**

---

### Plan-and-Solve Agent
**File:** `examples/agents/demo_plan_and_solve_agent.py`

Shows the PlanAndSolveAgent, a two-phase agent that separates planning from execution. A ChatAgent acts as the planner, generating and updating a step-by-step plan in JSON format. A ReActAgent acts as the executor, carrying out one step at a time using preset time and file tools. The PlanAndSolveAgent orchestrates the loop between planning and execution until the task is complete.

**Key Components:** HttpLLM, ChatAgent (planner), preset_tools (time_tools, file_tools), ReActAgent (executor), PlanAndSolveAgent

**[Detailed Guide →](./demo_plan_and_solve_agent.md)**

---

### Shell Use Agent
**File:** `examples/agents/demo_shell_use_agent.py`

Demonstrates ShellUseAgent, which connects to a remote host via SSH and executes shell commands autonomously to accomplish tasks. The agent is configured with SSH authentication info (hostname, port, username, password) and uses preset SSH tools. With `max_react_rounds=64` and `is_discard_react_memory=False`, it can perform long multi-step operations while retaining full context of previous commands and their outputs.

**Key Components:** HttpLLM, preset_tools.ssh_tools, ShellUseAgent, auth_info

**[Detailed Guide →](./demo_shell_use_agent.md)**

---

### Skill Agent
**File:** `examples/agents/demo_skill_agent.py`

Introduces the SkillAgent, which dynamically loads skill definitions from a directory (`./skills`). Skills are reusable, structured task templates that the agent can discover and invoke. The agent is also equipped with file viewing and shell command tools from preset_tools, enabling it to read skill files and execute commands as part of skill execution.

**Key Components:** HttpLLM, preset_tools (file_tools, shell_tools), SkillAgent, skills

**[Detailed Guide →](./demo_skill_agent.md)**

---

### Document Analysis Agent
**File:** `examples/agents/demo_document_analysis_agent.py`

Sets up a ReActAgent for document analysis using preset `document_tools`, which support processing and analyzing various document formats (PDF, Word, Excel, etc.). The HttpLLM is configured with streaming enabled for real-time output. This is a practical example of combining preset tool packs with a ReActAgent for domain-specific tasks.

**Key Components:** HttpLLM (stream), preset_tools.document_tools, ReActAgent

**[Detailed Guide →](./demo_document_analysis_agent.md)**

---

### Evaluate and Evolve (Batch Processing)
**File:** `examples/agents/demo_evaluate_and_evolve.py`

Demonstrates batch processing for SFT (Supervised Fine-Tuning) data quality review. Unlike other examples that start a web service, this one uses `mas.start_batch_processing()` to evaluate multiple data samples concurrently. The workflow retrieves LLM node data from Elasticsearch, sends each sample to a ChatAgent for quality evaluation against defined criteria, parses the JSON results, filters out low-quality samples, and writes the approved data to a JSONL file for training.

**Key Components:** HttpLLM, ChatAgent, batch_processing, Elasticsearch

**[Detailed Guide →](./demo_evaluate_and_evolve.md)**
