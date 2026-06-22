# Top-K 工具向量检索

**源文件:** `examples/advanced/demo_top_k_tools.py`

## 概述

本示例演示了 `top_k_tools` 功能,该功能利用向量相似度搜索为每次查询筛选出最相关的工具,再发送给 LLM。当 Agent 注册了大量工具时,此功能通过每轮仅呈现最相关的前 N 个工具来减少提示词长度并提高工具选择准确性。

## 前置条件

- 环境变量: `DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Vearch 向量数据库实例(在 `config.json` 的 `test` 环境中配置)
- Embedding 模型(在 `config.json` 中配置,用于向量相似度计算)
- Node.js 运行时(用于 `npx` 运行 MCP 文件系统服务器,以及 `uvx` 运行时间服务器)

## 运行方式

```bash
python -m examples.advanced.demo_top_k_tools
```

## 代码详解

### 配置

```python
Config.load_from_json("./config.json", env="test")
```

从 `config.json` 加载配置,使用 `test` 环境覆盖层。该环境必须定义 Vearch 向量数据库设置(如 `vearch.router_url`、`vearch.db_name`)以及向量相似度搜索所需的 embedding 模型配置。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | `api_key`、`base_url`、`model_name`(来自环境变量);`llm_params={"temperature": 0.1}` |
| `time_tools` | `StdioMCPClient` | `command="uvx"`、`args=["mcp-server-time", "--local-timezone=Asia/Shanghai"]` |
| `file_tools` | `StdioMCPClient` | `command="npx"`、`args=["-y", "@modelcontextprotocol/server-filesystem", "./local_file"]` |
| `master_agent` | `ReActAgent` | `llm_model="default_llm"`、`tools=["time_tools", "file_tools"]`、`top_k_tools=3` |

`master_agent` 同时注册了 `time_tools` 和 `file_tools`,这些工具集可能包含许多独立的工具函数。设置 `top_k_tools=3` 后,每次查询仅将与当前问题向量相似度最高的 3 个工具包含在 LLM 提示词中。

### 入口函数

`main()` 创建 `MAS` 上下文并以 `first_query="What time is it now?"` 启动 Web 服务。对于该查询,向量相似度搜索应将时间相关的工具排在文件相关工具之前。

## 核心概念

- **top_k_tools** -- Agent 上的整数参数,限制每次查询呈现给 LLM 的工具数量。工具按查询与各工具描述之间的向量相似度进行排序。
- **Vearch** -- 框架用于工具检索的向量数据库。工具描述被嵌入为向量并存储在 Vearch 中,实现高效的相似度搜索。
- **Config.load_from_json()** -- 从 JSON 文件加载配置,支持环境分层。`env` 参数选择在 `default` 设置之上应用哪个环境覆盖层。
- **动态工具选择** -- 不再将所有工具呈现给 LLM(这可能溢出上下文窗口并降低选择准确性),而是根据每次查询动态选择最相关的工具子集。

## 预期行为

1. Web 服务在 `127.0.0.1:8080` 启动。
2. 当用户询问 "What time is it now?" 时,框架计算查询与所有可用工具描述之间的向量相似度。
3. 选择相似度最高的前 3 个工具,包含在 LLM 提示词中。
4. LLM 从缩小后的工具集中选择合适的时间工具,返回当前时间。
