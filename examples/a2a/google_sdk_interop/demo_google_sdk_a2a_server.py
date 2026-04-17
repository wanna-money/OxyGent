# -*- coding: utf-8 -*-
"""Minimal Google A2A SDK server demo (local).

Run:
    PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_google_sdk_a2a_server.py

Then call with OxyGent client:
    PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_oxygent_client_call_google_sdk_server.py
"""

import logging
import time
import uuid
from typing import Any, AsyncGenerator

from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import Event
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    Message,
    MessageSendParams,
    Part,
    Role,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
)
from a2a.utils.message import get_message_text

HOST = "0.0.0.0"
PORT = 8011
BASE_URL = f"http://127.0.0.1:{PORT}"
logger = logging.getLogger(__name__)


def build_agent_card() -> AgentCard:
    return AgentCard(
        name="google_sdk_demo_server",
        description="Minimal A2A SDK server for OxyGent interop testing",
        url=BASE_URL,
        version="0.1.0",
        capabilities=AgentCapabilities(
            push_notifications=False,
            state_transition_history=True,
            streaming=True,
        ),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[
            AgentSkill(
                id="chat",
                name="chat",
                description="Simple chat test skill",
                tags=["a2a", "sdk", "interop"],
            )
        ],
    )


class SimpleA2AHandler:
    """Simple handler for non-stream and stream message calls."""

    async def on_message_send(self, params: MessageSendParams, *args: Any, **kwargs: Any) -> Message:
        query = get_message_text(params.message) or ""
        context_id = params.message.context_id
        task_id = params.message.task_id
        answer = f"Google SDK A2A server reply: I received your question: {query}"
        logger.info("on_message_send context_id=%s task_id=%s query=%s", context_id, task_id, query)
        return Message(
            messageId=uuid.uuid4().hex,
            role=Role.agent,
            parts=[Part(root=TextPart(text=answer))],
            contextId=context_id,
            taskId=task_id,
        )

    async def on_message_send_stream(
        self,
        params: MessageSendParams,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncGenerator[Event, None]:
        task_id = params.message.task_id or uuid.uuid4().hex
        context_id = params.message.context_id or "google-sdk-context"
        query = get_message_text(params.message) or ""
        logger.info(
            "on_message_send_stream context_id=%s task_id=%s query=%s",
            context_id,
            task_id,
            query,
        )

        yield TaskStatusUpdateEvent(
            task_id=task_id,
            context_id=context_id,
            status=TaskStatus(state=TaskState.working),
            final=False,
        )

        text = f"Google SDK stream reply: {query}"
        for i in range(1, len(text) + 1):
            partial = text[:i]
            msg = Message(
                messageId=uuid.uuid4().hex,
                role=Role.agent,
                parts=[Part(root=TextPart(text=partial))],
                contextId=context_id,
                taskId=task_id,
            )
            time.sleep(0.1)
            yield TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=context_id,
                status=TaskStatus(state=TaskState.working, message=msg),
                final=False,
            )

        yield TaskStatusUpdateEvent(
            task_id=task_id,
            context_id=context_id,
            status=TaskStatus(state=TaskState.completed),
            final=True,
        )


handler = SimpleA2AHandler()
app = A2AStarletteApplication(
    agent_card=build_agent_card(),
    http_handler=handler,
).build()


if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Google SDK A2A demo server at %s:%s", HOST, PORT)
    uvicorn.run(app, host=HOST, port=PORT, reload=False)
