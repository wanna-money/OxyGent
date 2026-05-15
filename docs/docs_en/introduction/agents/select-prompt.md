# How to Pass Prompts to an Agent

## Using Custom Prompts

In OxyGent, you can inform agents with preset prompts. For example:

```python
text_summarizer_prompt = """
You are a document analysis expert. Users will provide you with documents. You need to analyze the text content in the documents and provide a summary.
"""

data_analyser_prompt = """
You are a data analysis expert. You need to analyze tables, charts, echart code, and other data in documents, and provide text-based analysis results.
"""

document_checker_prompt = """
You need to review the documents provided by users and try to identify issues in the document content, such as contradictions, incorrect statements, etc., to help users make improvements.
"""
```

Then, you can use the `prompt` parameter in your execution script to pass the prompt:

```python
oxy.ChatAgent(
    name="text_summarizer",
    desc="A tool that can summarize markdown text",
    prompt=text_summarizer_prompt,
),
oxy.ChatAgent(
    name="data_analyser",
    desc="A tool that can summarize echart data",
    prompt=data_analyser_prompt,
),
oxy.ChatAgent(
    name="document_checker",
    desc="A tool that can find problems in document",
    prompt=document_checker_prompt,
),
```

## Using System Preset Prompts

You can also use the following approach to call our **default prompts**:

```python
from oxygent.prompts import INTENTION_PROMPT
from oxygent.prompts import SYSTEM_PROMPT
from oxygent.prompts import SYSTEM_PROMPT_RETRIEVAL
from oxygent.prompts import MULTIMODAL_PROMPT
```

> Our default [Prompts](https://github.com/jd-opensource/OxyGent/blob/main/oxygent/prompts.py) contain critical information such as tool call formats.

> Therefore, before using custom prompts, we recommend referring to our default [Prompts](https://github.com/jd-opensource/OxyGent/blob/main/oxygent/prompts.py) to better understand how to parse LLM output and handle tool calls or answer processing.

> We also provide a property for passing your custom parsing functions for more flexible output handling. For details, please refer to [Handling Agent Output](../advanced/handle-output.md).

If you do not specify any prompts, our agents will use the system prompts by default. You can append to the system prompts:

```python
oxy.ReActAgent(
    name="time_agent",
    desc="A tool for time query.",
    additional_prompt="Do not send other information except time.",
    tools=["time_tools"],
),
```

[Previous: Select the LLM for Your Agent](./select-llm.md)
[Next: Choose Agent Types](./agent-types.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Single Agent Example](../../examples/agents/demo_single_agent.md) -- Demonstrates the `func_process_input` and `func_format_output` hooks
- [Custom LLM Parser Example](../../examples/advanced/demo_custom_llm_parser.md) -- Custom LLM output parsing
- [Live Prompts Example](../../examples/live_prompts/demo_live_prompt.md) -- Dynamic prompt management
