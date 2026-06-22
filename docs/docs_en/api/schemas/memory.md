# Memory Schemas

---
The position of the classes is:

```
oxygent/schemas/memory.py
```

---

## Introduction

This module defines the data structures for chat conversations: `Function`, `ToolCall`, `Message`, and `Memory`. These classes represent the building blocks of conversation history used by agents throughout the OxyGent framework.

## Function (BaseModel)

| Parameter   | Type  | Default    | Description                    |
| ----------- | ----- | ---------- | ------------------------------ |
| `name`      | `str` | (required) | Function name.                 |
| `arguments` | `str` | (required) | Serialized function arguments. |

## ToolCall (BaseModel)

| Parameter  | Type       | Default      | Description              |
| ---------- | ---------- | ------------ | ------------------------ |
| `id`       | `str`      | (required)   | Tool call identifier.    |
| `type`     | `str`      | `"function"` | Tool call type.          |
| `function` | `Function` | (required)   | The function being called. |

## Message (BaseModel)

### Parameters

| Parameter      | Type / Allowed value                                  | Default    | Description                           |
| -------------- | ----------------------------------------------------- | ---------- | ------------------------------------- |
| `role`         | `Literal["system", "user", "assistant", "tool"]`      | (required) | Message role.                         |
| `content`      | `Optional[Union[str, list, dict]]`                    | `None`     | Message content.                      |
| `tool_calls`   | `Optional[list[ToolCall]]`                            | `None`     | Tool calls in this message.           |
| `name`         | `Optional[str]`                                       | `None`     | Name (for tool messages).             |
| `tool_call_id` | `Optional[str]`                                       | `None`     | Tool call ID (for tool responses).    |

### Methods

| Method                                               | Coroutine (async) | Return Value     | Purpose (concise)                                         |
| ---------------------------------------------------- | ----------------- | ---------------- | --------------------------------------------------------- |
| `user_message(content)` (classmethod)                | No                | `Message`        | Factory: create a user-role message.                      |
| `system_message(content)` (classmethod)              | No                | `Message`        | Factory: create a system-role message.                    |
| `assistant_message(content)` (classmethod)           | No                | `Message`        | Factory: create an assistant-role message.                |
| `tool_message(content, name, tool_call_id)` (classmethod) | No          | `Message`        | Factory: create a tool-role message.                      |
| `from_tool_calls(tool_calls, content, **kwargs)` (classmethod) | No    | `Message`        | Create assistant message with formatted tool calls.       |
| `dict_list_to_messages(dict_list)` (staticmethod)    | No                | `list[Message]`  | Convert list-of-dicts to list-of-Messages.                |
| `to_dict()`                                          | No                | `dict`           | Convert to SDK-compatible dict (non-None fields only).    |

## Memory (BaseModel)

### Parameters

| Parameter      | Type            | Default | Description                        |
| -------------- | --------------- | ------- | ---------------------------------- |
| `messages`     | `list[Message]` | `[]`    | Stored messages.                   |
| `max_messages` | `int`           | `50`    | Maximum message buffer size.       |

### Methods

| Method                                    | Coroutine (async) | Return Value    | Purpose (concise)                                              |
| ----------------------------------------- | ----------------- | --------------- | -------------------------------------------------------------- |
| `add_message(message)`                    | No                | `None`          | Append a single message.                                       |
| `add_messages(messages)`                  | No                | `None`          | Append multiple messages.                                      |
| `clear()`                                 | No                | `None`          | Drop all stored messages.                                      |
| `get_recent_messages(n)`                  | No                | `list[Message]` | Return the `n` most recent messages.                           |
| `to_dict_list(short_memory_size=None)`    | No                | `list[dict]`    | Convert to list-of-dicts with sliding-window trimming.         |
