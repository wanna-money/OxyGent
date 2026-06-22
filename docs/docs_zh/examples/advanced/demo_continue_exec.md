# 断点续执行(从节点重启)

**源文件:** `examples/advanced/demo_continue_exec.py`

## 概述

本示例演示了"断点续执行"或"从节点重启"功能,允许从某个中间节点重新运行 Agent 的工作流。在初始查询完成后,你可以提供 `restart_node_id`(以及可选的 `restart_node_output`)从指定节点开始回放执行。这对于调试、测试替代工具输出或从执行中途的故障中恢复非常有用。

## 前置条件

- 环境变量: `DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Node.js 运行时(用于 `uvx` 启动 MCP 时间服务器)

## 运行方式

```bash
python -m examples.advanced.demo_continue_exec
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name`(来自环境变量) |
| `time_tools` | `StdioMCPClient` | `command="uvx"`、`args=["mcp-server-time", "--local-timezone=Asia/Shanghai"]` |
| `time_agent` | `ReActAgent` | `desc="A tool for time query."`、`tools=["time_tools"]`、`llm_model="default_llm"` |

### 入口函数

`main()` 演示了两阶段执行模式:

**第一阶段 -- 初始执行:**
```python
payload = {"query": "Get what time it is Asia/Shanghai"}
oxy_response = await mas.chat_with_agent(payload=payload)
```
正常运行时间 Agent 并打印结果。

**第二阶段 -- 从节点重启(已注释):**
```python
payload = {
    "restart_node_id": "BcgSFR4Ls3nHCkFm",   # 第一次执行中的 node_id
    "restart_node_output": '{"timezone": "Asia/Shanghai", ...}',  # 可选的输出覆盖
}
oxy_response = await mas.chat_with_agent(payload=payload)
```
使用时需取消注释并提供第一次运行 trace 中的有效 `restart_node_id`。`restart_node_output` 字段是可选的:如果提供,则替换该节点的原始输出,让你可以测试 Agent 对不同中间结果的反应。

## 核心概念

- **restart_node_id** -- 要从其重启的中间执行节点标识符,从上次运行的 trace 数据中获取。
- **restart_node_output** -- 节点输出的可选覆盖值。如果省略,将自动从数据库中检索原始查询,节点正常重新执行。
- **Trace 回放** -- 框架会存储执行 trace(节点、工具调用、LLM 响应),可以从任意点开始回放,使得无需重新运行整个链即可迭代 Agent 行为。
- **chat_with_agent()** -- MAS 的核心入口点,用于运行查询。同时支持标准查询和重启载荷。

## 预期行为

1. 第一阶段执行:时间 Agent 查询亚洲/上海的当前时间并打印结果。
2. 第二阶段(取消注释后):从指定节点恢复执行,可选择使用覆盖的输出,Agent 基于该节点的数据生成新的最终答案。
