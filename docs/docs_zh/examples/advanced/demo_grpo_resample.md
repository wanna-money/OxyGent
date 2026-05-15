# GRPO 重采样(Trace 回放用于强化学习)

**源文件:** `examples/advanced/demo_grpo_resample.py`

## 概述

本示例演示了一种适用于 GRPO(Group Relative Policy Optimization,组相对策略优化)或类似强化学习工作流的 trace 回放模式。它先运行一个多 Agent 任务,从执行 trace 中检索所有中间 LLM 节点,然后并行回放每个 LLM 节点。这样可以从相同的中间状态收集多个 Agent 行为样本,用于奖励建模或策略优化。

## 前置条件

- 环境变量: `DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`

## 运行方式

```bash
python -m examples.advanced.demo_grpo_resample
```

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
Config.set_message_is_send_tool_call(False)
Config.set_message_is_send_observation(False)
Config.set_storage_es_engine("MemoryEs")
```

- `set_agent_llm_model("default_llm")` -- 为所有 Agent 设置默认 LLM。
- `set_message_is_send_tool_call(False)` -- 禁止向前端发送工具调用消息(在批量回放时减少噪音)。
- `set_message_is_send_observation(False)` -- 禁止向前端发送观察消息。
- `set_storage_es_engine("MemoryEs")` -- 使用内存中的 Elasticsearch 替代品,而非真实的 ES 集群,将 trace 数据保存在内存中。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name`(来自环境变量) |
| `time_tools` | `preset_tools.time_tools` | 内置预设时间工具 |
| `time_agent` | `ReActAgent` | `desc="A tool that can query the time"`、`tools=["time_tools"]` |
| `file_tools` | `preset_tools.file_tools` | 内置预设文件系统工具 |
| `file_agent` | `ReActAgent` | `desc="A tool that can operate the file system"`、`tools=["file_tools"]` |
| `math_tools` | `preset_tools.math_tools` | 内置预设数学工具 |
| `math_agent` | `ReActAgent` | `desc="A tool that can perform mathematical calculations."`、`tools=["math_tools"]` |
| `master_agent` | `ReActAgent` | `is_master=True`、`sub_agents=["time_agent", "file_agent", "math_agent"]` |

### 入口函数

`main()` 执行三步工作流:

**第一步 -- 初始执行:**
```python
payload = {"query": "What time is it now? Please save it into time.txt."}
oxy_response = await mas.chat_with_agent(payload)
trace_id = oxy_response.oxy_request.current_trace_id
await mas.await_background_tasks(trace_id)
```
运行完整的多 Agent 任务并等待所有后台任务完成。

**第二步 -- 提取 LLM 节点:**
```python
res = await get_task_info(trace_id)
filterd_nodes = [node for node in res["data"]["nodes"] if node["node_type"] == "llm"]
```
使用 `get_task_info()`(来自 `oxygent.routes`)获取完整的执行 trace,然后筛选出所有 LLM 类型的节点。

**第三步 -- 并行回放:**
```python
tasks = []
for node in sorted(filterd_nodes, key=lambda x: x["create_time"]):
    payload = {"restart_node_id": node["node_id"]}
    tasks.append(mas.chat_with_agent(payload))
oxy_responses = await asyncio.gather(*tasks)
```
使用 `restart_node_id` 并行回放所有 LLM 节点。每次回放从该特定点重新执行 Agent,由于 LLM 采样的随机性,可能产生不同的输出。

## 核心概念

- **GRPO 重采样** -- 通过从同一 trace 回放 LLM 决策点,可以从相同状态收集多条轨迹样本,这是 Group Relative Policy Optimization 的关键步骤。
- **MemoryEs** -- 内存中的 Elasticsearch 替代品,无需真实 ES 集群即可存储 trace 数据,适合实验和演示。
- **get_task_info()** -- 路由工具函数,用于检索给定 `trace_id` 的完整执行 trace,包括所有节点、类型、调用方、被调用方和时间戳。
- **并行回放** -- 使用 `asyncio.gather()` 并发回放多个节点,从相同中间状态收集多样化输出。
- **await_background_tasks()** -- 等待与 trace 关联的所有后台任务完成,确保 trace 数据完整填充后再继续。

## 预期行为

1. 第一步:主 Agent 查询时间,委派给 `time_agent`,获取结果后委派给 `file_agent` 将其保存到 `time.txt`。
2. 第二步:检索执行 trace 并筛选出所有 LLM 决策节点。
3. 第三步:并行回放每个 LLM 节点。输出(由于 LLM 采样可能有所不同)逐行打印到标准输出。
