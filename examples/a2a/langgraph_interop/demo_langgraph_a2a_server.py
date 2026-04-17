"""Minimal LangGraph-based A2A server demo.

Run:
    PYTHONPATH=. python examples/agents/demo_langgraph_a2a_server.py
"""

import asyncio
import json
from typing import Any, TypedDict
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse

try:
    from langgraph.graph import END, StateGraph
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "Missing dependency `langgraph`. Install it first, e.g.:\n"
        "pip install langgraph"
    ) from e


APP_HOST = "127.0.0.1"
APP_PORT = 8102
BASE_PATH = "/a2a"

TASKS: dict[str, dict[str, Any]] = {}


class GraphState(TypedDict):
    query: str
    answer: str


def extract_text(payload: dict[str, Any]) -> str:
    message = payload.get("message", {}) if isinstance(payload, dict) else {}
    parts = message.get("parts", []) if isinstance(message, dict) else []
    for part in parts:
        if isinstance(part, dict) and part.get("kind") == "text":
            return str(part.get("text", ""))
    return str(payload.get("query") or payload.get("text") or "")


def build_message(text: str, task_id: str, context_id: str) -> dict[str, Any]:
    return {
        "kind": "message",
        "messageId": str(uuid4()),
        "role": "agent",
        "parts": [{"kind": "text", "text": text}],
        "taskId": task_id,
        "contextId": context_id,
    }


def build_task(text: str, task_id: str, context_id: str) -> dict[str, Any]:
    return {
        "kind": "task",
        "id": task_id,
        "contextId": context_id,
        "status": {"state": "completed", "message": build_message(text, task_id, context_id)},
        "artifacts": [
            {
                "artifactId": str(uuid4()),
                "name": "final_answer",
                "parts": [{"kind": "text", "text": text}],
            }
        ],
        "metadata": {"framework": "langgraph"},
    }


def answer_node(state: GraphState) -> GraphState:
    return {"query": state["query"], "answer": f"[LangGraph Server] {state['query']}"}


builder = StateGraph(GraphState)
builder.add_node("answer", answer_node)
builder.set_entry_point("answer")
builder.add_edge("answer", END)
graph = builder.compile()

app = FastAPI()


@app.get(f"{BASE_PATH}/.well-known/agent.json")
async def card():
    return {
        "name": "langgraph_a2a_server",
        "description": "LangGraph powered A2A demo server",
        "version": "0.1.0",
        "url": f"http://{APP_HOST}:{APP_PORT}{BASE_PATH}",
        "capabilities": {
            "streaming": True,
            "task_control": True,
            "pushNotifications": False,
        },
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "skills": [
            {
                "id": "chat",
                "name": "chat",
                "description": "Chat with LangGraph demo server",
                "tags": ["langgraph", "a2a", "chat"],
                "inputModes": ["text/plain"],
                "outputModes": ["text/plain"],
            }
        ],
    }


@app.post(BASE_PATH)
@app.post(f"{BASE_PATH}/")
async def unified(request: Request):
    payload = await request.json()
    req_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params", {}) if isinstance(payload, dict) else {}

    if method == "message/send":
        task_id = (
            params.get("message", {}).get("taskId")
            or params.get("message", {}).get("task_id")
            or str(uuid4())
        )
        context_id = (
            params.get("message", {}).get("contextId")
            or params.get("message", {}).get("context_id")
            or str(uuid4())
        )
        text = extract_text(params)
        answer = graph.invoke({"query": text, "answer": ""}).get("answer", "")
        task = build_task(answer, task_id, context_id)
        TASKS[task_id] = task
        return {"jsonrpc": "2.0", "id": req_id, "result": task}

    if method == "message/stream":
        task_id = (
            params.get("message", {}).get("taskId")
            or params.get("message", {}).get("task_id")
            or str(uuid4())
        )
        context_id = (
            params.get("message", {}).get("contextId")
            or params.get("message", {}).get("context_id")
            or str(uuid4())
        )
        text = extract_text(params)
        answer = graph.invoke({"query": text, "answer": ""}).get("answer", "")

        async def stream_gen():
            emitted = ""
            for i in range(1, len(answer) + 1):
                emitted = answer[:i]
                event = build_message(emitted, task_id, context_id)
                yield {
                    "data": json.dumps(
                        {"jsonrpc": "2.0", "id": req_id, "result": event},
                        ensure_ascii=False,
                    )
                }
                await asyncio.sleep(0.1)

            task = build_task(answer, task_id, context_id)
            TASKS[task_id] = task

        return EventSourceResponse(stream_gen())

    if method == "tasks/get":
        tid = params.get("id") or params.get("taskId")
        task = TASKS.get(str(tid))
        if not task:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32004, "message": "task not found"},
            }
        return {"jsonrpc": "2.0", "id": req_id, "result": task}

    if method == "tasks/cancel":
        tid = params.get("id") or params.get("taskId")
        task = TASKS.get(str(tid))
        if not task:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32004, "message": "task not found"},
            }
        task["status"] = {"state": "canceled"}
        return {"jsonrpc": "2.0", "id": req_id, "result": task}

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"method `{method}` not found"},
    }


async def main():
    config = uvicorn.Config(app, host=APP_HOST, port=APP_PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
