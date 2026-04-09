"""Use A2A SDK client to call OxyGent A2A server.

Prerequisite:
    PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py

Run:
    PYTHONPATH=. python examples/a2a/demo_a2a_sdk_call_oxygent_server.py
"""

import asyncio
import json
from typing import Any
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    GetTaskRequest,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
    TaskQueryParams,
)


async def poll_task(
    client: A2AClient,
    task_id: str,
    metadata: dict[str, Any] | None = None,
    interval_seconds: int = 1,
    max_wait_seconds: int = 30,
):
    terminal_states = {"completed", "failed", "canceled", "rejected"}
    waited = 0
    while True:
        get_request = GetTaskRequest(
            id=str(uuid4()),
            params=TaskQueryParams(id=task_id, metadata=metadata or None),
        )
        get_resp = await client.get_task(get_request)
        print("[tasks/get]", json.dumps(get_resp.model_dump(mode="json", exclude_none=True), ensure_ascii=False))

        task_obj = getattr(get_resp.root, "result", None) if getattr(get_resp, "root", None) else None
        state = ""
        if task_obj and getattr(task_obj, "status", None) and getattr(task_obj.status, "state", None):
            state_obj = task_obj.status.state
            state = getattr(state_obj, "value", state_obj)
            state = str(state).lower()

        if state in terminal_states:
            print({"taskId": task_id, "state": state, "msg": "task finished"})
            return

        if waited >= max_wait_seconds:
            print({"taskId": task_id, "state": state or "unknown", "msg": "polling timeout"})
            return

        await asyncio.sleep(interval_seconds)
        waited += interval_seconds


async def main() -> None:
    streaming = False
    enable_polling = True

    base_url = "http://127.0.0.1:8090/a2a"
    agent_card_path = ".well-known/agent.json"

    async with httpx.AsyncClient(timeout=60) as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
            agent_card_path=agent_card_path,
        )

        card: AgentCard = await resolver.get_agent_card()
        print("[agent_card]", card.model_dump_json(indent=2, exclude_none=True))

        # Keep one client for whole conversation.
        client = A2AClient(httpx_client=httpx_client, agent_card=card)

        # ---- turn 1 ----
        send_message_payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "计算1+1的结果"}],
                "messageId": uuid4().hex,
            },
            "metadata": {},
        }

        if streaming:
            streaming_request = SendStreamingMessageRequest(
                id=str(uuid4()),
                params=MessageSendParams(**send_message_payload),
            )
            print("[turn1 stream]")
            async for chunk in client.send_message_streaming(streaming_request):
                print(json.dumps(chunk.model_dump(mode="json", exclude_none=True), ensure_ascii=False))
            return

        request = SendMessageRequest(id=str(uuid4()), params=MessageSendParams(**send_message_payload))
        response = await client.send_message(request)
        print("[turn1 send]", json.dumps(response.model_dump(mode="json", exclude_none=True), ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
