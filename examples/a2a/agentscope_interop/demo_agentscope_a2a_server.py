# -*- coding: utf-8 -*-
"""AgentScope A2A server demo.

Run:
    PYTHONPATH=. python examples/a2a/agentscope_interop/demo_agentscope_a2a_server.py

Then call with OxyGent client:
    PYTHONPATH=. python examples/a2a/agentscope_interop/demo_oxygent_client_call_agentscope_server.py
"""

import uuid
from typing import Any, AsyncGenerator
import logging

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
PORT = 8003
BASE_URL = f"http://127.0.0.1:{PORT}"
logger = logging.getLogger(__name__)


def build_agent_card() -> AgentCard:
    return AgentCard(
        name="agentscope_a2a_server",
        description="AgentScope ReAct A2A server demo",
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
                description="General chat via AgentScope ReActAgent",
                tags=["chat", "agentscope", "a2a"],
            )
        ],
    )


class AgentScopeStreamHandler:
    """Minimal stream handler for interop testing.

    This server intentionally avoids external model dependencies and only echoes
    the input in streaming status updates.
    """

    async def on_message_send_stream(
        self,
        params: MessageSendParams,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncGenerator[Event, None]:
        task_id = params.message.task_id or uuid.uuid4().hex
        context_id = params.message.context_id or "default-context"
        query = get_message_text(params.message) or ""
        if not query:
            query = "(empty input)"
        logger.info(
            "AgentScope A2A receive message task_id=%s context_id=%s query=%s",
            task_id,
            context_id,
            query,
        )

        yield TaskStatusUpdateEvent(
            task_id=task_id,
            context_id=context_id,
            status=TaskStatus(state=TaskState.working),
            final=False,
        )

        full_text = (
            "我是 AgentScope A2A 测试服务。"
            f"我已收到你的问题：{query}。"
            "这是一个流式演示回复。"
        )
        for i in range(1, len(full_text) + 1):
            partial = full_text[:i]
            agent_message = Message(
                messageId=uuid.uuid4().hex,
                role=Role.agent,
                parts=[Part(root=TextPart(text=partial))],
                taskId=task_id,
                contextId=context_id,
            )
            yield TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=context_id,
                status=TaskStatus(
                    state=TaskState.working,
                    message=agent_message,
                ),
                final=False,
            )
        logger.info(
            "AgentScope A2A stream completed task_id=%s context_id=%s",
            task_id,
            context_id,
        )

        yield TaskStatusUpdateEvent(
            task_id=task_id,
            context_id=context_id,
            status=TaskStatus(state=TaskState.completed),
            final=True,
        )


handler = AgentScopeStreamHandler()
app = A2AStarletteApplication(
    agent_card=build_agent_card(),
    http_handler=handler,
).build()


if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting AgentScope A2A server at %s:%s", HOST, PORT)

    uvicorn.run(app, host=HOST, port=PORT, reload=False)
