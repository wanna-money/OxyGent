"""OxyGent streaming client -> LangChain A2A server demo.

Prerequisite:
    PYTHONPATH=. python examples/a2a/langchain_interop/demo_langchain_a2a_server.py

Run:
    PYTHONPATH=. python examples/a2a/langchain_interop/demo_oxygent_stream_client_call_langchain_server.py
"""

import asyncio

from oxygent import Config, MAS, OxyRequest, oxy

SERVER_URL = "http://127.0.0.1:8101/a2a"
CLIENT_NAME = "langchain_stream_client"


async def call_once(mas: MAS, query: str):
    req = OxyRequest(
        callee=CLIENT_NAME,
        arguments={"query": query},
        is_send_message=False,
        is_save_history=False,
    )
    req.mas = mas
    return await mas.oxy_name_to_oxy[CLIENT_NAME].execute(req)


async def main():
    Config.set_app_name("demo-oxygent-stream-client-call-langchain-server")
    oxy_space = [
        oxy.A2AClientAgent.minimal(
            name=CLIENT_NAME,
            server_url=SERVER_URL,
            streaming=True,
            timeout=120,
            enable_task_polling=False,
        )
    ]

    async with MAS(oxy_space=oxy_space) as mas:
        response = await call_once(mas, "请简要介绍一下 LangChain A2A 服务能力。")
        print("\n[final]", response.output)
        print("session:", response.extra.get("context_id"), response.extra.get("task_id"))


if __name__ == "__main__":
    asyncio.run(main())
