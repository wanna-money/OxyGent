# OxyGent A2A Design Overview and Capability Summary

This document is intended for open-source users, explaining the design philosophy, core capabilities, protocol mappings, and minimal upgrade approach of OxyGent A2A from scratch.

Main implementation code:
- A2A Server Gateway: `oxygent/transport/a2a/a2a_server_gateway.py`
- A2A Client Agent: `oxygent/oxy/agents/a2a_client_agent.py`

## 1. Design Philosophy

The core goal of OxyGent A2A is: **minimal changes to integrate A2A, maximum reuse of existing MAS capabilities**.

1. For the Server side:
- A2A is not treated as a new business Agent, but as a protocol gateway (Gateway)
- A2A requests are converted into internal MAS calls, and results are converted back into A2A responses

2. For the Client side:
- Provides `A2AClientAgent` based on `RemoteAgent`
- Automatically discovers service capabilities through Agent Card, unifying the send/stream/poll experience

3. For framework users:
- Supports both internal OxyGent inter-calls and interoperability with external A2A frameworks
- Maintains backward compatibility with legacy paths (e.g., `/messages/send`), reducing upgrade costs

## 2. Architecture Overview

### 2.1 Server (A2AServerGateway)

`A2AServerGateway` is responsible for:
- Card exposure: `/.well-known/agent.json`
- Protocol entry: JSON-RPC and compatible POST endpoints
- Request conversion: A2A -> MAS payload
- Result conversion: MAS output/SSE -> A2A Message/Task structure

It is essentially a "protocol adaptation layer" -- business execution still happens within the target Agent in MAS.

### 2.2 Client (A2AClientAgent)

`A2AClientAgent` is responsible for:
- Card discovery (`server_url` or `agent_card_url`)
- Non-streaming: `message/send`
- Streaming: `message/stream`
- Task state: `tasks/get` polling, `cancel`, `resubscribe`
- Session state: `context_id/task_id/reference_task_ids` passing and reuse

## 3. Core Capabilities

### 3.1 Protocol Capabilities

Supported:
1. `message/send`
2. `message/stream`
3. `tasks/get`
4. `tasks/cancel`
5. `tasks/resubscribe`
6. Agent Card discovery and parsing

Compatibility features:
1. JSON-RPC method (standard A2A calls)
2. Compatible with legacy routes (e.g., `/messages/send`)
3. Unified POST entry dispatched by `method/action`

### 3.2 Streaming and Non-Streaming

1. The Server side supports both `send` and `stream`  
2. `stream` bridges to the A2A event stream via the MAS SSE pipeline  
3. On the Client side, streaming or non-streaming is determined by parameters, with no business code changes required

### 3.3 Multi-Task and Context Management

1. A `task` is an independent execution unit  
2. `context_id` represents the session context  
3. Subsequent tasks are associated with previous tasks through `reference_task_ids`  
4. The Server maps `referenceTaskIds[-1]` to MAS's `from_trace_id`, enabling context-based multi-turn correlation

## 4. Key Mappings Between A2A and MAS

1. `contextId` -> `group_id`  
2. `taskId` -> Task execution identifier (also used for task lifecycle management)  
3. `referenceTaskIds[-1]` -> `from_trace_id`  
4. Streaming events -> Incremental SSE from MAS's `_process_redis_messages`

## 5. Minimal Upgrade Approach (For Existing OxyGent Projects)

Simply enable A2A when starting MAS:

```python
async with MAS(
    oxy_space=oxy_space,
    enable_a2a_server=True,
    a2a_base_path="/a2a",
) as mas:
    await mas.start_web_service()
```

This automatically assembles the A2A Router and exposes:
- `GET /.well-known/agent.json`
- A2A POST endpoints (including stream/non-stream/task paths)

## 6. Open-Source Maintainability Design

The Server has been split by transport layer into `transport/a2a`:
- `a2a_server_gateway.py`: Gateway main flow and routing
- `a2a_card.py`: Card/skills construction
- `a2a_mapper.py`: Field extraction and request mapping
- `a2a_protocol.py`: A2A response structure construction
- `a2a_store.py`: Task/context runtime state storage

This separation makes protocol layer evolution, issue diagnosis, and test isolation clearer.

## 7. Current Boundaries and Notes

1. Current capabilities focus on "protocol interoperability and engineering usability"  
2. Distributed persistence/cross-process consistency of tasks can be further enhanced as needed  
3. Streaming effectiveness depends on whether the upstream model/service produces genuine incremental output

## 8. Summary

OxyGent A2A now provides the following practical capabilities:
1. Client + Server dual-endpoint capabilities
2. Both streaming and non-streaming paths
3. Context correlation in multi-task scenarios
4. Legacy path compatibility and minimal upgrade integration
5. Cross-framework interoperability foundation (AgentScope/LangChain/LangGraph)

For existing OxyGent users, A2A integration can be quickly deployed through "minimal configuration changes."

---

## Related Examples

- [A2A Server Example](../../examples/a2a/demo_a2a_oxygent_server.md) -- Demonstrates how to start an OxyGent A2A Server

---

[Previous: A2A Quick Start](./demo-guide.md)
[Back to Home](../readme.md)
