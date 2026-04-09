# OxyGent Agent-to-Agent (A2A) Examples

`A2A` in OxyGent provides both:
- an **A2A Server Gateway** (expose MAS as an A2A-compatible server)
- an **A2A Client Agent** (call external A2A servers from OxyGent)

This folder demonstrates:
1. OxyGent basic A2A server/client usage
2. streaming and multi-task follow-up patterns
3. interoperability with AgentScope, LangChain, LangGraph, and the A2A SDK

Related deep-dive docs:
- [Design and capabilities (CN)](../../docs/docs_zh/a2a_design_and_capabilities.md)
- [Demo guide (CN)](../../docs/docs_zh/a2a_demo_guide.md)

> Note  
> A2A support is practical and actively evolving. Some advanced protocol features are intentionally simplified in current examples.

## Directory Layout

```text
examples/a2a
├── demo_a2a_oxygent_server.py
├── demo_a2a_oxygent_client.py
├── demo_a2a_oxygent_stream_client.py
├── demo_a2a_oxygent_task_followup_client.py
├── agentscope_interop
│   ├── demo_agentscope_a2a_server.py
│   ├── demo_agentscope_client_call_oxygent_server.py
│   └── demo_oxygent_client_call_agentscope_server.py
├── google_sdk_interop
│   ├── demo_a2a_sdk_call_oxygent.py
│   └── demo_a2a_sdk_stream_call_oxygent.py
├── langchain_interop
│   ├── demo_langchain_a2a_server.py
│   ├── demo_langchain_client_call_oxygent_server.py
│   └── demo_oxygent_client_call_langchain_server.py
├── langgraph_interop
│   ├── demo_langgraph_a2a_server.py
│   ├── demo_langgraph_client_call_oxygent_server.py
│   └── demo_oxygent_client_call_langgraph_server.py
├── other
└── DEMO_STRUCTURE.md
```

## Quick Start

Start OxyGent A2A server:

```bash
PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py
```

Then run a basic OxyGent client call:

```bash
PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_client.py
```

## Recommended Run Order

1. OxyGent basics:
   - `demo_a2a_oxygent_server.py`
   - `demo_a2a_oxygent_client.py`
   - `demo_a2a_oxygent_stream_client.py`
   - `demo_a2a_oxygent_task_followup_client.py`
2. SDK interop:
   - `google_sdk_interop/demo_a2a_sdk_call_oxygent.py`
   - `google_sdk_interop/demo_a2a_sdk_stream_call_oxygent.py`
3. Cross-framework interop:
   - `agentscope_interop/*`
   - `langchain_interop/*`
   - `langgraph_interop/*`

## Core A2A Capabilities in OxyGent

### Server side

1. Auto-mount A2A router from MAS startup config:
   - `enable_a2a_server=True`
   - `a2a_base_path="/a2a"`
2. Agent Card discovery endpoint:
   - `GET /.well-known/agent.json`
3. Supports non-stream and stream:
   - `message/send`
   - `message/stream`
4. Task lifecycle endpoints:
   - `tasks/get`
   - `tasks/cancel`
   - `tasks/resubscribe`
5. Compatibility paths:
   - legacy-style routes like `/messages/send`
6. Context/task mapping:
   - `contextId -> group_id`
   - `taskId -> task execution identity`
   - `referenceTaskIds[-1] -> from_trace_id`

### Client side (`A2AClientAgent`)

1. Agent Card discovery from `server_url` or `agent_card_url`
2. Non-stream and stream calls
3. Optional task polling (`tasks/get`) until terminal state
4. Session reuse with:
   - `context_id`
   - `task_id`
   - `reference_task_ids`

## Supported Patterns Demonstrated

1. Basic single-turn chat over A2A
2. Streaming output consumption
3. Multi-task follow-up in a shared context
4. OxyGent ↔ AgentScope interoperability
5. OxyGent ↔ LangChain interoperability
6. OxyGent ↔ LangGraph interoperability
7. Generic A2A SDK → OxyGent server calls

## Current Scope / Limitations

1. Demos focus on chatbot-like request/response patterns.
2. Real-time steering/interruption is not a primary path in current examples.
3. Advanced structured agentic outputs are not the main compatibility target.
4. Task/context persistence strategy can be further enhanced for large-scale distributed scenarios.
5. Streaming quality depends on upstream model/service behavior (true incremental output vs pseudo-stream).

## Minimal MAS Upgrade to Enable A2A Server

```python
async with MAS(
    oxy_space=oxy_space,
    enable_a2a_server=True,
    a2a_base_path="/a2a",
) as mas:
    await mas.start_web_service()
```

This is the intended low-friction migration path for existing OxyGent projects.
