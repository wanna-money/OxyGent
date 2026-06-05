# Oxy Schemas

---
类所在位置：

```
oxygent/schemas/oxy.py
```

---

## 简介

本模块定义了 OxyGent 框架中用于请求/响应处理和状态管理的核心数据类。包括 `OxyState`（生命周期枚举）、`OxyRequest`（携带 trace、caller/callee 及参数的请求对象）、`OxyResponse`（响应封装）以及 `OxyOutput`（带附件的结构化输出）。

## OxyState

| 参数                                 | 类型 / 允许值                                                                                | 默认值  | 描述                                             |
| ------------------------------------ | -------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------ |
| *无数据类字段；枚举成员：*           | 允许值：`CREATED`、`RUNNING`、`COMPLETED`、`FAILED`、`PAUSED`、`SKIPPED`、`CANCELED`          | —       | 用于标记节点状态的生命周期状态。                 |


## OxyRequest (Pydantic BaseModel)

### 参数

| 参数                       | 类型 / 允许值                | 默认值                         | 描述                                        |
| -------------------------- | ---------------------------- | ------------------------------ | ------------------------------------------- |
| `request_id`               | `str`                        | 自动生成 (ShortUUID, 22)      | 客户端 ID，用于追踪/恢复。                  |
| `group_id`                 | `str`                        | 自动生成 (ShortUUID, 16)      | 用于关联相关 trace 的静态标识符。            |
| `from_trace_id`            | `Optional[str]`              | `""`                           | 父节点的 trace ID。                          |
| `current_trace_id`         | `Optional[str]`              | 自动生成 (ShortUUID, 16)      | 当前节点的唯一 ID。                          |
| `reference_trace_id`       | `Optional[str]`              | `""`                           | 用于特殊流程的引用指针。                     |
| `restart_node_id`          | `Optional[str]`              | `""`                           | 需要重新启动的节点 ID。                      |
| `restart_node_output`      | `Optional[str]`              | `""`                           | 重启时缓存的输出。                           |
| `restart_node_order`       | `Optional[str]`              | `""`                           | 重启时的顺序索引。                           |
| `input_md5`                | `Optional[str]`              | `""`                           | 输入内容的哈希值。                           |
| `root_trace_ids`           | `list`                       | `[]`                           | 会话树的所有根节点 ID。                      |
| `mas`                      | `Optional[Any]`              | `None`                         | MAS 运行时句柄（不会被序列化）。             |
| `caller`                   | `Optional[str]`              | `"user"`                       | 调用方 Oxy 的名称。                          |
| `callee`                   | `Optional[str]`              | `""`                           | 被调用方 Oxy 的名称。                        |
| `call_stack`               | `list[str]`                  | `["user"]`                     | 调用方名称栈。                               |
| `node_id_stack`            | `list[str]`                  | `[""]`                         | 节点 ID 栈。                                 |
| `father_node_id`           | `Optional[str]`              | `""`                           | 父节点 ID。                                  |
| `pre_node_ids`             | `Optional[list[str] \| str]` | `[]`                           | 前驱节点 ID。                                |
| `latest_node_ids`          | `Optional[list[str] \| str]` | `[]`                           | 最新的并行节点 ID。                          |
| `caller_category`          | `Optional[str]`              | `"user"`                       | 调用方类别（user/agent/tool）。              |
| `callee_category`          | `Optional[str]`              | `""`                           | 被调用方类别。                               |
| `node_id`                  | `Optional[str]`              | `""`                           | 当前节点 ID。                                |
| `arguments`                | `dict`                       | `{}`                           | 调用参数（用户输入、工具参数）。             |
| `is_save_history`          | `bool`                       | `True`                         | 是否持久化对话历史。                         |
| `shared_data`              | `dict`                       | `{}`                           | 在 trace 内共享的临时数据区。                |
| `parallel_id`              | `Optional[str]`              | `""`                           | 并行组标识符。                               |
| `parallel_dict`            | `Optional[dict]`             | `{}`                           | 用于并行调度的内部映射。                     |

### 方法

| 方法                                                       | 协程 (async) | 返回值        | 用途（简述）                                                                                            |
| ---------------------------------------------------------- | ------------ | ------------- | ------------------------------------------------------------------------------------------------------- |
| `session_name` (property)                                  | 否           | `str`         | 便捷的会话键：`"caller__callee"`。                                                                      |
| `set_mas(self, mas)`                                       | 否           | `None`        | 绑定 MAS 运行时句柄。                                                                                   |
| `get_oxy(self, oxy_name)`                                  | 否           | `Any`         | 在 MAS 注册表中按名称查找 Oxy。                                                                         |
| `has_oxy(self, oxy_name)`                                  | 否           | `bool`        | 检查 MAS 注册表中是否存在指定 Oxy。                                                                     |
| `__deepcopy__(self, memo)`                                 | 否           | `OxyRequest`  | 自定义深拷贝，保留 MAS/shared\_data 并重置并行信息。                                                    |
| `clone_with(self, **kwargs)`                               | 否           | `OxyRequest`  | 深拷贝后原子性地覆盖指定字段。                                                                          |
| `call(self, **kwargs)`                                     | 是           | `OxyResponse` | 带覆盖参数的克隆、权限检查、超时保护、`retrieve_tools` 特殊处理，然后执行。                              |
| `start(self)`                                              | 是           | `OxyResponse` | 入口：使用当前请求执行目标 callee 的 `execute`。                                                        |
| `send_message(self, message)`                              | 是           | `None`        | 通过 MAS/Redis 向前端推送结构化事件。                                                                   |
| `set_query(self, query, master_level=False)`               | 否           | `None`        | 在主节点（`shared_data`）或当前节点（`arguments`）层级存储查询。                                        |
| `get_query(self, master_level=False)`                      | 否           | `str`         | 从主节点或当前节点范围获取查询。                                                                        |
| `get_full_parts(self, master_level=False)`                 | 否           | `list`        | 以 A2A 风格的有序部分返回查询（`{part: {...}}` 列表）。                                                 |
| `has_short_memory(self, master_level=False)`               | 否           | `bool`        | 在指定范围内是否存在短期记忆。                                                                          |
| `set_short_memory(self, short_memory, master_level=False)` | 否           | `None`        | 在指定范围内设置短期记忆。                                                                              |
| `get_short_memory(self, master_level=False)`               | 否           | `list`        | 获取指定范围内的短期记忆。                                                                              |
| `get_request_id(self)`                                     | 否           | `str`         | 返回当前 `request_id`。                                                                                 |
| `set_request_id(self, request_id)`                         | 否           | `None`        | 手动覆盖 `request_id`。                                                                                 |
| `get_group_id(self)`                                       | 否           | `str`         | 返回 `group_id`。                                                                                       |
| `set_group_id(self, request_id)`                           | 否           | `None`        | 手动覆盖 `group_id`。                                                                                   |

## OxyResponse (Pydantic BaseModel)

### 参数

| 参数          | 类型 / 允许值          | 默认值           | 描述                                         |
| ------------- | ---------------------- | ---------------- | -------------------------------------------- |
| `state`       | `OxyState`             | 必须赋值         | 任务的最终状态。                             |
| `output`      | `Any`                  | 必须赋值         | 面向用户的输出内容或错误信息。               |
| `extra`       | `dict`                 | `{}`             | 可选的元数据（如 token 数、延迟等）。        |
| `oxy_request` | `Optional[OxyRequest]` | `None`           | 原始请求的回传。                             |

### 方法

| 方法            | 协程 (async) | 返回值       | 用途（简述）                                                |
| --------------- | ------------ | ------------ | ----------------------------------------------------------- |
| *未声明方法*    | —            | —            | 数据容器模型；依赖 Pydantic 自动生成的方法。                |

## OxyOutput (Pydantic BaseModel)


### 参数

| 参数          | 类型 / 允许值      | 默认值           | 描述                             |
| ------------- | -------------------- | ---------------- | -------------------------------- |
| `result`      | `Any`                | 必须赋值         | 主要结果内容。                   |
| `attachments` | `list`               | `[]`             | 附件描述列表。                   |
