"""LangGraph-style client -> OxyGent A2A server demo.

Prerequisite:
    PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py

Run:
    PYTHONPATH=. python examples/agents/demo_langgraph_client_call_oxygent_server.py
"""

import asyncio
import json
from typing import TypedDict

import httpx

try:
    from langgraph.graph import END, StateGraph
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "Missing dependency `langgraph`. Install it first, e.g.:\n"
        "pip install langgraph"
    ) from e


BASE_URL = "http://127.0.0.1:8090/a2a"


class GraphState(TypedDict):
    query: str
    answer: str
    context_id: str
    task_id: str
    raw_task: dict


def extract_task_text(task: dict) -> str:
    status_msg = (((task or {}).get("status") or {}).get("message") or {})
    parts = status_msg.get("parts", [])
    if parts and isinstance(parts[0], dict):
        txt = parts[0].get("text")
        if isinstance(txt, str) and txt:
            return txt
    artifacts = (task or {}).get("artifacts", [])
    if artifacts and isinstance(artifacts[0], dict):
        aparts = artifacts[0].get("parts", [])
        if aparts and isinstance(aparts[0], dict):
            txt = aparts[0].get("text")
            if isinstance(txt, str):
                return txt
    return ""


async def send_a2a(query: str, context_id: str = "", task_id: str = "") -> tuple[dict, str]:
    message = {
        "kind": "message",
        "messageId": "lg-" + query[:8],
        "role": "user",
        "parts": [{"kind": "text", "text": query}],
    }
    if context_id:
        message["contextId"] = context_id
    if task_id:
        message["taskId"] = task_id

    payload = {
        "jsonrpc": "2.0",
        "id": "req-" + query[:8],
        "method": "message/send",
        "params": {"message": message},
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(BASE_URL, json=payload)
        resp.raise_for_status()
        body = resp.json()
    task = body.get("result", {})
    return task, extract_task_text(task)


async def call_node(state: GraphState) -> GraphState:
    task, answer = await send_a2a(
        state["query"], context_id=state.get("context_id", ""), task_id=state.get("task_id", "")
    )
    return {
        "query": state["query"],
        "answer": answer,
        "context_id": str(task.get("contextId") or ""),
        "task_id": str(task.get("id") or ""),
        "raw_task": task,
    }


builder = StateGraph(GraphState)
builder.add_node("call", call_node)
builder.set_entry_point("call")
builder.add_edge("call", END)
graph = builder.compile()


async def main():
    turn1 = await graph.ainvoke(
        {"query": "哪个数字最大，直接回答：1、5、7", "answer": "", "context_id": "", "task_id": "", "raw_task": {}}
    )
    print("\n[turn1 raw]", json.dumps(turn1["raw_task"], ensure_ascii=False))
    print("[turn1]", turn1["answer"])


if __name__ == "__main__":
    asyncio.run(main())

