# Reflexion 智能体示例

**源文件:** `examples/flows/reflexion_agent_demo.py`

## 概述

本示例展示了 OxyGent 中的 **Reflexion**（反思）流程模式。在该模式下，智能体通过自我评估迭代优化其回答。示例注册了两个反思工作流 -- 通用反思循环和数学专用反思循环 -- 以及一个根据问题类型进行路由的主控智能体。两种工作流遵循相同的迭代模式：生成回答、评估质量、持续优化直到满意或达到最大轮次。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- 已安装 OxyGent 包（`pip install -r requirements.txt`）

## 运行方式

```bash
python -m examples.flows.reflexion_agent_demo
```

示例会启动 Web 服务（默认 `127.0.0.1:8080`），初始查询为"Calculate the area of a circle with radius 5."（计算半径为 5 的圆的面积）。

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
```

设置所有智能体默认使用的 LLM 模型名称。实际的 LLM 在 `oxy_space` 列表中配置为 `HttpLLM`，采用低温度（0.01）以获得确定性输出，并发信号量为 4。

### 组件（`oxy_space`）

| 组件 | 类型 | 角色 |
|---|---|---|
| `default_llm` | `HttpLLM` | 所有智能体共享的语言模型 |
| `worker_agent` | `ReActAgent` | 为通用问题生成初始回答 |
| `reflexion_agent` | `ChatAgent` | 评估回答质量并提供改进建议 |
| `math_expert_agent` | `ChatAgent` | 提供详细步骤的数学解题 |
| `math_checker_agent` | `ChatAgent` | 验证数学解答的正确性 |
| `general_reflexion` | `Reflexion` | 内置 Reflexion 流程，使用 `worker_agent` 和 `reflexion_agent` |
| `math_reflexion` | `MathReflexion` | 内置 MathReflexion 流程，用于数学专用验证 |
| `master_agent` | `ReActAgent` | 将问题路由到 `general_reflexion` 或 `math_reflexion` |

`general_reflexion` 节点标记为 `is_master=True`，表示它是用户查询的默认入口。它引用 `worker_agent` 作为答案生成器，`reflexion_agent` 作为评估器，最多进行 3 轮反思。

### 工作流函数

代码中定义了两个异步工作流函数，作为手动实现反思模式的参考：

1. **`reflexion_workflow`** -- 通用反思循环：
   - 调用 `worker_agent` 生成初始回答。
   - 将回答和原始问题发送给 `reflexion_agent` 进行评估。
   - 解析评估结果中的"Satisfactory"（满意）/"Unsatisfactory"（不满意）。
   - 如果不满意，提取改进建议并附加到查询中进入下一轮。
   - 最多重复 `max_iterations`（3）次。

2. **`math_reflexion_workflow`** -- 数学专用反思循环：
   - 调用 `math_expert_agent` 求解问题。
   - 将解答发送给 `math_checker_agent` 根据正确性标准（计算步骤、完整性、清晰度）进行验证。
   - 解析结果中的"Pass"（通过）/"Fail"（不通过）。
   - 如果不通过，提取修正建议并重复。

注意：在生产环境中，内置的 `Reflexion` 和 `MathReflexion` 流程类会自动处理此循环。手动函数展示了底层逻辑。

### 入口

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="Calculate the area of a circle with radius 5.")
```

创建 `MAS` 实例，注册所有组件，并启动 Web 服务。`first_query` 在 Web 界面加载时自动发送。

## 核心概念

- **Reflexion 模式**：一种迭代自我改进循环，智能体生成回答后由评审者评估，反馈被纳入后续尝试。这模拟了人类修改草稿的过程。
- **Reflexion vs. MathReflexion**：`Reflexion` 是通用的；`MathReflexion` 使用领域特定的验证标准（计算正确性、步骤完整性）。
- **`is_master=True`**：将组件标记为 MAS 中用户查询的入口。
- **`max_reflexion_rounds`**：控制评估-改进迭代的最大轮次。
- **`oxy_request.call()`**：一个 Oxy 组件通过名称调用另一个组件的机制，传递参数并接收 `OxyResponse`。

## 预期行为

1. Web 界面打开并发送数学查询。
2. `master_agent` 将问题路由到合适的反思工作流。
3. 工作者/专家智能体生成初始回答（例如面积 = pi * 25 = 78.54）。
4. 评估者/检查者智能体审查回答的质量/正确性。
5. 如果回答通过评估，立即返回；否则循环继续并纳入反馈。
6. 最终答案显示在 Web 界面中，标注经过了多少轮反思。
