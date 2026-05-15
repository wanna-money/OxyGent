# How to Handle Agent Output?

OxyGent uses a simple JSON parser by default to handle agent output. In the default state, the instructional output format for tool calls from an Agent looks like this:

```json
{
    "think": "Your thinking (if analysis is needed)",
    "tool_name": "Tool name",
    "arguments": {
        "parameter_name": "parameter_value"
    }
}
```

If you need to customize how the agent's output is processed, you can use the following methods.

## Setting the LLM Output Format

In most cases, you can set instructions in `prompts` to make the LLM output a specific format.

For example, you can use the following format to guide the LLM to return tool call output:

```python
SYSTEM_PROMPT = """
You are a helpful assistant that can use these tools:
${tools_description}

Choose the appropriate tool based on the user's question.
If no tool is needed, respond directly.
If answering the user's question requires multiple tool calls, call only one tool at a time. After the user receives the tool result, they will provide you with feedback on the tool call result.

Important instructions:
1. When you have collected enough information to answer the user's question, please respond in the following format:
<think>Your thinking (if analysis is needed)</think>
Your answer content
2. When you find that the user's question lacks conditions, you can ask the user back, please respond in the following format:
<think>Your thinking (if analysis is needed)</think>
Your question to the user
3. When you need to use a tool, you must only respond with the exact JSON object format below, nothing else:
{
    "think": "Your thinking (if analysis is needed)",
    "tool_name": "Tool name",
    "arguments": {
        "parameter_name": "parameter_value"
    }
}

After receiving the tool's response:
1. Transform the raw data into a natural conversational response
2. The answer should be concise but rich in content
3. Focus on the most relevant information
4. Use appropriate context from the user's question
5. Avoid simply repeating the raw data

Please only use the tools explicitly defined above.
"""
```


## Setting the LLM Output Parser

`oxy.ReActAgent` supports passing a custom output parser via `func_parse_llm_response`.

For example, in OxyGent's default settings, JSON-formatted output is treated as a tool call instruction. If you want to attempt a tool call only when `tool_name` is valid, and treat JSON as plain text in other cases, you can define a custom parser as follows:

```python
import json
import yaml
import xml.etree.ElementTree as ET
from oxy.schemas import LLMResponse, LLMState

def json_parser(ori_response: str) -> LLMResponse:
    try:
        data = json.loads(ori_response)

        # Only trigger a tool call when data is a dict and tool_name is non-empty (replace with your own requirements)
        if isinstance(data, dict) and data.get("tool_name"):
            return LLMResponse(
                state=LLMState.TOOL_CALL,
                output=data,
                ori_response=ori_response
            )

        # All other JSON (including arrays or plain objects) is returned as answer text
        return LLMResponse(
            state=LLMState.ANSWER,
            output=data,
            ori_response=ori_response
        )

    except json.JSONDecodeError as e:
        return LLMResponse(
            state=LLMState.ERROR_PARSE,
            output=f"Invalid JSON: {e}",
            ori_response=ori_response
        )


```

Then, you can pass this parser to `oxy.ReActAgent`:

```python
oxy.ReActAgent(
    name="json_agent",
    desc="A tool that can convert plaintext into json text",
    func_parse_llm_response=json_parser, # key method
),
```

## Processing in MAS

OxyGent also supports using external methods to process `oxy.Response`. For example, you can customize the output format:

```python
def format_output(oxy_response: OxyResponse) -> OxyResponse:
    oxy_response.output = "Answer: " + oxy_response.output
    return oxy_response
```

Then inject this processing method into the corresponding Agent:

```python
oxy.ReActAgent(
    name="master_agent",
    sub_agents=["time_agent", "file_agent", "math_agent"],
    is_master=True,
    func_format_output=format_output, # key method
    timeout=100,
    llm_model="default_llm",
),
```
### Notes
1. **`func_parse_llm_response`**: Used for custom parsing of LLM output. It can handle tool call results or plain text as needed.
2. **`func_format_output`**: This method is used to customize the output format of `oxy.Response`, helping you control how the final result is presented.

[Previous: Processing Queries and Prompts](./process-input.md)
[Next: Reflexion and Redo Pattern](./reflexion.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Custom LLM Parser Example](../../examples/advanced/demo_custom_llm_parser.md) -- Demonstrates how to customize the LLM output parser
