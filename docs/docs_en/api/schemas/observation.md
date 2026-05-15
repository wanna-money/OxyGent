# Observation Schemas

---
The position of the classes is:

```
oxygent/schemas/observation.py
```

---

## Introduction

This module defines the data structures for tool execution observations. An `Observation` collects one or more `ExecResult` entries — each representing the output of a single tool call — and provides formatting for display.

## ExecResult (BaseModel)

| Parameter      | Type          | Default    | Description                           |
| -------------- | ------------- | ---------- | ------------------------------------- |
| `executor`     | `str`         | (required) | Name of the tool/executor.            |
| `oxy_response` | `OxyResponse` | (required) | The response returned by the tool.    |

## Observation (BaseModel)

### Parameters

| Parameter      | Type               | Default | Description                              |
| -------------- | ------------------ | ------- | ---------------------------------------- |
| `exec_results` | `List[ExecResult]` | `[]`    | List of individual tool execution results. |

### Methods

| Method                              | Coroutine (async) | Return Value | Purpose (concise)                                              |
| ----------------------------------- | ----------------- | ------------ | -------------------------------------------------------------- |
| `add_exec_result(exec_result)`      | No                | `None`       | Append an execution result.                                    |
| `to_str(is_prefix_included=True)`   | No                | `str`        | Format all results as human-readable string with optional tool name prefix. |
