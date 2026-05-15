# 带反思机制的 ReAct 代理

**源文件:** `examples/agents/demo_react_agent.py`

## 概述

本示例展示了带有自定义反思（自我纠正）函数的 `ReActAgent`。代理使用推理-行动（ReAct）模式，反思回调函数验证代理的输出格式，如果响应不是纯数字则强制重试。当你需要从 LLM 获取结构化、受约束的输出时，这种模式非常有用。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包

## 运行方式

```bash
python -m examples.agents.demo_react_agent
```

## 代码详解

### 钩子函数

#### `master_reflexion(response: str, oxy_request: OxyRequest) -> str`

通过 `func_reflexion` 注册的**反思**回调。当代理产生响应后，此函数进行验证：

1. 使用正则表达式 `r"^[-+]?(\d+(\.\d*)?|\.\d+)$"` 检查响应是否为有效数字（整数或小数，可选正负号）。
2. 如果响应**不匹配**（即包含非数字文本），函数返回 `"仅回答数字"`，该字符串作为纠正反馈传回代理，触发新一轮尝试。
3. 如果响应**匹配**，函数隐式返回 `None`，表示输出可接受。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量（默认设置） |
| `master_agent` | `ReActAgent` | `llm_model="default_llm"`；`func_reflexion=master_reflexion`；`additional_prompt="请你根据我的问题，给出最优的回答"` |

### 入口函数

```python
await mas.start_web_service(first_query="1+1等于几")
```

启动 Web 服务，初始查询为 "1+1等于几"。

## 核心概念

- **ReAct 模式** -- 代理遵循推理-行动循环：对问题进行推理，采取行动（如调用工具或生成答案），观察结果，然后迭代。
- **反思（Reflexion）** -- 一种自我纠正机制。当 `func_reflexion` 返回非 None 字符串时，该字符串被视为反馈，代理将结合反馈重新尝试。
- **`additional_prompt`** -- 追加到代理的系统提示词中，在不覆盖基础提示词的情况下提供额外指令。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 首个查询 "1+1等于几" 被自动发送。
3. 代理尝试回答。如果它回复了类似 "1+1等于2" 的文本（散文形式），反思函数会拒绝并发送反馈 "仅回答数字"。
4. 代理重试，最终回复纯数字 `"2"`，通过反思验证。
5. 最终简洁的数字答案显示在 Web UI 中。
