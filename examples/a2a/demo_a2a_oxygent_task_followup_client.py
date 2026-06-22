"""Validate A2A task follow-up with context_id + reference_task_ids.

Prerequisite:
    PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py

Run:
    PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_task_followup_client.py
"""

import asyncio
import time

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
    Config.set_app_name("demo-a2a-oxygent-task-followup-client")
    oxy_space = [
        oxy.A2AClientAgent.minimal(
            name="a2a_client",
            server_url=SERVER_URL,
            timeout=60,
            streaming=False,
            enable_task_polling=True,
        )
    ]

    async with MAS(oxy_space=oxy_space) as mas:
        first = await call_once(mas, "哪个数字最大，直接给出结果，1，5，7")
        print("\n[turn1]", first.output)
        session = {
            "context_id": first.extra.get("context_id"),
            "task_id": first.extra.get("task_id"),
        }
        print("session:", session["context_id"], session["task_id"])
        if not session["context_id"] or not session["task_id"]:
            raise RuntimeError("missing session ids from turn1 response")

        time.sleep(1)
        second = await call_once(
            mas,
            "哪个数字最小",
            context_id=session["context_id"],
            reference_task_ids=[session["task_id"]],
        )
        print("\n[turn2]", second.output)
        print("session:", second.extra.get("context_id"), second.extra.get("task_id"))


if __name__ == "__main__":
    asyncio.run(main())
