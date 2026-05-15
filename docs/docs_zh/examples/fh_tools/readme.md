# FunctionHub 工具示例

演示如何在 OxyGent 智能体中使用基于 `FunctionHub` 的自定义 Python 工具。

---

## 示例

### 最短路径示例

**文件:** `examples/fh_tools/shortest_path/shortest_path_demo.py`

本示例演示了如何使用 `FunctionHub` 结合 Google OR-Tools 求解城市之间的最短路径问题。FunctionHub（从 `function_hubs/shortest_path.py` 导入）提供两个工具：`info_update` 使用 pandas 从 Excel 文件中读取城市和距离数据到内存中，`shortest_path` 使用 OR-Tools 的 `min_cost_flow` 求解器计算两个城市之间的最短路径，然后通过 matplotlib 和 networkx 进行可视化，并将结果图保存为 PNG 图片。多智能体系统包含一个用于计算路径的 `shortest_path_agent`、一个用于读取文件信息的 `excel_agent`，以及一个协调两者的主控 `ReActAgent`。该示例启动 Web 服务，用户可以上传包含城市和距离数据的 Excel 文件，并查询最短路径。

**核心组件:**
- `HttpLLM` -- 通过环境变量配置的 LLM 后端
- `FunctionHub`（"shortest_path_tools"）-- 自定义 Python 工具，用于 Excel 数据导入和基于 OR-Tools 的最短路径计算
- `ReActAgent`（"shortest_path_agent"）-- 用于计算城市间最短路径的智能体
- `ReActAgent`（"excel_agent"）-- 用于读取 Excel 文件信息的智能体
- `ReActAgent`（"master_agent"）-- 协调 Excel 和最短路径智能体的编排器
- `MAS` -- 启动 Web 服务的运行时容器

**[详细文档 →](./shortest_path/shortest_path_demo.md)**
