"""OxyGent client -> AgentScope A2A server demo.

Prerequisite:
    python examples/agents/demo_agentscope_a2a_server.py

Run:
    PYTHONPATH=. python examples/agents/demo_oxygent_client_call_agentscope_server.py
"""

import asyncio

from oxygent import MAS, Config, OxyRequest, oxy

SERVER_URL = "http://127.0.0.1:8003"


async def call_once(
    mas: MAS,
    query: str,
    context_id: str | None = None,
    task_id: str | None = None,
):
    args = {"query": query}
    if context_id:
        args["context_id"] = context_id
    if task_id:
        args["task_id"] = task_id

    req = OxyRequest(
        callee="agentscope_client",
        arguments=args,
        is_send_message=False,
        is_save_history=False,
    )
    req.mas = mas
    return await mas.oxy_name_to_oxy["agentscope_client"].execute(req)


async def main():
    Config.set_app_name("demo-oxygent-client-call-agentscope-server")

    oxy_space = [
        oxy.A2AClientAgent.minimal(
            name="agentscope_client",
            server_url=SERVER_URL,
            # Do not pass relative card_url here.
            # A2AClientAgent will use default card_path ".well-known/agent.json".
            # AgentScope demo server mainly implements stream handler.
            streaming=True,
            timeout=120,
            enable_task_polling=False,
            task_poll_interval_seconds=1,
            task_poll_max_wait_seconds=30,
        )
    ]

    async with MAS(oxy_space=oxy_space) as mas:
        first = await call_once(mas, "请用一句话介绍你自己")
        print("\n[turn1]", first.output)
        session = {
            "context_id": first.extra.get("context_id"),
            "task_id": first.extra.get("task_id"),
        }
        print("session:", session["context_id"], session["task_id"])


if __name__ == "__main__":
    asyncio.run(main())
