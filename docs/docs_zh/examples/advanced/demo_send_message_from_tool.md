# 工具内发送消息(含任务中断)

**源文件:** `examples/advanced/demo_send_message_from_tool.py`

## 概述

本示例演示了工具函数如何直接向用户发送消息(通过 SSE/Web UI)以及在执行过程中中断 Agent 任务。当工具产生的结果需要立即呈现给用户、而无需等待 Agent 完整推理周期完成时,该模式非常有用。

## 前置条件

- 环境变量: `DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`

## 运行方式

```bash
python -m examples.advanced.demo_send_message_from_tool
```

## 代码详解

### FunctionHub 与工具定义

```python
fh_math_tools = oxy.FunctionHub(name="math_tools")

@fh_math_tools.tool(description="A tool that can calculate the value of pi.")
async def calc_pi(
    prec: int = Field(description="how many decimal places"),
    oxy_request: OxyRequest = Field(description="The oxy request"),
) -> float:
```

创建了一个名为 `math_tools` 的 `FunctionHub`,并在其上注册了 `calc_pi` 工具。该工具:

1. 接受 `prec`(精度/小数位数)和 `oxy_request`(由框架自动注入)。
2. 使用 Ramanujan 级数和 Python 的 `Decimal` 库进行任意精度的圆周率计算。
3. **直接向前端发送消息:** `await oxy_request.send_message({"type": "answer", "content": result})` -- 通过 SSE 立即将结果推送到 Web UI。
4. **中断 Agent 任务:** `await oxy_request.break_task()` -- 阻止 Agent 在工具返回后继续 ReAct 循环。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name`(来自环境变量) |
| `math_tools` | `FunctionHub` | 包含 `calc_pi` 工具 |
| `master_agent` | `ReActAgent` | `tools=["math_tools"]`、`llm_model="default_llm"` |

### 入口函数

`main()` 创建 `MAS` 上下文并以 `first_query="Please calculate the 20 positions of Pi"` 启动 Web 服务。

## 核心概念

- **oxy_request.send_message()** -- 直接向前端(Web UI,通过 SSE)发送消息载荷。消息字典可以包含 `type` 和 `content` 字段,允许工具实时向用户传达结果。
- **oxy_request.break_task()** -- 中断当前 Agent 任务,阻止后续 ReAct 迭代。调用后,Agent 执行停止,工具的消息成为最终输出。
- **FunctionHub** -- 通过 `@fh.tool()` 装饰器将 Python 函数注册为工具的容器。函数可以使用 Pydantic `Field` 注解来描述参数。
- **OxyRequest 注入** -- 在函数参数中包含 `oxy_request: OxyRequest`,框架会自动将当前请求上下文注入工具函数。

## 预期行为

1. Web 服务在 `127.0.0.1:8080` 启动。
2. 主 Agent 接收圆周率查询,以 `prec=20` 调用 `calc_pi` 工具。
3. 工具计算圆周率,直接将结果发送到 Web UI,并中断任务。
4. 用户在 Web UI 中立即看到圆周率值,Agent 不会另外生成最终答案。
