# OxyGent A2A Demo Guide

This document describes the adjusted directory structure under `examples/a2a`, the verification goals of each demo, and cross-framework interoperability demonstrations.

## 1. Root Directory (OxyGent Core Capabilities)

- `demo_a2a_oxygent_server.py`
- `demo_a2a_oxygent_client.py`
- `demo_a2a_oxygent_stream_client.py`
- `demo_a2a_oxygent_task_followup_client.py`

Capability Descriptions:
- `demo_a2a_oxygent_server.py`
  - Verifies OxyGent's minimal startup capability as an A2A Server
  - Exposes `/.well-known/agent.json` and A2A request endpoints externally
- `demo_a2a_oxygent_client.py`
  - Verifies OxyGent's minimal call chain as an A2A Client
  - Demonstrates single-turn requests and `context_id/task_id` round-trip
- `demo_a2a_oxygent_stream_client.py`
  - Verifies streaming consumption capability from OxyGent Client to OxyGent Server
  - Focus on observing incremental streaming output and final aggregated results
- `demo_a2a_oxygent_task_followup_client.py`
  - Verifies task follow-up capability using `context_id + reference_task_ids`
  - Demonstrates multi-turn contextual semantic correlation across tasks

## 2. `agentscope_interop/`

- `demo_agentscope_client_call_oxygent_server.py`
- `demo_oxygent_client_call_agentscope_server.py`

Capability Descriptions:
- `demo_agentscope_client_call_oxygent_server.py`
  - Verifies AgentScope Client -> OxyGent Server
- `demo_oxygent_client_call_agentscope_server.py`
  - Verifies OxyGent Client -> AgentScope Server

Core value of this directory:
- Validates OxyGent's protocol compatibility in heterogeneous framework environments
- Verifies that card parsing, streaming/non-streaming message paths are interoperable

## 3. `google_sdk_interop/`

- `demo_a2a_sdk_call_oxygent.py`
- `demo_a2a_sdk_stream_call_oxygent.py`

Capability Descriptions:
- `demo_a2a_sdk_call_oxygent.py`
  - Verifies standard A2A SDK calling OxyGent Server (non-streaming)
- `demo_a2a_sdk_stream_call_oxygent.py`
  - Verifies standard A2A SDK calling OxyGent Server (streaming)

Core value of this directory:
- Proves that OxyGent A2A Server is directly compatible with "framework-agnostic SDKs"

## 4. `langchain_interop/`

- `demo_langchain_a2a_server.py`
- `demo_langchain_client_call_oxygent_server.py`
- `demo_oxygent_client_call_langchain_server.py`

Capability Descriptions:
- `demo_langchain_a2a_server.py`
  - Starts a LangChain A2A Server-side example
- `demo_langchain_client_call_oxygent_server.py`
  - Verifies LangChain Client -> OxyGent Server
- `demo_oxygent_client_call_langchain_server.py`
  - Verifies OxyGent Client -> LangChain Server

## 5. `langgraph_interop/`

- `demo_langgraph_a2a_server.py`
- `demo_langgraph_client_call_oxygent_server.py`
- `demo_oxygent_client_call_langgraph_server.py`

Capability Descriptions:
- `demo_langgraph_a2a_server.py`
  - Starts a LangGraph A2A Server-side example
- `demo_langgraph_client_call_oxygent_server.py`
  - Verifies LangGraph Client -> OxyGent Server
- `demo_oxygent_client_call_langgraph_server.py`
  - Verifies OxyGent Client -> LangGraph Server

## 6. OxyGent A2A Capability Map (Perceivable Through Demos)

1. Core Protocol Capabilities:
- Agent Card exposure and parsing
- `message/send` request/response

2. Task and Session Capabilities:
- `context_id/task_id` passthrough
- `reference_task_ids` follow-up correlation
- `tasks/get` polling for terminal state (demonstrated in corresponding client demos)

3. Streaming Capabilities:
- `message/stream` event stream consumption
- Incremental output and final output aggregation

4. Cross-Framework Interoperability:
- Bidirectional communication between OxyGent and AgentScope / LangChain / LangGraph
- OxyGent Server can be called directly by a generic A2A SDK

[Next: A2A Design & Capabilities](./design.md)
[Back to Home](../readme.md)

---

## Related Examples

- [A2A Examples Overview](../../examples/a2a/readme.md) -- Complete list of A2A-related examples with instructions
