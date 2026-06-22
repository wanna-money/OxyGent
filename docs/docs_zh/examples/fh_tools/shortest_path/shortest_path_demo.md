# 基于 FunctionHub 工具的最短路径代理

**源文件:** `examples/fh_tools/shortest_path/shortest_path_demo.py`

## 概述

本示例展示了如何构建一个计算城市间最短路径的多代理系统。它使用基于 Google OR-Tools 的自定义 `FunctionHub` 工具进行图优化计算，并使用 matplotlib/networkx 进行可视化。主代理协调一个 Excel 读取代理和一个最短路径计算代理。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- 额外 Python 依赖包：
  - `ortools` -- Google OR-Tools，用于最小费用流/最短路径计算
  - `matplotlib` -- 用于路径可视化
  - `networkx` -- 用于图构建和绘制
  - `pandas` -- 用于读取 Excel 文件
  - `openpyxl` -- pandas 的 Excel 引擎（`.read_excel` 隐式依赖）

## 运行方式

```bash
python -m examples.fh_tools.shortest_path.shortest_path_demo
```

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
```

设置全局默认 LLM 模型。

### FunctionHub 工具 (`shortest_path_tools`)

工具定义位于 `function_hubs/shortest_path.py`，以 `shortest_path_tools` 导入。该 `FunctionHub` 提供两个工具：

#### `info_update(file_path, sheet_name=0)`

从 Excel 文件中读取城市和距离数据到模块级变量 `column_data` 字典中。Excel 文件应包含名为 `cities`、`start_cities`、`end_cities` 和 `distances` 的列。返回 `"File Read Success!"` 或 `"File is Empty"`。

#### `shortest_path(start_city, end_city)`

使用 OR-Tools 的 `SimpleMinCostFlow` 求解器计算两个城市间的最短路径：

1. 从加载的城市/距离数据构建有向图。
2. 为每条连接添加双向弧（因为道路是双向的）。
3. 在起点和终点设置供给/需求。
4. 求解最小费用流问题（对于单位容量等价于最短路径）。
5. 返回包含 `status`、`distance`、`solve_time`、`path` 和 `path_cities` 的结果字典。
6. 调用 `visualize_city_path()` 生成 PNG 图片（`city_shortest_path.png`），显示所有城市节点和连接，最短路径以红色高亮。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | 凭证来自环境变量 |
| `shortest_path_tools` | `FunctionHub` | 从 `function_hubs/shortest_path` 导入 |
| `shortest_path_agent` | `ReActAgent` | `tools=["shortest_path_tools"]`，`timeout=30`，`retries=3`，`delay=1`，`semaphore=2` |
| `excel_agent` | `ReActAgent` | `desc="...基于 Excel 文件路径读取文件信息"`，`tools=["shortest_path_tools"]` |
| `master_agent` | `ReActAgent` | `is_master=True`，`sub_agents=["excel_agent", "shortest_path_agent"]` |

### 代理架构

系统采用两步工作流：

1. **`excel_agent`** -- 使用 `info_update` 读取包含城市和距离信息的 Excel 文件。
2. **`shortest_path_agent`** -- 使用 `shortest_path` 计算两个指定城市间的最短路径。

**`master_agent`** 协调两者，首先委派 Excel 代理加载数据，然后委派最短路径代理进行计算。

### 入口函数

```python
await mas.start_web_service(first_query="")
```

以空初始查询启动 Web 服务，由用户交互式地提供 Excel 文件路径和查询。

## 核心概念

- **FunctionHub** -- 将 Python 函数封装为代理可调用工具的工具容器。通过 `@fh.tool()` 装饰器注册工具，附带描述字符串。
- **Google OR-Tools** -- 一个开源优化库。此处将最短路径问题建模为单位容量的最小费用流问题来求解。
- **代理工厂函数** -- `create_optimal_agent()` 展示了如何通过编程方式创建代理，精细控制 `timeout`、`retries`、`delay` 和 `semaphore` 等参数。
- **`semaphore`** -- 限制代理的并发执行数量为指定值（此处为 2），防止资源耗尽。
- **`retries` / `delay`** -- 执行失败时代理最多重试 3 次，每次间隔 1 秒。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8080` 启动。
2. 用户提供引用包含城市数据的 Excel 文件的查询（列名：`cities`、`start_cities`、`end_cities`、`distances`）。
3. 主代理委派 `excel_agent` 通过 `info_update` 读取 Excel 文件。
4. 主代理随后委派 `shortest_path_agent` 通过 `shortest_path` 计算两个城市间的最短路径。
5. 求解器返回最优路径、总距离和计算耗时。
6. 可视化结果保存为 `city_shortest_path.png`，显示所有城市节点、所有连接边，以及红色高亮的最短路径。
