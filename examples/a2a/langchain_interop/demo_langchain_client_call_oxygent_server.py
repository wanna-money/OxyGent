"""LangChain-style client -> OxyGent A2A server demo.

Prerequisite:
    PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py

Run:
    PYTHONPATH=. python examples/agents/demo_langchain_client_call_oxygent_server.py
"""

import asyncio
import json

import httpx

try:
    from langchain_core.runnables import RunnableLambda
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "Missing dependency `langchain-core`. Install it first, e.g.:\n"
        "pip install langchain-core"
    ) from e


BASE_URL = "http://127.0.0.1:8090/a2a"


def extract_task_text(task: dict) -> str:
    status_msg = ((task or {}).get("status") or {}).get("message") or {}
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


async def send_once(
    client: httpx.AsyncClient,
    query: str,
    context_id: str | None = None,
    task_id: str | None = None,
):
    message = {
        "kind": "message",
        "messageId": "lc-" + query[:8],
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
    resp = await client.post(BASE_URL, json=payload)
    resp.raise_for_status()
    body = resp.json()
    task = body.get("result", {})
    return task, extract_task_text(task)


async def main():
    pre = RunnableLambda(lambda q: f"[LangChain Client] {q}")
    post = RunnableLambda(lambda t: t.strip())

    async with httpx.AsyncClient(timeout=60) as client:
        turn1_query = pre.invoke("哪个数字最大，直接回答：1、5、7")
        task1, text1 = await send_once(client, turn1_query)
        print("\n[turn1 raw]", json.dumps(task1, ensure_ascii=False))
        print("[turn1]", post.invoke(text1))


if __name__ == "__main__":
    asyncio.run(main())
