"""A2A SDK streaming client demo for OxyGent server.

Prerequisite:
    PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py

Run:
    PYTHONPATH=. python examples/agents/demo_a2a_sdk_stream_client.py
"""

import asyncio
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    Message,
    MessageSendParams,
    SendStreamingMessageRequest,
    Task,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
)
from a2a.utils.message import get_message_text
from a2a.utils.parts import get_text_parts


def extract_text(result) -> str:
    if isinstance(result, Message):
        return get_message_text(result) or ""
    if isinstance(result, Task):
        chunks = []
        if result.status and result.status.message:
            txt = get_message_text(result.status.message)
            if txt:
                chunks.append(txt)
        if result.artifacts:
            for a in result.artifacts:
                chunks.extend(get_text_parts(a.parts or []))
        return "\n".join([x for x in chunks if x]).strip()
    if isinstance(result, TaskStatusUpdateEvent):
        status = getattr(result, "status", None)
        msg = getattr(status, "message", None) if status else None
        return get_message_text(msg) if msg else ""
    if isinstance(result, TaskArtifactUpdateEvent):
        artifact = getattr(result, "artifact", None)
        return "\n".join(get_text_parts(getattr(artifact, "parts", None) or [])).strip()
    return ""


async def main() -> None:
    base_url = "http://127.0.0.1:8090/a2a"
    card_path = ".well-known/agent.json"

    async with httpx.AsyncClient(timeout=120) as http_client:
        resolver = A2ACardResolver(
            httpx_client=http_client,
            base_url=base_url,
            agent_card_path=card_path,
        )
        card = await resolver.get_agent_card()
        print("[card]", card.url)

        client = A2AClient(httpx_client=http_client, agent_card=card)

        payload = {
            "message": {
                "role": "user",
                "parts": [
                    {"kind": "text", "text": "请分三点介绍 OxyGent A2A 流式能力"}
                ],
                "messageId": uuid4().hex,
            },
            "metadata": {},
        }

        req = SendStreamingMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**payload),
        )

        print("\n[stream begin]")
        emitted = ""
        async for chunk in client.send_message_streaming(req):
            root = getattr(chunk, "root", None)
            if root is None:
                continue
            if getattr(root, "error", None) is not None:
                print("[stream error]", root.error)
                break

            result = getattr(root, "result", None)
            text = extract_text(result)
            if text:
                delta = text[len(emitted) :] if text.startswith(emitted) else text
                emitted = text if text.startswith(emitted) else (emitted + text)
                if delta:
                    print(delta, end="")

            # print raw chunk for debugging/compat check
            # print("[chunk]", json.dumps(chunk.model_dump(mode="json", exclude_none=True), ensure_ascii=False))

        print("[stream end]")
        print("[final]", emitted)


if __name__ == "__main__":
    asyncio.run(main())
