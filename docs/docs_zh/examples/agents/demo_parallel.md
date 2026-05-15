# 并行代理（专家评审团）

**源文件:** `examples/agents/demo_parallel.py`

## 概述

本示例展示了 `ParallelAgent`，它将单个查询同时分发给多个专家代理并汇总它们的响应。四个专业的 `ChatAgent` 实例（技术、商业、风险和法律专家）并行评估一个商业提案，`ParallelAgent` 将所有分析汇集为统一的响应。这种模式非常适合多角度评估、专家评审团以及任何需要对同一输入获取多元观点的场景。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包

## 运行方式

```bash
python -m examples.agents.demo_parallel
```

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
```

为所有代理设置全局默认 LLM 模型。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量 |
| `tech_expert` | `ChatAgent` | `prompt`：高级技术架构师；评估技术栈、架构、挑战、资源；输出可行性评分 (1-10) |
| `business_expert` | `ChatAgent` | `prompt`：商业分析师；评估市场机会、商业模式、投资回报率、上市策略；输出可行性评分 (1-10) |
| `risk_expert` | `ChatAgent` | `prompt`：风险管理专家；分析技术、市场、运营和合规风险；评定概率/影响/等级 |
| `legal_expert` | `ChatAgent` | `prompt`：AI 产品法律专家；分析数据合规、AI 治理、知识产权保护、合同；提供法律风险清单 |
| `expert_panel` | `ParallelAgent` | `permitted_tool_name_list=["tech_expert", "business_expert", "risk_expert", "legal_expert"]`；`is_master=True` |

每个专家代理都有详细的系统提示词，将其限制在特定的分析领域。提示词指示每位专家输出结构化的评估，包含评分和建议。

### 入口函数

`main()` 函数定义了关于构建 AI 客服系统的详细商业查询：

```python
query = (
    "We are a mid-sized e-commerce company (50 support staff, 5000+ daily inquiries). "
    "We want to build an AI customer service system that auto-handles 80%+ common questions, "
    ...
    "Please evaluate whether we should proceed."
)
```

此查询通过 `mas.start_web_service(first_query=query)` 发送。

## 核心概念

- **`ParallelAgent`** -- 使用 `asyncio` 将相同查询并发分发给 `permitted_tool_name_list` 中列出的所有代理，然后汇总结果。
- **`permitted_tool_name_list`** -- `ParallelAgent` 将并行调用的代理/工具名称列表。尽管名称中包含 "tool"，但它也适用于代理（在 OxyGent 中代理被视为可调用工具）。
- **专家专业化** -- 每个 `ChatAgent` 通过其提示词被限制在单一评估维度，防止重叠并确保全面覆盖。
- **并发执行** -- 四位专家同时处理查询，与顺序执行相比显著减少总延迟。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. AI 客服提案的详细查询被发送。
3. `ParallelAgent` 将查询并发分发给四位专家。
4. 每位专家生成其领域专业分析：
   - **技术专家**：评估技术栈可行性、架构和资源需求。
   - **商业专家**：评估市场机会、投资回报率和上市策略。
   - **风险专家**：识别并评定技术、市场、运营和合规风险。
   - **法律专家**：分析数据合规、AI 治理和知识产权保护。
5. 四份分析汇总为一个综合响应，显示在 Web UI 中。
6. 总响应时间约为最慢专家的耗时（而非所有专家耗时之和）。
