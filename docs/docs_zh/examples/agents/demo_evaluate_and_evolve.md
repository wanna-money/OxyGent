# SFT 数据评估与进化（批处理）

**源文件:** `examples/agents/demo_evaluate_and_evolve.py`

## 概述

本示例展示了如何使用 OxyGent 进行批量数据处理 -- 具体来说，是审核监督微调（SFT）训练数据的质量。一个带有详细评估提示词的 `ChatAgent` 审核从 Elasticsearch 中检索的 LLM 节点数据，判断每个样本是否符合高质量 SFT 正样本标准，审核结果被解析后用于过滤和导出干净的 JSONL 训练数据集。这种模式非常适合数据质量管线、自动内容审核以及任何批量 AI 评估任务。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- `requirements.txt` 中列出的 Python 依赖包
- 包含已有 LLM 节点数据的 Elasticsearch 实例（由之前的 OxyGent 运行填充），或带有存储数据的本地 ES 回退方案

## 运行方式

```bash
python -m examples.agents.demo_evaluate_and_evolve
```

## 代码详解

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name` 来自环境变量；`semaphore=4`（最大并发请求数 4）；`is_save_data=False` |
| `sft_agent` | `ChatAgent` | `prompt=sft_prompt`（详细的 SFT 审核指令）；`llm_model="default_llm"`；`is_save_data=False` |

两个组件都设置了 `is_save_data=False`，避免将审核过程本身存回数据库，保持数据管线的清洁。

### SFT 评估提示词

`sft_prompt` 指示代理充当严格的 SFT 数据审核员。对于包含 `node_id`、`input`（消息数组）和 `output`（候选回复）的每个样本，它评估四个标准：

1. **遵循系统指令/工具调用规则** -- 输出必须符合系统指定的任何约束。
2. **满足用户需求且事实正确** -- 逻辑合理、准确、格式规范。
3. **无违规/低质量内容** -- 无隐私泄露、攻击性语言或无意义填充。
4. **语言清晰流畅** -- 表达流畅且清晰。

输出必须是单个 JSON 对象：
```json
{
  "node_id": "...",
  "keep": true | false,
  "reason": "<20字以内>"
}
```

### 辅助函数

#### `get_llm_node_data(mas)`

异步函数，从 Elasticsearch 查询最近 32 条 LLM 节点记录：

1. 在 `{mas.name}_node` 索引中搜索 `node_type == "llm"` 的文档。
2. 按 `create_time` 降序排列，限制 32 条结果。
3. 对每条记录，提取 `node_id`、`input`（从 JSON 解析）和 `output`。
4. 返回两个列表：`app_node_data`（格式化的审核项）和 `datas`（用于最终数据集的原始消息数组）。

#### `parse_results(to_jsonl_path, datas, results)`

同步函数，处理代理的审核结果：

1. 对每个结果，从 markdown 代码块（```json ... ```）中提取 JSON。
2. 如果 `keep` 为 `true`，将对应的原始消息数据添加到数据集。
3. 打印过滤和保留样本的摘要。
4. 将保留的样本写入指定的 JSONL 文件。

### 入口函数

```python
async def main():
    to_jsonl_path = "./sft_dataset.jsonl"
    async with MAS(oxy_space=oxy_space) as mas:
        app_node_data, datas = await get_llm_node_data(mas)
        results = await mas.start_batch_processing(app_node_data)
        parse_results(to_jsonl_path, datas, results)
```

这里使用 `mas.start_batch_processing()` 而非 `start_web_service()` 或 `start_cli_mode()`。批处理将所有项目并发发送（受 LLM 的 `semaphore=4` 限制）并收集所有结果。

## 核心概念

- **批处理** -- `mas.start_batch_processing(items)` 通过主代理并发处理输入列表，返回结果列表。不涉及 Web UI 或 CLI 交互。
- **`is_save_data=False`** -- 防止审核代理自身的交互存储到数据库，避免污染训练数据管线。
- **`semaphore=4`** -- 限制 LLM 最多 4 个并发 API 调用，防止批处理期间触发速率限制。
- **数据管线模式** -- 从 ES 检索数据、用 LLM 代理评估、解析结果、导出过滤后的数据。这是一个完整的自动化数据质量管线。
- **SFT 数据质量** -- 提示词编码了一套全面的评分标准，用于评估 LLM 输出是否适合监督微调。

## 预期行为

1. 脚本连接到 Elasticsearch，检索最多 32 条最近的 LLM 节点记录。
2. 每条记录被发送给 `sft_agent` 进行质量评估（最多 4 条并行处理）。
3. 代理根据四个标准审核每个样本，输出 JSON 格式的判定结果。
4. 解析结果：标记为 `"keep": true` 的样本被保留。
5. 打印摘要："Filter out X samples and keep Y samples."
6. 保留的样本写入 `./sft_dataset.jsonl`。
7. 处理完成后脚本退出（不启动 Web 服务器）。
