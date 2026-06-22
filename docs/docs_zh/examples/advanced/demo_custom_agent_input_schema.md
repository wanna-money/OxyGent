# 自定义 Agent 输入模式

**源文件:** `examples/advanced/demo_custom_agent_input_schema.py`

## 概述

本示例演示了如何为 WorkflowAgent 定义自定义输入模式(input_schema),使主 Agent 在调用子 Agent 时能够准确传递所需参数。当你需要一个子 Agent(或类工具 Agent)接受结构化、经过校验的输入(而非简单的查询字符串)时,该模式非常有用。

## 前置条件

- 环境变量: `DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`

## 运行方式

```bash
python -m examples.advanced.demo_custom_agent_input_schema
```

## 代码详解

### 工作流函数

```python
async def workflow(oxy_request: OxyRequest):
```

一个自定义的异步函数,接收 `OxyRequest` 对象,从中提取两个参数:

- `query` -- 用户的问题(打印到标准输出)。
- `precision` -- 需要返回的圆周率位数。

函数内部存储了一个 80 位的圆周率字符串,根据请求的精度进行截断并返回。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name`(来自环境变量) |
| `master_agent` | `ReActAgent` | `is_master=True`、`sub_agents=["math_agent"]` |
| `math_agent` | `WorkflowAgent` | `desc="A tool for pi query"`、`input_schema={...}`、`func_workflow=workflow` |

`math_agent` 上的 `input_schema` 是一个 JSON Schema 风格的字典,包含两个属性:

- `query`(必填)-- 描述: "Query question"
- `precision`(必填)-- 描述: "How many decimal places are there"

该模式会暴露给主 Agent 的 LLM,以便生成正确的结构化调用。

### 入口函数

`main()` 使用 oxy_space 创建 `MAS` 上下文,并以 `first_query="Please calculate the 20 positions of Pi"` 启动 Web 服务。主 Agent 接收到查询后,识别出 `math_agent` 可以处理该请求,并传入正确的 `query` 和 `precision` 参数进行调用。

## 核心概念

- **input_schema** -- 符合 JSON Schema 规范的字典,声明 WorkflowAgent 所需的参数。主 Agent 的 LLM 利用该模式生成正确的结构化工具调用。
- **WorkflowAgent** -- 一种将普通 Python 异步函数(`func_workflow`)封装并暴露为可调用子 Agent 的 Agent 类型。
- **OxyRequest.get_arguments()** -- 从调用方 Agent 传递的请求载荷中获取指定参数。

## 预期行为

1. Web 服务在 `127.0.0.1:8080` 启动。
2. 主 Agent 接收圆周率查询,识别出 `math_agent` 为合适的子 Agent,并传入 `query` 和 `precision` 参数进行调用。
3. `math_agent` 执行工作流函数,返回圆周率的前 20 位。
4. 主 Agent 通过 Web UI 将结果返回给用户。
