# Trust 模式

**源文件:** `examples/advanced/demo_trust_mode.py`

## 概述

本示例演示了 ReActAgent 上的 `trust_mode` 参数,该参数控制 LLM 的工具调用是否跳过验证直接执行。示例中配置了两个相同的 Agent -- 一个为普通模式,另一个为 Trust 模式 -- 通过对比它们回答同一时间查询时的行为差异来展示该功能。

## 前置条件

- 环境变量: `DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Node.js 运行时(用于 `uvx` 启动 MCP 时间服务器)

## 运行方式

```bash
python -m examples.advanced.demo_trust_mode
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name`(来自环境变量) |
| `time_tools` | `StdioMCPClient` | `command="uvx"`、`args=["mcp-server-time", "--local-timezone=Asia/Shanghai"]` |
| `normal_agent` | `ReActAgent` | `tools=["time_tools"]`、`llm_model="default_llm"`、`trust_mode=False` |
| `trust_agent` | `ReActAgent` | `tools=["time_tools"]`、`llm_model="default_llm"`、`trust_mode=True` |

两个 Agent 共享相同的 LLM 和 MCP 时间工具,唯一的区别在于 `trust_mode` 标志。

### 入口函数

`main()` 创建 `MAS` 上下文,通过 `mas.call()` 分别调用两个 Agent,使用相同的查询 `"What is the current time"`:

1. 调用 `normal_agent` 并打印结果。
2. 调用 `trust_agent` 并打印结果。

注意:本示例使用 `mas.call()`(编程方式调用)而非 `mas.start_web_service()`,因此以 CLI 脚本形式运行,不启动 Web 服务器。

## 核心概念

- **trust_mode=False(普通模式)** -- Agent 的工具调用决策经过标准 ReAct 验证循环。LLM 决定调用工具,框架执行工具,LLM 对观察结果进行反思后再生成最终答案。
- **trust_mode=True(Trust 模式)** -- 工具调用以更少的开销执行,更直接地信任 LLM 的决策。这可以在处理成熟、低风险的工具调用时降低延迟和 token 消耗。
- **StdioMCPClient** -- 通过标准输入输出连接 MCP 服务器。此处启动 `mcp-server-time` 提供时区感知的时间查询。
- **mas.call()** -- 一种直接调用特定命名 Agent 的编程方式,是 `chat_with_agent()` 或 Web 服务的替代方案。

## 预期行为

1. 脚本打印 `=== normal mode test ===`,随后输出普通 Agent 返回的当前时间。
2. 脚本打印 `=== trust mode test ===`,随后输出 Trust Agent 返回的当前时间。
3. 两个 Agent 都应返回正确的亚洲/上海时区当前时间,但 Trust 模式的 Agent 由于减少了验证开销,可能完成得更快。
