# Custom LLM Response Parser (XML Format)

**Source:** `examples/advanced/demo_custom_llm_parser.py`

## Overview

This example shows how to replace the default JSON-based LLM response parser with a custom XML-based parser using the `func_parse_llm_response` parameter. This is useful when working with LLMs that produce non-standard output formats, or when you want fine-grained control over how agent responses are interpreted.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Node.js runtime (for `npx` to run the MCP filesystem server and `uvx` for the time server)

## How to Run

```bash
python -m examples.advanced.demo_custom_llm_parser
```

## Code Walkthrough

### Configuration

```python
Config.set_agent_llm_model("default_llm")
```

Sets the default LLM model for all agents globally.

### Custom XML Parser

```python
def parse_llm_response(ori_response: str, oxy_request: OxyRequest = None) -> LLMResponse:
```

This function replaces the default parser. It expects the LLM to output in one of two XML formats:

**Tool call format:**
```xml
<tool>
  <think>reasoning</think>
  <tool_name>name</tool_name>
  <arguments>
    <param1>value1</param1>
  </arguments>
</tool>
```

**Answer format:**
```xml
<answer>
  <think>reasoning</think>
  Your answer here
</answer>
```

The parser uses `xml.etree.ElementTree` to parse the response and returns an `LLMResponse` with:
- `LLMState.TOOL_CALL` -- when a `<tool_name>` element is found, extracting the tool name and arguments dict.
- `LLMState.ANSWER` -- when no tool name is found, extracting the answer text (minus any `<think>` content).
- `LLMState.ERROR_PARSE` -- on any parsing exception.

### Custom Agent Prompt

```python
NOTE_AGENT_PROMPT = """\
You are a helpful note-taking assistant. ...
IMPORTANT: Use the following XML formats for your responses:
...
"""
```

The prompt instructs the LLM to:
1. Act as a note-taking assistant that records memos in a specific format.
2. First get the current time (Asia/Shanghai timezone), then save the note to `local_file/note.txt`.
3. Use the XML response format defined above instead of the default JSON format.
4. The `${tools_description}` placeholder is automatically replaced with the actual tool descriptions at runtime.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from environment; `llm_params={"temperature": 0.1}` |
| `time_tools` | `StdioMCPClient` | `command="uvx"`, `args=["mcp-server-time", "--local-timezone=Asia/Shanghai"]` |
| `file_tools` | `StdioMCPClient` | `command="npx"`, `args=["-y", "@modelcontextprotocol/server-filesystem", "./local_file"]` |
| `note_agent` | `ReActAgent` | `prompt=NOTE_AGENT_PROMPT`, `tools=["time_tools", "file_tools"]`, `func_parse_llm_response=parse_llm_response` |
| `master_agent` | `ReActAgent` | `is_master=True`, `sub_agents=["note_agent"]` |

### Entry Point

`main()` creates a `MAS` context and starts the web service with `first_query="Save a memo: team standup at 3 PM in room 618"`.

## Key Concepts

- **func_parse_llm_response** -- A callback parameter on ReActAgent that lets you replace the default JSON response parser with any custom function. The function receives the raw LLM output string and must return an `LLMResponse` object.
- **LLMResponse** -- A structured object containing `state` (TOOL_CALL, ANSWER, or ERROR_PARSE), `output` (parsed content), and `ori_response` (the raw string).
- **LLMState** -- An enum defining the possible states of a parsed LLM response: `TOOL_CALL`, `ANSWER`, `ERROR_PARSE`.
- **Custom Prompt with XML Instructions** -- When using a custom parser, the agent's prompt must instruct the LLM to output in the expected format.
- **${tools_description}** -- A template variable in the prompt that the framework replaces with the actual descriptions of available tools.

## Expected Behavior

1. The web service starts on `127.0.0.1:8080`.
2. The master agent delegates the memo task to `note_agent`.
3. The note agent instructs the LLM to use XML format. The LLM first calls `time_tools` (via XML tool call) to get the current time.
4. The LLM then calls `file_tools` (via XML tool call) to save the formatted memo to `local_file/note.txt`.
5. The note agent returns a confirmation to the user via the web UI.
