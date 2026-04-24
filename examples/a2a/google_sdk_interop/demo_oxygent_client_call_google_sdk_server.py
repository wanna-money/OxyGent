"""OxyGent client -> Google A2A SDK server demo.

Prerequisite:
    PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_google_sdk_a2a_server.py

Run:
    PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_oxygent_client_call_google_sdk_server.py
"""

import asyncio
import os

from oxygent import Config, MAS, OxyRequest, oxy

SERVER_URL = "http://127.0.0.1:8011"
CLIENT_NAME = "google_sdk_server_client"
DEMO_HEADERS = {
    "x-demo-client": "oxygent-a2a",
    "x-demo-token": os.getenv("GOOGLE_A2A_DEMO_TOKEN", "demo-token"),
}


async def call_once(mas: MAS, query: str):
    req = OxyRequest(
        callee=CLIENT_NAME,
        arguments={"query": query},
        shared_data={"_headers": DEMO_HEADERS},
        is_send_message=False,
        is_save_history=False,
    )
    req.mas = mas
    return await mas.oxy_name_to_oxy[CLIENT_NAME].execute(req)


async def main():
    Config.set_app_name("demo-oxygent-client-call-google-sdk-server")
    oxy_space = [
        oxy.A2AClientAgent.minimal(
            name=CLIENT_NAME,
            server_url=SERVER_URL,
            streaming=False,
            timeout=60,
            enable_task_polling=False,
            headers=DEMO_HEADERS
        )
    ]

    async with MAS(oxy_space=oxy_space) as mas:
        print("request headers:", DEMO_HEADERS)
        response = await call_once(mas, "Please introduce yourself in one short sentence.")
        print(response.output)
        print("session:", response.extra.get("context_id"), response.extra.get("task_id"))


if __name__ == "__main__":
    asyncio.run(main())
