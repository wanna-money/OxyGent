# Memory Schemas

---
类所在位置：

```
oxygent/schemas/memory.py
```

---

## 简介

本模块定义了聊天对话的数据结构：`Function`、`ToolCall`、`Message` 和 `Memory`。这些类代表了 OxyGent 框架中 Agent 所使用的对话历史的基本构建单元。

## Function (BaseModel)

| 参数        | 类型  | 默认值     | 描述                         |
| ----------- | ----- | ---------- | ---------------------------- |
| `name`      | `str` | （必填）   | 函数名称。                   |
| `arguments` | `str` | （必填）   | 序列化的函数参数。           |

## ToolCall (BaseModel)

| 参数       | 类型       | 默认值       | 描述                     |
| ---------- | ---------- | ------------ | ------------------------ |
| `id`       | `str`      | （必填）     | 工具调用标识符。         |
| `type`     | `str`      | `"function"` | 工具调用类型。           |
| `function` | `Function` | （必填）     | 被调用的函数。           |

## Message (BaseModel)

### 参数

| 参数           | 类型 / 允许值                                         | 默认值     | 描述                              |
| -------------- | ----------------------------------------------------- | ---------- | --------------------------------- |
| `role`         | `Literal["system", "user", "assistant", "tool"]`      | （必填）   | 消息角色。                        |
| `content`      | `Optional[Union[str, list, dict]]`                    | `None`     | 消息内容。                        |
| `tool_calls`   | `Optional[List[ToolCall]]`                            | `None`     | 此消息中的工具调用。              |
| `name`         | `Optional[str]`                                       | `None`     | 名称（用于工具消息）。            |
| `tool_call_id` | `Optional[str]`                                       | `None`     | 工具调用 ID（用于工具响应）。     |

### 方法

| 方法                                                       | 协程 (async) | 返回值           | 用途（简述）                                              |
| ------------------------------------------------------------ | ------------ | ---------------- | --------------------------------------------------------- |
| `user_message(content)` (classmethod)                        | 否           | `Message`        | 工厂方法：创建 user 角色消息。                            |
| `system_message(content)` (classmethod)                      | 否           | `Message`        | 工厂方法：创建 system 角色消息。                          |
| `assistant_message(content)` (classmethod)                   | 否           | `Message`        | 工厂方法：创建 assistant 角色消息。                       |
| `tool_message(content, name, tool_call_id)` (classmethod)    | 否           | `Message`        | 工厂方法：创建 tool 角色消息。                            |
| `from_tool_calls(tool_calls, content, **kwargs)` (classmethod) | 否         | `Message`        | 创建包含格式化工具调用的 assistant 消息。                 |
| `dict_list_to_messages(dict_list)` (staticmethod)            | 否           | `List[Message]`  | 将字典列表转换为 Message 列表。                           |
| `to_dict()`                                                  | 否           | `dict`           | 转换为 SDK 兼容的字典（仅包含非 None 字段）。            |

## Memory (BaseModel)

### 参数

| 参数           | 类型            | 默认值  | 描述                               |
| -------------- | --------------- | ------- | ---------------------------------- |
| `messages`     | `List[Message]` | `[]`    | 存储的消息。                       |
| `max_messages` | `int`           | `50`    | 最大消息缓冲区大小。              |

### 方法

| 方法                                      | 协程 (async) | 返回值          | 用途（简述）                                                   |
| ----------------------------------------- | ------------ | --------------- | -------------------------------------------------------------- |
| `add_message(message)`                    | 否           | `None`          | 追加单条消息。                                                 |
| `add_messages(messages)`                  | 否           | `None`          | 追加多条消息。                                                 |
| `clear()`                                 | 否           | `None`          | 清空所有存储的消息。                                           |
| `get_recent_messages(n)`                  | 否           | `List[Message]` | 返回最近的 `n` 条消息。                                       |
| `to_dict_list(short_memory_size=None)`    | 否           | `List[dict]`    | 转换为字典列表，支持滑动窗口裁剪。                             |
