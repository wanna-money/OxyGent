# Architecture Overview

This document explains how OxyGent is structured internally. Understanding the architecture helps you make better design decisions when building multi-agent systems.

---

## Oxy: The Universal Building Block

Everything in OxyGent -- agents, tools, LLMs, flows -- inherits from a single abstract base class called `Oxy`. Each Oxy component has a `name`, follows the same execution lifecycle, and can be wired together by name.

When an Oxy component is called, the following lifecycle hooks execute in order:

```
Entry point: __call__()
│
├─ _pre_process()         Pre-processing: validate and transform input
├─ _pre_log()             Pre-logging: record the incoming request
├─ _pre_save_data()       Pre-persistence: save the request to the database
├─ _format_input()        Format input: invoke the func_format_input hook
├─ _pre_send_message()    Pre-message: push status to the frontend
│
├─ _before_execute()      Before-execute hook: final preparation
├─ _execute()             Core execution (abstract, implemented by subclasses)
│   └─ Supports retries: retries count, delay interval
├─ _after_execute()       After-execute hook: post-process the result
│
├─ _post_process()        Post-processing: transform the output
├─ _post_log()            Post-logging: record the response
├─ _post_save_data()      Post-persistence: save the response to the database
├─ _format_output()       Format output: invoke the func_format_output hook
└─ _post_send_message()   Post-message: push the result to the frontend
```

Every hook can be customized via constructor parameters. For example, `func_process_input` transforms the request during `_pre_process`, and `func_format_output` formats the response during `_format_output`.

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

The following diagram shows the complete flow of a user request from entering MAS to returning the result:

```
User
 |
 v
MAS.chat_with_agent(payload)
 |
 +-- Create OxyRequest (trace_id, query, shared_data)
 |
 v
Master Agent.__call__(oxy_request)
 |
 +-- _pre_process  -> _pre_log -> _pre_save_data
 +-- _format_input -> _pre_send_message
 |
 +-- _execute()    <-- ReActAgent's reason-act loop
 |   |
 |   +-- LLM reasoning -> "I need to call time_agent"
 |   |
 |   +-- Call sub-agent time_agent.__call__(sub_request)
 |   |   +-- time_agent._execute()
 |   |   |   +-- LLM reasoning -> "Call get_time tool"
 |   |   |   +-- Tool execution -> "2024-01-01 12:00:00"
 |   |   |   +-- LLM summarize -> "The current time is..."
 |   |   +-- Return OxyResponse
 |   |
 |   +-- LLM summarize -> Final answer
 |
 +-- _post_process -> _post_log -> _post_save_data
 +-- _format_output -> _post_send_message
 |
 v
OxyResponse (output, state, extra)
 |
 v
User
```

### Core Data Structures

| Structure | Description |
|-----------|-------------|
| `OxyRequest` | Request object. Carries `trace_id` (tracing identifier), `caller`/`callee` (caller/callee names), `query` (query content), `shared_data` (shared data) |
| `OxyResponse` | Response object. Carries `output` (output text), `state` (`OxyState` enum), `extra` (additional data) |
| `trace_id` | Unique tracing identifier that spans the entire call chain |

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

`MAS` is the runtime container that manages the full lifecycle of all components.

```python
async with MAS(oxy_space=oxy_space) as mas:
    # MAS initialization is complete at this point
    await mas.start_web_service()
# On exiting the async with block, MAS automatically cleans up resources
```

### Initialization Phase (`__aenter__`)

1. **Register components**: Register all components from `oxy_space` into the `oxy_name_to_oxy` dictionary.
2. **Connect databases**: Initialize Elasticsearch, Redis, and Vearch connections (if configured).
3. **Resolve references**: Resolve string name references to actual objects (LLMs, tools, sub-agents).
4. **Initialize MCP**: Start all MCP clients and connect to external tool servers.
5. **Build organization tree**: Establish the hierarchical relationships between agents (`agent_organization`).
6. **Determine entry point**: Find the agent with `is_master=True` as the `master_agent_name`.

### Run Phase

MAS provides multiple run modes (see "Deployment Modes" below). All modes ultimately route requests to the master agent through `chat_with_agent()`.

### Cleanup Phase (`__aexit__`)

Automatically closes database connections, MCP clients, background tasks, and other resources.

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
    querys=["Q1", "Q2", "Q3"],
)
```

Process multiple queries concurrently.

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

## Summary

| Concept | Description |
|---------|-------------|
| Oxy | Universal abstract base class that defines the execution lifecycle |
| Name reference | Components reference each other by `name` strings |
| oxy_space | The list where components are declared |
| MAS | Runtime container that manages registration, initialization, and routing |
| OxyRequest / OxyResponse | Request and response data structures |
| trace_id | Call-chain tracing identifier |

---

[Previous: Concepts Overview](./overview.md)
[Next: Configuration](./config.md)
[Back to Home](../readme.md)
