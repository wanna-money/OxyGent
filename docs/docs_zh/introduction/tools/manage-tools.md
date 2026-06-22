# 如何管理智能体使用工具的行为？

在 OxyGent 中，智能体通过 `tools` 参数指定它可以使用的工具。工具通过名称引用——`tools=["time_tools"]` 表示该智能体可以使用 `oxy_space` 中名为 `time_tools` 的工具组件。

## 基本工具分配

```python
oxy.ReActAgent(
    name="time_agent",
    desc="一个可以查询时间的智能体",
    tools=["time_tools"],           # 允许使用 time_tools
    except_tools=["dangerous_tool"], # 禁止使用 dangerous_tool
    llm_model="default_llm",
)
```

> 工具名称对应 `oxy_space` 列表中某个工具组件的 `name` 属性。运行时，MAS 会自动查找并关联。

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `tools` | `list[str]` | `[]` | 允许使用的工具名称列表 |
| `except_tools` | `list[str]` | `[]` | 禁止使用的工具名称列表 |
| `sub_agents` | `list[str]` | `[]` | 子智能体名称列表（可被当作工具调用） |
| `is_sourcing_tools` | `bool` | `False` | 是否启用语义检索工具（需配置向量数据库） |
| `top_k_tools` | `int` | `10` | 语义检索返回的工具数量 |
| `is_retain_subagent_in_toolset` | `bool` | `False` | 是否将子智能体也放入工具列表中 |
| `is_retrieve_even_if_tools_scarce` | `bool` | `True` | 工具数量少时是否仍执行检索 |

## 工具解析流程

当智能体运行时，OxyGent 按以下逻辑确定可用工具：

1. 从 `tools` 列表中，按名称在 `oxy_space` 中查找对应的工具组件
2. 从 `sub_agents` 列表中查找子智能体（子智能体也可被当作工具调用）
3. 如果设置了 `except_tools`，从可用工具中移除对应的工具
4. 如果 `is_sourcing_tools=True`，使用向量数据库对工具进行语义检索，返回 `top_k_tools` 个最相关的工具

## 完整示例

```python
import asyncio, os
from oxygent import MAS, oxy, preset_tools

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    preset_tools.time_tools,
    preset_tools.math_tools,
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        tools=["time_tools", "math_tools"],
        llm_model="default_llm",
    ),
]

async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="现在几点了？")

if __name__ == "__main__":
    asyncio.run(main())
```

[上一章：使用MCP自定义工具](./custom-mcp-tools.md)
[下一章：设置OxyGent Config](../getting-started/config.md)
[回到首页](../readme.md)

---

## 相关示例

- [FunctionHub工具注册示例](../../examples/tools/demo_functionhub.md) — 演示工具的注册与管理
- [ReAct智能体示例](../../examples/agents/demo_react_agent.md) — 演示智能体如何自动调用工具
