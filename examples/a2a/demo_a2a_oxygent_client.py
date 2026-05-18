"""Call local OxyGent A2A server with OxyGent A2A client.

Prerequisite:
    PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py

Run:
    PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_client.py
"""

import asyncio
import json

from oxygent import MAS, Config, OxyRequest, oxy

SERVER_URL = "http://127.0.0.1:8090/a2a"


async def call_once(
    mas: MAS,
    query: str,
    context_id: str | None = None,
    task_id: str | None = None,
    reference_task_ids: list[str] | None = None,
):
    args = {"query": query}
    if context_id:
        args["context_id"] = context_id
    if task_id:
        args["task_id"] = task_id
    if reference_task_ids:
        args["reference_task_ids"] = reference_task_ids
    req = OxyRequest(
        callee="a2a_client",
        arguments=args,
        is_send_message=False,
        is_save_history=False,
    )
    req.mas = mas
    return await mas.oxy_name_to_oxy["a2a_client"].execute(req)


async def main():
    Config.set_app_name("demo-a2a-oxygent-client")
    oxy_space = [
        oxy.A2AClientAgent.minimal(
            name="a2a_client",
            server_url=SERVER_URL,
            timeout=60,
            streaming=False,
            enable_task_polling=False,
        )
    ]

    async with MAS(oxy_space=oxy_space) as mas:
        response = await call_once(mas, "1+1等于几")
        task_id = response.extra.get("task_id")
        print(response.output)
        print("session:", response.extra.get("context_id"), task_id)

        if task_id:
            client = mas.oxy_name_to_oxy["a2a_client"]
            task = await client.get_task(task_id=task_id)
            print("[tasks/get]")
            print(json.dumps(task, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
