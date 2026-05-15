# LLM Schemas

---
The position of the classes is:

```
oxygent/schemas/llm.py
```

---

## Introduction

This module defines the LLM response state enumeration and the parsed response container. These are used by agents to interpret the output of LLM calls — determining whether the LLM wants to call a tool, provide an answer, or encountered a parsing error.

## LLMState (Enum)

| Member        | Value            | Description                          |
| ------------- | ---------------- | ------------------------------------ |
| `TOOL_CALL`   | `"tool_call"`    | LLM wants to invoke a tool.         |
| `ANSWER`      | `"answer"`       | LLM is providing a final answer.    |
| `ERROR_PARSE` | `"error_parse"`  | Failed to parse the LLM output.     |
| `ERROR_CALL`  | `"error_call"`   | Error occurred during the LLM call. |

## LLMResponse (BaseModel)

### Parameters

| Parameter      | Type / Allowed value         | Default    | Description                                      |
| -------------- | ---------------------------- | ---------- | ------------------------------------------------ |
| `state`        | `LLMState`                   | (required) | Parsed state of the LLM response.                |
| `output`       | `Union[str, list, dict]`     | (required) | Parsed output content.                           |
| `ori_response` | `str`                        | `""`       | Original raw LLM response text before parsing.   |
