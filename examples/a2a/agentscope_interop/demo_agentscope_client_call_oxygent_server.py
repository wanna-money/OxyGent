"""AgentScope client -> OxyGent A2A server demo.

Prerequisite:
    PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py

Run:
    PYTHONPATH=. python examples/agents/demo_agentscope_client_call_oxygent_server.py
"""

import asyncio

from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agentscope.agent import A2AAgent
from agentscope.message import Msg


def build_oxygent_agent_card() -> AgentCard:
    return AgentCard(
        name="oxygent_a2a_server",
        description="OxyGent A2A server endpoint",
        url="http://127.0.0.1:8090/a2a",
        version="0.1.0",
        capabilities=AgentCapabilities(
            push_notifications=False,
            state_transition_history=True,
            # Use non-streaming path to avoid async stream-close race in
            # AgentScope demo runtime.
            streaming=False,
        ),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[
            AgentSkill(
                id="chat",
                name="chat",
                description="Chat with OxyGent server",
                tags=["chat", "oxygent", "a2a"],
            )
        ],
    )


async def main() -> None:
    agent = A2AAgent(agent_card=build_oxygent_agent_card())

    msg1 = Msg(name="user", role="user", content="哪个数字最大，1，5，7")
    resp1 = await agent(msg1)
    print("\n[turn1]", resp1.get_text_content())

    await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
