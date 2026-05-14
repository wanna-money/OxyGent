"""OxyGent A2AClientAgent streaming demo (minimal mode).

Prerequisite:
    PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py

Run:
    PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_stream_client.py
"""

import asyncio
import json

from oxygent import Config, MAS, OxyRequest, oxy

SERVER_URL = "http://127.0.0.1:8090/a2a"

async def call_once(mas: MAS, query: str):
    req = OxyRequest(
        callee="stream_client",
        arguments={"query": query},
        is_send_message=False,
        is_save_history=False,
    )
    req.mas = mas
    return await mas.oxy_name_to_oxy["stream_client"].execute(req)


async def main():
    Config.set_app_name("demo-a2a-stream-client-agent")
    oxy_space = [
        oxy.A2AClientAgent.minimal(
            name="stream_client",
            server_url=SERVER_URL,
            streaming=True,
            timeout=120,
            enable_task_polling=False,
        )
    ]

    async with MAS(oxy_space=oxy_space) as mas:
        response = await call_once(mas, "讲一个100字的故事。")
        task_id = response.extra.get("task_id")
        print("\n[final]", response.output)
        print("session:", response.extra.get("context_id"), task_id)

        if task_id:
            client = mas.oxy_name_to_oxy["stream_client"]
            task = await client.get_task(task_id=task_id)
            print("[tasks/get]")
            print(json.dumps(task, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
