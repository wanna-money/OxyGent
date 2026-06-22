# How to Use Multimodal?

The current version of OxyGent supports multimodal input for images and videos. Through multimodal capabilities, you can use images, videos, and other attachments as input, combined with text for processing, enabling richer interactions.

## Configuring a Multimodal Model

First, you need to declare your multimodal model. In particular, you need to set `is_multimodal_supported` to `True` to enable multimodal support:

```python
oxy.HttpLLM(
    name="default_vlm",
    api_key=os.getenv("DEFAULT_VLM_API_KEY"),
    base_url=os.getenv("DEFAULT_VLM_BASE_URL"),
    model_name=os.getenv("DEFAULT_VLM_MODEL_NAME"),
    llm_params={"temperature": 0.6, "max_tokens": 2048},
    max_pixels=10000000,  # set maximum pixel size
    is_multimodal_supported=True,  # enable multimodal support
    is_convert_url_to_base64=True,  # convert URLs to base64 format if needed
    semaphore=4,
)
```

## Passing Attachments

Once multimodal support is enabled, you can pass attachments via the `attachments` parameter (or the visual interface). OxyGent will automatically process these attachments and pass them along with the query:

```python
async with MAS(oxy_space=oxy_space) as mas:
    """Single-turn conversation"""
    payload = {
        "query": "What is it in the picture?",  # question
        "attachments": ["http://image.jd.com/123.jpg"],  # pass image attachment
    }
    oxy_response = await mas.chat_with_agent(payload=payload)
    print("LLM: ", oxy_response.output)
```

In this example, `attachments` contains the image URL. OxyGent will automatically fetch the image from the URL and process it.

## Complete Runnable Example

Here is a complete runnable example demonstrating how to configure and use multimodal input:

```python
import asyncio

from oxygent import MAS, Config, OxyRequest, OxyResponse, oxy
import os

# Set LLM model
Config.set_agent_llm_model("default_vlm")


async def master_workflow(oxy_request: OxyRequest) -> OxyResponse:
    # Call generate_agent to process image description
    generate_agent_oxy_response = await oxy_request.call(
        callee="generate_agent",
        arguments={
            "query": oxy_request.get_query(),
            "attachments": oxy_request.arguments.get("attachments", []),
            "llm_params": {"temperature": 0.6},
        },
    )
    # Call discriminate_agent to determine if the image description is accurate
    discriminate_agent_oxy_response = await oxy_request.call(
        callee="discriminate_agent",
        arguments={
            "query": str(generate_agent_oxy_response.output),
            "attachments": oxy_request.arguments.get("attachments", []),
        },
    )
    return f"generate_agent output: {generate_agent_oxy_response.output} \n discriminate_agent output: {discriminate_agent_oxy_response.output}"


# Initialize oxy_space
oxy_space = [
    oxy.HttpLLM(
        name="default_vlm",
        api_key=os.getenv("DEFAULT_VLM_API_KEY"),
        base_url=os.getenv("DEFAULT_VLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_VLM_MODEL_NAME"),
        llm_params={"temperature": 0.6, "max_tokens": 2048},
        max_pixels=10000000,  # set maximum pixel count
        is_multimodal_supported=True,  # enable multimodal support
        is_convert_url_to_base64=True,  # convert image URLs to base64 format
        semaphore=4,
    ),
    oxy.ChatAgent(
        name="generate_agent",
        prompt="You are a helpful assistant. Please describe the content of the image in detail.",
    ),
    oxy.ChatAgent(
        name="discriminate_agent",
        prompt="Please determine whether the following text is a description of the content of the image. If it is, please output 'True', otherwise output 'False'.",
    ),
    oxy.Workflow(
        name="master_agent",
        is_master=True,
        permitted_tool_name_list=["generate_agent", "discriminate_agent"],
        func_workflow=master_workflow,
    ),
]

# Main function
async def main():
    # Multimodal input
    async with MAS(oxy_space=oxy_space) as mas:
        """Single-turn conversation"""
        payload = {
            "query": "What is it in the picture?",
            "attachments": ["http://image.jd.com/123.jpg"],  # pass image URL
        }
        oxy_response = await mas.chat_with_agent(payload=payload)
        print("LLM: ", oxy_response.output)


if __name__ == "__main__":
    asyncio.run(main())
```

### Notes

1. **`is_multimodal_supported=True`**: Enables multimodal support, allowing you to use images, videos, and other attachments as input.
2. **`attachments`**: Used to pass images or other attachments. You can provide URLs or Base64-encoded files.


[Previous: Retrieving Memory and Regenerating](./continue-exec.md)
[Next: RAG](./rag.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Multimodal Example](../../examples/advanced/demo_multimodal.md) -- Demonstrates how to configure and use multimodal input for image processing
- [Multimodal Transfer Example](../../examples/advanced/demo_multimodal_transfer.md) -- Demonstrates how to pass multimodal data between agents
