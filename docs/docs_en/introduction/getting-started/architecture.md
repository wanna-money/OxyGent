# Architecture Overview

This document explains how OxyGent is structured internally. Understanding the architecture helps you make better design decisions when building multi-agent systems.

---

## Oxy: The Universal Building Block

Everything in OxyGent -- agents, tools, LLMs, flows -- inherits from a single abstract base class called `Oxy`. Each Oxy component has a `name`, follows the same execution lifecycle, and can be wired together by name.

The execution lifecycle runs in this order:

```
_pre_process
  -> _pre_log
  -> _pre_save_data
  -> _format_input
  -> _pre_send_message
    -> _before_execute
    -> _execute          <-- abstract, each subclass implements this
    -> _after_execute
  -> _post_process
  -> _post_log
  -> _post_save_data
  -> _format_output
  -> _post_send_message
```

You rarely need to override the full lifecycle. Most of the time, you implement `_execute()` and optionally hook into `_format_input` / `_format_output` for pre/post-processing.

---

## Class Hierarchy

```
Oxy (base_oxy.py)
|
+-- BaseTool (base_tool.py)
|   +-- FunctionHub           Python function collections
|   +-- FunctionTool          Individual function wrapper
|   +-- HttpTool              HTTP API wrapper
|   +-- BaseMCPClient
|       +-- StdioMCPClient    MCP via stdio transport
|       +-- SSEMCPClient      MCP via SSE transport
|       +-- StreamableMCPClient  MCP via streamable transport
|
+-- BaseLLM (llms/base_llm.py)
|   +-- HttpLLM               Cloud models via HTTP API
|   +-- OpenAILLM             OpenAI SDK-compatible models
|   +-- LocalLLM              HuggingFace local models
|   +-- MockLLM               Mock model for testing
|
+-- BaseFlow (base_flow.py)
    +-- BaseAgent (agents/base_agent.py)
    |   +-- LocalAgent
    |   |   +-- ChatAgent           Single LLM call, no tools
    |   |   +-- ReActAgent          Reason-act loop with tools
    |   |   |   +-- ShellUseAgent   SSH remote commands
    |   |   |   +-- SkillAgent      Dynamically loaded skills
    |   |   +-- ParallelAgent       Concurrent sub-task execution
    |   |   +-- WorkflowAgent       Custom step sequences
    |   |   +-- PlanAndSolveAgent   Plan first, then execute
    |   |   +-- RAGAgent            Retrieval-augmented generation
    |   +-- RemoteAgent
    |       +-- SSEOxyGent          Cross-process distributed agents
    |       +-- A2AClientAgent      A2A protocol client
    |
    +-- Workflow                User-defined step sequences
    +-- PlanAndSolve            Plan-and-solve flow
    +-- Reflexion               Self-reflection flow
    +-- MathReflexion           Math-specific reflection
```

---

## Request/Response Flow

Every interaction follows this path:

```
User Query
    |
    v
MAS.chat_with_agent(payload)
    |
    v
Master Agent (is_master=True)
    |
    +----> LLM call (reasoning)
    |
    +----> Tool call?  -----> Tool._execute() -----> Observation
    |                                                     |
    +----> Sub-agent call? -> Sub-Agent._execute() ------+
    |                                                     |
    +<-------------- Result back to master <--------------+
    |
    v
OxyResponse (output, state, extra)
    |
    v
User receives answer
```

The `OxyRequest` carries the query, trace ID, caller/callee names, shared data, and arguments. The `OxyResponse` carries the output text, execution state (`OxyState`), and any extra structured data.

Each call is tracked by a `trace_id`. Conversation history is linked across turns using `from_trace_id`, enabling multi-turn context.

---

## Component Wiring

Components reference each other **by string name**, not by Python object reference. This is a deliberate design choice:

```python
oxy_space = [
    oxy.HttpLLM(name="gpt4", ...),
    oxy.ReActAgent(
        name="agent_a",
        llm_model="gpt4",          # string reference to the LLM
        tools=["calculator"],       # string reference to the tool
        sub_agents=["agent_b"],     # string reference to another agent
    ),
    oxy.ChatAgent(name="agent_b", llm_model="gpt4"),
]
```

When `MAS` starts up, it:
1. Registers each component into `oxy_name_to_oxy` (a name-to-instance dict).
2. Resolves all string references to actual object references.
3. Builds the agent organization tree.

This means you can define components in any order, and you can serialize/deserialize component configurations easily (since names are just strings).

---

## MAS Lifecycle

`MAS` is the runtime container. It manages the lifecycle of all components:

```python
async with MAS(oxy_space=oxy_space) as mas:
    # At this point:
    # 1. All components are registered in oxy_name_to_oxy
    # 2. Agent organization tree is built
    # 3. DB connections (ES, Redis) are initialized
    # 4. MCP tool servers are started
    # 5. The system is ready to serve

    await mas.start_web_service()

# On exit:
# - MCP connections are closed
# - DB connections are cleaned up
# - Resources are released
```

The `async with` context manager handles setup and teardown automatically. Each component's `init()` method is called during setup, and `cleanup()` is called on exit.

---

## Deployment Modes

MAS supports four ways to run:

### Web Service (FastAPI + SSE)

```python
await mas.start_web_service(port=8080)
```

Starts a FastAPI server with:
- `POST /chat` -- synchronous chat
- `POST /sse/chat` -- SSE streaming chat
- `POST /async/chat` -- async chat with polling
- `GET /get_organization` -- agent tree structure
- Built-in web UI at the root URL

### CLI Mode

```python
await mas.start_cli_mode(first_query="Hello")
```

Interactive REPL in the terminal. Type queries, get responses. Type `reset` to start a new session.

### Batch Processing

```python
await mas.start_batch_processing(
    inputs=[{"query": "Q1"}, {"query": "Q2"}, ...],
    concurrency=4,
)
```

Process multiple inputs concurrently with configurable parallelism.

### Programmatic

```python
response = await mas.chat_with_agent(payload={"query": "Hello"})
print(response.output)
```

Direct function call for embedding OxyGent into larger applications.

---

## Storage Layer

OxyGent uses an optional storage layer for persistence:

| Service | Purpose | Fallback |
|---------|---------|----------|
| Elasticsearch | Traces, messages, prompts, ratings | `LocalEs` (file-based) or `MemoryEs` (in-memory) |
| Redis | SSE message queuing between backend and frontend | `LocalRedis` (in-memory) |
| Vearch | Vector DB for tool retrieval | Optional, not required |

All storage is optional. Without external databases, OxyGent uses local fallbacks automatically. You can run a complete multi-agent system with zero infrastructure dependencies.

---

[Previous: Quickstart](./quickstart.md)
[Back to Home](../readme.md)
