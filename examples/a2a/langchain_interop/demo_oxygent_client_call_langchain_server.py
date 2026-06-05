"""OxyGent client -> LangChain A2A server demo.

Prerequisite:
    PYTHONPATH=. python examples/agents/demo_langchain_a2a_server.py

Run:
    PYTHONPATH=. python examples/agents/demo_oxygent_client_call_langchain_server.py
"""

import asyncio

from oxygent import MAS, Config, OxyRequest, oxy

SERVER_URL = "http://127.0.0.1:8101/a2a"


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
        callee="langchain_client",
        arguments=args,
        is_send_message=False,
        is_save_history=False,
    )
    req.mas = mas
    return await mas.oxy_name_to_oxy["langchain_client"].execute(req)


async def main():
    Config.set_app_name("demo-oxygent-client-call-langchain-server")
    oxy_space = [
        oxy.A2AClientAgent.minimal(
            name="langchain_client",
            server_url=SERVER_URL,
            streaming=False,
            enable_task_polling=True,
            timeout=60,
        )
    ]

    async with MAS(oxy_space=oxy_space) as mas:
        first = await call_once(mas, "请介绍你自己，并说明你来自哪个框架")
        print("\n[turn1]", first.output)
        print("session:", first.extra.get("context_id"), first.extra.get("task_id"))


if __name__ == "__main__":
    asyncio.run(main())
