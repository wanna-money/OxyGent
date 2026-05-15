# How to Set Up a Database?

OxyGent supports setting up external tools, such as your database. Currently, OxyGent supports three types of external databases:

+ Elasticsearch: https://www.elastic.co/elasticsearch
+ Redis: https://redis.io/
+ Vearch: https://github.com/vearch/vearch

Taking Elasticsearch as an example, you can enter your database information in [Config](https://github.com/jd-opensource/OxyGent/blob/main/oxygent/config.py):

```python
Config.set_es_config( # Adjust according to your actual database type
    {
        "hosts": ["${PROD_ES_HOST_1}", "${PROD_ES_HOST_2}", "${PROD_ES_HOST_3}"],
        "user": "${PROD_ES_USER}",
        "password": "${PROD_ES_PASSWORD}",
    }
)
```

After setting up the database, agents will automatically use it for storage and retrieval. If you have not configured a database, OxyGent will use the local file system to simulate database operations.

## Complete Runnable Example

Here is a complete runnable code example:

```python
"""Demo for using OxyGent with multiple LLMs and an agent."""

import asyncio

from oxygent import MAS, Config, oxy
import os

Config.set_es_config(
    {
        "hosts": ["${PROD_ES_HOST_1}", "${PROD_ES_HOST_2}", "${PROD_ES_HOST_3}"],
        "user": "${PROD_ES_USER}",
        "password": "${PROD_ES_PASSWORD}",
    }
)
oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.01},
        semaphore=4,
        timeout=240,
    ),
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        llm_model="default_llm",
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "hello"},
        ]
        result = await mas.call(callee="master_agent", arguments={"messages": messages})
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

[Previous: Setting Up OxyGent Config](../getting-started/config.md)
[Next: Setting Up Global Data](./global-data.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Config Configuration Example](../../examples/backend/demo_config.md) -- Demonstrates how to configure OxyGent, including database setup
