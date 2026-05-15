# How to Use Workflows?

## Simple Example

OxyGent supports controlling the execution order of agents through external workflows. You can use the `call` method within a workflow to specify the task execution sequence of agents. For example, in `demo.py`, we use a workflow to ensure the agent queries the time before calculating Pi:

```python
async def workflow(oxy_request: OxyRequest):
    short_memory = oxy_request.get_short_memory()
    print("--- History record --- :", short_memory)
    master_short_memory = oxy_request.get_short_memory(master_level=True)
    print("--- History record-User layer --- :", master_short_memory)
    print("user query:", oxy_request.get_query(master_level=True))
    await oxy_request.send_message("msg")
    oxy_response = await oxy_request.call(
        callee="time_agent",
        arguments={"query": "What time is it now in Asia/Shanghai?"},
    )
    print("--- Current time --- :", oxy_response.output)
    oxy_response = await oxy_request.call(
        callee="default_llm",
        arguments={
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
            "llm_params": {"temperature": 0.6},
        },
    )
    print(oxy_response.output)
    import re

    numbers = re.findall(r"\d+", oxy_request.get_query())
    if numbers:
        n = numbers[-1]
        oxy_response = await oxy_request.call(callee="calc_pi", arguments={"prec": n})
        return f"Save {n} positions: {oxy_response.output}"
    else:
        return "Save 2 positions: 3.14, or you could ask me to save how many positions you want."
```

In this workflow, we first query the time, then perform document analysis, and finally save the computation result. A workflow requires an upper-level Agent for execution. You can use `oxy.WorkflowAgent` to control the workflow:

```python
oxy.WorkflowAgent(
    name="math_agent",
    desc="A tool for pi query",
    sub_agents=["time_agent"],
    tools=["math_tools"],
    func_workflow=workflow,
    is_retain_master_short_memory=True,
),
```
For the complete example, please refer to `demo.py`.

## Building a Workflow

Workflow is a very fine-grained approach. Below, we will start with the example from [How to Customize Prompt Processing?](./process-input.md) and step by step write a runnable workflow.

### Assumed Work Requirements

Assume our work requirement is:

> Write a summary for the document entered by the user, and store the timestamped summary in an `output.txt` file.

The workflow can be broken down into the following steps:

1. Get the time (no original input needed)
2. Analyze the document (requires the user's original input)
3. Write to file (requires the output from the previous two steps)

### Converting Steps to Code

#### Getting the Time (No Original Input Needed)

```python
time_resp = await oxy_request.call(
    callee="time_agent", arguments={"query": "What is the current Beijing time?"}
)
current_time = time_resp.output
```

#### Analyzing the Document (Requires User's Original Input)

```python
# Use get_query to get the user's original input
user_query = oxy_request.get_query(master_level=True)

analysis_resp = await oxy_request.call(
    callee="analyzer",
    arguments={"query": f"Please analyze the document: {user_query}"},
)
analysis_result = analysis_resp.output
```

#### Writing to File (Requires Output from the Previous Two Steps)

```python
final_content = f"Time: {current_time}\n\nAnalysis Result: {analysis_result}"
    file_resp = await oxy_request.call(
        callee="file_agent",
        arguments={"query": f"Please write the following content to output.txt:\n{final_content}"},
    )
```

### Wrapping into a Workflow

Wrap the above steps in order into a workflow. It requires an `OxyRequest` object as a parameter:

```python
async def workflow(oxy_request: OxyRequest):
    # Step 1: Get the time
    time_resp = await oxy_request.call(
        callee="time_agent", arguments={"query": "What is the current Beijing time?"}
    )
    current_time = time_resp.output
    print("== Current Time ==\n", current_time)

    # Subsequent steps...
    return "Process complete, output.txt written successfully"
```

### Specifying an Agent to Invoke the Workflow

Use `oxy.WorkflowAgent` to control the entire workflow and specify the sub-agents and required tools:

```python
oxy.WorkflowAgent(
    name="workflow_agent",
    desc="Workflow for time retrieval + document analysis + file writing",
    sub_agents=["file_agent", "time_agent", "analyzer"],
    func_workflow=workflow,
    llm_model="default_llm",
),
oxy.ReActAgent(
    name="master_agent",
    is_master=True,
    sub_agents=["workflow_agent"],
),
```

The expected output is:

```markdown
Time: The current Beijing time is July 25, 2025, 09:27:01.

Analysis Result: Based on the parallel execution of the tasks, the following summary has been compiled and stored in the `output.txt` file:

---

**Current Time: 2023-12-05 10:00:00**

**Summary:**

...

---

The above summary has been stored in the `output.txt` file.
```

## Complete Runnable Example

Here is a complete runnable code example:

```python
import asyncio
from oxygent import MAS, OxyRequest, Config, oxy
import os
from oxygent import preset_tools

# Set LLM model
Config.set_agent_llm_model("default_llm")

# Workflow core logic
async def workflow(oxy_request: OxyRequest):
    # Step 1: Get the time
    time_resp = await oxy_request.call(
        callee="time_agent", arguments={"query": "What is the current Beijing time?"}
    )
    current_time = time_resp.output
    print("== Current Time ==\n", current_time)

    # Step 2: Get the user's original markdown file query
    user_query = oxy_request.get_query(master_level=True)

    # Step 3: Analyze the document (preserve the original query as file path)
    analysis_resp = await oxy_request.call(
        callee="analyzer",
        arguments={"query": f"Please analyze the document: {user_query}"},
    )
    analysis_result = analysis_resp.output
    print("== Analysis Result ==\n", analysis_result)

    # Step 4: Write to file
    final_content = f"Time: {current_time}\n\nAnalysis Result: {analysis_result}"
    file_resp = await oxy_request.call(
        callee="file_agent",
        arguments={"query": f"Please write the following content to output.txt:\n{final_content}"},
    )
    print("== File Write Result ==\n", file_resp.output)
    return "Process complete, output.txt written successfully"

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
    oxy.StdioMCPClient(
        name="time_tools",
        params={
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
        },
    ),
    preset_tools.file_tools,
    oxy.ReActAgent(
        name="file_agent",
        desc="A tool that can operate the file system",
        tools=["file_tools"],
    ),
    oxy.ReActAgent(
        name="time_agent",
        desc="A tool that can get current time",
        tools=["time_tools"],
    ),
    oxy.ChatAgent(
        name="text_summarizer",
        desc="A tool that can summarize markdown text",
        prompt="You are a text summarizer. Please provide a concise summary of the given text.",
    ),
    oxy.ChatAgent(
        name="data_analyser",
        desc="A tool that can summarize echart data",
        prompt="You are a data analyst. Please analyze the given data and provide insights.",
    ),
    oxy.ChatAgent(
        name="document_checker",
        desc="Document validator",
        prompt="You are a document checker. Please review the document and identify any issues.",
    ),
    oxy.ParallelAgent(
        name="analyzer",
        desc="A tool that analyze markdown document",
        permitted_tool_name_list=["text_summarizer", "data_analyser", "document_checker"],
    ),
    oxy.WorkflowAgent(
        name="workflow_agent",
        desc="Workflow for time retrieval + document analysis + file writing",
        sub_agents=["file_agent", "time_agent", "analyzer"],
        func_workflow=workflow,
        llm_model="default_llm",
    ),
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        sub_agents=["workflow_agent"],
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello!"
        )

if __name__ == "__main__":
    asyncio.run(main())
```

[Previous: Reflexion and Redo Pattern](./reflexion.md)
[Next: Creating Flows](./preset-flows.md)
[Back to Home](../readme.md)

---

## Related Examples

- [WorkflowAgent Example](../../examples/agents/demo_workflow_agent.md) -- Demonstrates how to use WorkflowAgent to build custom workflows
