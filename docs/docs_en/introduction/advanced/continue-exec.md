# How to Modify Memory Nodes?

OxyGent supports reading memory and re-execution. You can specify the node to access in the `chat_with_agent` method, modify the node content, and restart the system from the modified node.

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        # First run
        payload = {
            "query": "Get what time it is in America/New_York and save in `log.txt` under `./local_file`",
        }
        oxy_response = await mas.chat_with_agent(payload=payload)
        from_trace_id = oxy_response.oxy_request.current_trace_id
        print("LLM: ", oxy_response.output, from_trace_id)
```

Suppose during this run, you want to modify the content of the following node:

```apache
2025-07-29 23:21:45,029 - INFO - i4oNVqcwQjz6KVg6 - 6m8jX6xmQF4xXzpo - user <<< master_agent <<< time_agent <<< get_current_time  : {
  "timezone": "America/New_York",
  "datetime": "2025-07-30T02:21:45-04:00",
  "is_dst": true
}
```

You can record the node ID that needs to be modified and use the following method in `payload`:

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        # Second run
        payload = {
            "query": "Get what time it is in America/New_York and save in `log.txt` under `./local_file`",  
            "from_trace_id": "",
            "reference_trace_id": "i4oNVqcwQjz6KVg6",  # trace ID (optional)
            "restart_node_id": "6m8jX6xmQF4xXzpo", # node ID (required)
            "restart_node_output": """{ 
                "timezone": "America/New_York",
                "datetime": "2024-07-21T05:32:43-04:00",
                "is_dst": true
            }""", # output to modify (note: it is best to keep the format consistent)
        }
        oxy_response = await mas.chat_with_agent(payload=payload)
        from_trace_id = oxy_response.oxy_request.current_trace_id
        print("LLM: ", oxy_response.output, from_trace_id)
```

After re-execution, the system's output will reflect the value you set: `2024-07-21T05:32:43-04:00`.

```
2025-07-29 23:22:46,506 - INFO - qgk2gECEE7GFiB7X - ci4fmTXrvn35YSTV - user <<< master_agent <<< default_llm  Wrote by user: {
                "timezone": "America/New_York",
                "datetime": "2024-07-21T05:39:43-04:00",
                "is_dst": true
            }
...
LLM:  The current time in America/New_York has been successfully recorded as 05:39 AM, and the information has been saved in the file `./local_file/log.txt`. qgk2gECEE7GFiB7X
```

You can also perform detailed debugging and re-execution through the visual interface.

[Previous: Creating Flows](./preset-flows.md)
[Next: Multimodal](./multimodal.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Continue Execution Example](../../examples/advanced/demo_continue_exec.md) -- Demonstrates how to modify memory nodes and re-execute from a specified node
