# How to Run Agents in Parallel?

OxyGent supports highly compatible parallel execution, allowing you to run multiple agents simultaneously and collaborate.

## 1. Running Multiple Agents in Parallel

For example, if you need to perform data analysis, text summarization, and error checking on a document at the same time, you can register agents for each function and use `oxy.ParallelAgent` to manage them. `ParallelAgent` handles parallel processing and aggregates the results from each agent.

You can also set the maximum concurrency for each agent using the `semaphore` parameter.

```python
oxy.ChatAgent( # Agents to run in parallel
    name="text_summarizer",
    desc="A tool that can summarize markdown text",
    prompt=prompts.text_summarizer_prompt,
),
oxy.ChatAgent(
    name="data_analyser",
    desc="A tool that can summarize echart data",
    prompt=prompts.data_analyser_prompt,
),
oxy.ChatAgent(
    name="document_checker",
    desc="A tool that can find problems in document",
    prompt=prompts.document_checker_prompt,
),
oxy.ParallelAgent( # Managing upper-level agent
    name="analyzer",
    desc="A tool that analyze markdown document",
    permitted_tool_name_list=["text_summarizer", "data_analyser", "document_checker"]
),
```

`ParallelAgent` automatically starts all subagents, performs parallel computation, and ultimately returns the results of all tasks.

## 2. Running the Same Agent in Parallel

If you need to run the same agent multiple times in parallel, you can use the `start_batch_processing` method for batch request processing. Below is a complete runnable example:

```python
import asyncio

from pydantic import Field

from oxygent import MAS, Config, OxyRequest, oxy
import os

Config.set_agent_llm_model("default_llm")

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={
            "temperature": 0.7,
            "max_tokens": 512,
            "chat_template_kwargs": {"enable_thinking": False},
        },
        semaphore=200,
    ),
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        llm_model="default_llm",
        semaphore=200,
        timeout=100,
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        outs = await mas.start_batch_processing(["Hello!"] * 10, return_trace_id=True) # Run 10 times in parallel
        print(outs)


if __name__ == "__main__":
    asyncio.run(main())

```

### Notes

1. **`start_batch_processing`**: This method accepts a list of multiple requests, asynchronously executes all requests in parallel, and returns the results. If you want to process multiple identical or different requests, you can use this method for rapid batch processing.
2. **`semaphore`**: This parameter controls concurrency. By setting an appropriate concurrency level, you can flexibly manage system resource consumption and avoid performance bottlenecks caused by too many parallel requests.
3. **`return_trace_id=True`**: Returns the trace ID for each request, making it easy to track the execution process and results of each request.

[Previous: Duplicating Identical Agents](./mixture-of-agents.md)
[Next: Running Agents in a Distributed Manner](./distributed.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Parallel Agent Example](../../examples/agents/demo_parallel.md) -- Demonstrates the parallel execution usage of ParallelAgent
- [Document Analysis Agent Example](../../examples/agents/demo_document_analysis_agent.md) -- Demonstrates a practical application of parallel document processing
