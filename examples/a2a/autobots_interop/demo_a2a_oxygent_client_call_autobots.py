"""Use OxyGent A2AClientAgent to call Autobots A2A server.

Run:
    export JD_A2A_API_KEY="your_api_key"
    export JD_A2A_ERP="your_erp"  # optional
    PYTHONPATH=. python examples/a2a/demo_a2a_client_call_autobots.py
"""

import asyncio
import os

from oxygent import Config, MAS, OxyRequest, oxy

API_KEY = os.getenv("JD_A2A_API_KEY", "").strip()
ERP = os.getenv("JD_A2A_ERP", "zhaoli257").strip()
BASE_URL = "http://autobots-bk.jd.local/autobots/api/v1/a2a/agent/78441"
CARD_URL = f"{BASE_URL}/.well-known/agent.json?team_code=&token={API_KEY}"
CLIENT_NAME = "autobots_client"


def build_oxy_space():
    if not API_KEY:
        raise ValueError("Please set JD_A2A_API_KEY before running this demo.")
    return [
        oxy.A2AClientAgent.minimal(
            name=CLIENT_NAME,
            server_url=BASE_URL,
            card_url=CARD_URL,
            metadata={"erp": ERP, "token": API_KEY},
            streaming=False,
            timeout=120,
            enable_task_polling=True,
            task_poll_interval_seconds=1,
            task_poll_max_wait_seconds=60,
        )
    ]


async def call_once(
    mas: MAS,
    query: str,
):
    req = OxyRequest(
        callee=CLIENT_NAME,
        arguments={"query": query},
        is_send_message=False,
        is_save_history=False,
    )
    req.mas = mas
    return await mas.oxy_name_to_oxy[CLIENT_NAME].execute(req)


async def main():
    Config.set_app_name("demo-a2a-client-call-autobots")
    async with MAS(oxy_space=build_oxy_space()) as mas:
        response = await call_once(mas, "当前时间是多少")
        print(response.output)
        print("session:", response.extra.get("context_id"), response.extra.get("task_id"))
        if response.extra.get("polling"):
            print("polling:", response.extra["polling"])


if __name__ == "__main__":
    asyncio.run(main())
