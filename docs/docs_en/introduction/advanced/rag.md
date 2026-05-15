# How to Perform Retrieval-Augmented Generation?

OxyGent supports injecting knowledge into prompts via the `knowledge` parameter. Below is a simple RAG example:

If you haven't learned how to process prompts yet, it is recommended to read [How to Customize Prompt Processing?](./process-input.md).

You first need to create a `retrieval` method:

```python
def retrieval(query):
    # Replace with an actual database
    return "\n".join(["knowledge1", "knowledge2", "knowledge3"])
```

Then, you need to inject the retrieved knowledge in `update_query`:

```python
def update_query(oxy_request: OxyRequest):
    current_query = oxy_request.get_query()

    def retrieval(query):
        return "\n".join(["knowledge1", "knowledge2", "knowledge3"])

    oxy_request.arguments["knowledge"] = retrieval(current_query) # key method
    return oxy_request
```

## Complete Runnable Example

Here is a complete runnable code example:

```python
import asyncio

from oxygent import MAS, OxyRequest, oxy
import os

INSTRUCTION = """
You are a helpful assistant and can use these tools:
${tools_description}

Experience in choosing tools:
${knowledge}

Select the appropriate tool based on the user's question.
If no tool is needed, reply directly.
If answering the user's question requires calling multiple tools, call only one tool at a time. After the user receives the tool result, they will give you feedback on the tool call result.

Important notes:
1. When you have collected enough information to answer the user's question, please respond in the following format:
<think>Your reasoning (if analysis is needed)</think>
Your response content
2. When you find that the user's question lacks certain conditions, you can ask them back. Please respond in the following format:
<think>Your reasoning (if analysis is needed)</think>
Your follow-up question to the user
3. When you need to use a tool, you must respond **only** with the following exact JSON object format, and nothing else:

{
    "think": "Your reasoning (if analysis is needed)",
    "tool_name": "Tool name",
    "arguments": {
        "Parameter name": "Parameter value"
    }
}
"""


def update_query(oxy_request: OxyRequest):
    current_query = oxy_request.get_query()

    def retrieval(query):
        return "\n".join(["knowledge1", "knowledge2", "knowledge3"])

    oxy_request.arguments["knowledge"] = retrieval(current_query)
    return oxy_request


oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.01},
        semaphore=4,
    ),
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        llm_model="default_llm",
        timeout=100,
        prompt=INSTRUCTION,
        func_process_input=update_query,
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="This is an example for rag. Please modify it according to the specific needs",
        )

if __name__ == "__main__":
    asyncio.run(main())

```


[Previous: Multimodal](./multimodal.md)
[Next: Generating Training Samples](./training.md)
[Back to Home](../readme.md)

---

## Related Examples

- [RAG Agent Example](../../examples/agents/demo_rag_agent.md) -- Demonstrates how to use retrieval-augmented generation to build a knowledge-based Q&A agent
