# How to Set Up System Global Data?

OxyGent supports a very simple way to set and modify system global data. This data functions like global variables and can be accessed and modified within MAS using `OxyRequest`.

Supported methods include:
+ `get_global_data`: Access global data by key using `(key, default_value)`
+ `set_global_data`: Modify global data by key using `(key, value)`

Below is a simple counter implementation using global data.

```python
class CounterAgent(BaseAgent):
    async def execute(self, oxy_request: OxyRequest):
        cnt = oxy_request.get_global_data("counter", 0) + 1 # Get the count
        oxy_request.set_global_data("counter", cnt) # Store count + 1

        return OxyResponse(
            state=OxyState.COMPLETED,
            output=f"This MAS has been called {cnt} time(s).",
            oxy_request=oxy_request,
        )
```

By setting this `CounterAgent` as the `master`, you can output the number of times the MAS has been called.

```python
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
    CounterAgent(
        name="master_agent",  
        is_master=True,
    ),
]

async def main():
    async with MAS(name="global_demo", oxy_space=oxy_space) as mas:
        # First call -> counter = 1
        r1 = await mas.chat_with_agent({"query": "first"})
        print(r1.output)

        # Second call -> counter = 2 (global_data persisted inside MAS)
        r2 = await mas.chat_with_agent({"query": "second"})
        print(r2.output)

        # Access directly from MAS:
        print("Current global_data:", mas.global_data)
    # The lifecycle of global data is the same as MAS
```

[Previous: Setting Up Database](./database.md)
[Next: Creating a Simple Multi-Agent System](../multi-agent/multi-agent-system.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Global Data Example](../../examples/backend/demo_global_data.md) -- Demonstrates how to set up and use global data
- [Data Scope Example](../../examples/backend/demo_data_scope.md) -- Demonstrates data behavior across different scopes
