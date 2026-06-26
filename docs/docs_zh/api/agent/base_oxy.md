# Oxy

---
该类在类层次结构中的位置：

```markdown
[Oxy](./base_oxy.md)
├── [BaseFlow](./base_flow.md)
│   └── [BaseAgent](./base_agent.md)
│       ├── [LocalAgent](./local_agent.md)
│       │   ├── [ChatAgent](./chat_agent.md)
│       │   │   └── [RAGAgent](./rag_agent.md)
│       │   ├── [ReActAgent](./react_agent.md)
│       │   │   ├── [ShellUseAgent](./shell_use_agent.md)
│       │   │   └── [SkillAgent](./skill_agent.md)
│       │   ├── [ParallelAgent](./parallel_agent.md)
│       │   ├── [WorkflowAgent](./workflow_agent.md)
│       │   └── [PlanAndSolveAgent](./plan_and_solve_agent.md)
│       └── [RemoteAgent](./remote_agent.md)
│           ├── [SSEOxyGent](./sse_oxy_agent.md)
│           └── [A2AClientAgent](./a2a_client_agent.md)
└── [BaseTool](../tools/base_tools.md)
```
---

## 简介
`Oxy` 是 OxyGent 系统中所有 Agent 和工具的抽象基类。

该类定义了核心执行生命周期、权限管理、消息处理和数据持久化模式。它为本地和远程执行提供了统一接口，并具备全面的日志记录和错误处理能力。

## 参数
| 参数                               | 类型 / 允许的值        | 默认值                                       | 描述                                |
| -------------------------------- | -------------------- | ------------------------------------------ | ---------------------------------- |
| `name`                           | `str`                | 必须赋值                                    | Agent/工具的标识符                   |
| `desc`                           | `str`                | `""`                                       | 人类可读的描述信息                    |
| `category`                       | `str`                | `"tool"`                                   | 类别分类                            |
| `class_name`                     | `Optional[str]`      | `None`                                     | 类名（初始化后自动填充）              |
| `input_schema`                   | `dict[str, Any]`     | `{}`                                       | 输入模式定义                         |
| `desc_for_llm`                   | `str`                | `""`                                       | 展示给 LLM 的描述信息                |
| `is_entrance`                    | `bool`               | `False`                                    | 是否为 MAS 的入口点                  |
| `is_permission_required`         | `bool`               | `False`                                    | 执行是否需要权限                      |
| `is_save_data`                   | `bool`               | `True`                                     | 是否将执行数据持久化到存储            |
| `permitted_tool_name_list`       | `list`               | `[]`                                       | 该 Agent/工具可调用的工具列表         |
| `permitted_oxy`                  | `list`               | `[]`                                       | 额外的工具权限                       |
| `is_send_tool_call`              | `bool`               | `Config.get_message_is_send_tool_call()`   | 是否发送 *tool\_call* 消息           |
| `is_send_observation`            | `bool`               | `Config.get_message_is_send_observation()` | 是否发送 *observation* 消息          |
| `is_send_answer`                 | `bool`               | `Config.get_message_is_send_answer()`      | 是否发送 *answer* 消息               |
| `is_detailed_tool_call`          | `bool`               | `Config.get_log_is_detailed_tool_call()`   | 详细的 *tool\_call* 日志记录          |
| `is_detailed_observation`        | `bool`               | `Config.get_log_is_detailed_observation()` | 详细的 *observation* 日志记录         |
| `func_process_input`             | `Callable`           | `lambda x: x`                              | 请求预处理钩子                       |
| `func_process_output`            | `Callable`           | `lambda x: x`                              | 响应后处理钩子                       |
| `func_format_input`              | `Optional[Callable]` | `lambda x: x`                              | 为被调用方格式化请求                  |
| `func_format_output`             | `Optional[Callable]` | `lambda x: x`                              | 为调用方格式化响应                    |
| `func_execute`                   | `Optional[Callable]` | `None`                                     | 自定义执行入口                       |
| `func_interceptor`               | `Optional[Callable]` | `None`                                     | 请求拦截器钩子                       |
| `system_args`                    | `list[str]`          | `[]`                                       | 从 input_schema 中提取的系统级参数 |
| `preceding_oxy`                  | `Optional[list[str]]`| `[]`                                       | 在当前 Oxy 之前必须调用的 Oxy 名称列表 |
| `preceding_placeholder`          | `str`                | `"preceding_text"`                         | 用于注入前置 Oxy 输出的参数键名 |

> 所有 `func_*` 钩子参数均支持同步和异步函数。同步函数会在初始化时通过 `ensure_async()` 自动包装为异步函数。
| `mas`                            | `Optional[Any]`      | `None`                                     | 对 MAS 实例的引用                    |
| `friendly_error_text`            | `Optional[str]`      | `None`                                     | 面向用户的备用错误信息                |
| `semaphore`                      | `int`                | `16`                                       | 最大并发执行数                       |
| `timeout`                        | `float`              | `3600`                                     | 超时时间（秒）                       |
| `retries`                        | `int`                | `2`                                        | 失败重试次数                         |
| `delay`                          | `float`              | `1.0`                                      | 重试间隔（秒）                       |

## 方法
| 方法                                  | 协程（async）        | 用途（简要）                                             |
| ----------------------------------- | ----------------- | -------------------------------------------------------- |
| `__init__(**kwargs)`                | 否                | 构造对象，初始化信号量和 LLM 描述                          |
| `model_post_init(__context)`        | 否                | 在 Pydantic 初始化之后填充 `class_name`                   |
| `set_mas(mas)`                      | 否                | 绑定 MAS 引用                                            |
| `add_permitted_tool(tool_name)`     | 否                | 添加单个工具到权限列表                                     |
| `add_permitted_tools(tool_names)`   | 否                | 批量添加工具权限                                          |
| `_set_desc_for_llm()`               | 否                | 构建人类/LLM 友好的参数文档                                |
| `init()`                            | 是                | 在继承类中实现                                            |
| `_pre_process(oxy_request)`         | 是                | 填充 ID、栈信息，运行输入钩子                              |
| `_pre_log(oxy_request)`             | 是                | 生成 *tool\_call* 日志条目                                |
| `_request_interceptor(oxy_request)` | 是                | 在重启时恢复缓存的输出                                     |
| `_pre_save_data(oxy_request)`       | 是                | 持久化初始节点元数据                                       |
| `_format_input(oxy_request)`        | 是                | 应用调用方侧的格式化                                       |
| `_pre_send_message(oxy_request)`    | 是                | 将 *tool\_call* 消息转发到前端                             |
| `_before_execute(oxy_request)`      | 是                | 主执行之前的自定义钩子                                     |
| `_execute(oxy_request)`             | 是                | 在继承类中实现                                            |
| `_handle_exception(e)`              | 是                | 在继承类中实现                                            |
| `_after_execute(oxy_response)`      | 是                | 主执行之后的自定义钩子                                     |
| `_post_process(oxy_response)`       | 是                | 应用响应后处理                                            |
| `_post_log(oxy_response)`           | 是                | 生成 *observation* 日志                                   |
| `_post_save_data(oxy_response)`     | 是                | 持久化最终节点数据                                         |
| `_format_output(oxy_response)`      | 是                | 最终格式化和友好错误替换                                    |
| `_post_send_message(oxy_response)`  | 是                | 向前端发送 *observation* / *answer*                        |
| `execute(oxy_request)`              | 是                | 编排完整的异步生命周期（含重试）                            |

> 方法体仅为 `pass` 的方法标记为"在继承类中实现"，表示子类必须实现它们。

## 使用方式

`Oxy` 类必须被继承使用。
