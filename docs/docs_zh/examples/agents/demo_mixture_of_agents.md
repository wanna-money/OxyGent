# 混合代理（Mixture of Agents）

**源文件:** `examples/agents/demo_mixture_of_agents.py`

## 概述

本示例演示了使用 `team_size` 参数实现的混合代理（Mixture of Agents, MoA）模式。在代理上设置 `team_size=N` 会创建 N 个并行实例同时处理相同的查询，生成一组响应并聚合为单一答案。结合较高的温度设置，可以产生多样化且高质量的响应。这种模式非常适合通过集成方法提高响应的可靠性和质量。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包

## 运行方式

```bash
python -m examples.agents.demo_mixture_of_agents
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量；`llm_params={"temperature": 0.7}` |
| `qa_agent` | `ChatAgent` | `llm_model="default_llm"`；`team_size=4` |

两个关键设置：

- **`temperature=0.7`** -- 适度偏高的温度鼓励并行实例之间的多样性。每个实例对相同查询会生成稍有不同的响应。
- **`team_size=4`** -- 创建 `qa_agent` 的 4 个并行实例。所有 4 个实例并发处理相同的输入，它们的响应被聚合为单一最终答案。

### 入口函数

```python
await mas.start_web_service(first_query="What is the Agent?")
```

启动 Web 服务，初始查询为一个适合多角度回答的概念性问题。

## 核心概念

- **混合代理（MoA）** -- 一种集成技术，多个代理实例独立处理相同的查询。多样化的输出随后被综合为一个更稳健的答案。
- **`team_size`** -- 要创建的并行代理实例数量。当 `team_size > 1` 时，框架自动并发运行 N 个代理副本并聚合结果。
- **温度促进多样性** -- 设置 `temperature=0.7`（而非低值如 0.01）确保每个并行实例生成有意义的不同响应，使集成更有价值。
- **聚合** -- 框架自动处理多个响应的聚合，结合每个实例输出的最佳元素。
- **最简配置** -- 实现 MoA 只需在现有代理上设置 `team_size` 并调整温度。无需额外的代理或编排逻辑。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 查询 "What is the Agent?" 被发送。
3. `qa_agent` 的四个并行实例同时处理查询。
4. 由于 `temperature=0.7`，每个实例生成稍有不同的响应。
5. 四个响应被聚合为一个综合答案。
6. 聚合后的答案显示在 Web UI 中，通常比任何单个实例的响应更丰富、更均衡。
