# 基于 Mermaid 的流程图生成代理

**源文件:** `examples/other/create_flow_image_demo.py`

## 概述

本示例构建了一个交互式流程图助手，能够生成基于 Mermaid 的流程图并在浏览器中显示。它使用主 `ReActAgent` 协调两个子代理：一个用于从文本描述生成流程图 HTML 文件，另一个用于打开已有的流程图文件。应用还搭建了一个自定义 FastAPI 服务器，提供静态文件服务和专用的流程图操作 API 路由。

<img src="https://storage.jd.com/opponent/AI/5.png" width="80%"/>
<img src="https://storage.jd.com/opponent/AI/6.png" width="80%"/>

## 前置条件

- 环境变量：`OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL_NAME`（注意：本示例使用 OpenAI 风格的变量名，而非默认的 `DEFAULT_LLM_*` 名称）
- `requirements.txt` 中列出的 Python 依赖包
- `function_hubs.chart` 模块（提供 `flow_image_gen_tools`、`open_chart_tools`、`create_static_files` 和 `flowchart_api`）
- Web 浏览器，用于查看生成的流程图

## 运行方式

```bash
cd examples/other
python create_flow_image_demo.py
```

或从项目根目录运行：

```bash
PYTHONPATH=. python examples/other/create_flow_image_demo.py
```

注意：脚本手动将项目根目录添加到 `sys.path` 并通过 `python-dotenv` 加载 `.env`，因此可以直接从其所在目录运行。

## 代码详解

### 配置

```python
Config.set_agent_llm_model("default_llm")
```

设置全局默认 LLM 模型。脚本还可选择通过 `Config.set_server_auto_open_webpage(False)` 禁用自动打开浏览器（默认被注释掉）。

### 主代理提示词

`MASTER_AGENT_PROMPT` 是一个详细的中文系统提示词，指导主代理：

1. **分析用户意图** -- 识别用户是要生成、打开还是编辑流程图。
2. **路由到正确的代理/工具** -- 基于关键词匹配：
   - 生成类关键词（生成、创建、画、设计）路由到 `image_gen_agent`。
   - 打开/查看类关键词路由到 `open_chart_agent`。
   - 编辑/导出类问题直接提供使用指导。
3. **从用户输入中提取参数**（如流程图描述、文件路径）。
4. **使用预定义响应模板提供反馈**。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | 来自环境变量的 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL_NAME` |
| `flow_image_gen_tools` | FunctionHub | 从 `function_hubs.chart.flow_image_gen_tools` 导入；生成 Mermaid 流程图 |
| `open_chart_tools` | FunctionHub | 从 `function_hubs.chart.open_chart_tools` 导入；在浏览器中打开 HTML 文件 |
| `image_gen_agent` | `ReActAgent` | `tools=["flow_image_gen_tools"]`，描述：流程图生成代理 |
| `open_chart_agent` | `ReActAgent` | `tools=["open_chart_tools"]`，描述：在浏览器中打开流程图 |
| `master_agent` | `ReActAgent` | `is_master=True`，`sub_agents=["image_gen_agent", "open_chart_agent"]`，`prompt_template=MASTER_AGENT_PROMPT`，同时拥有两个工具集的直接访问权限 |

### FastAPI 应用配置

脚本在 OxyGent MAS 之外创建了自定义 FastAPI 应用：

1. **CORS 中间件** -- 允许所有来源，方便开发调试。
2. **流程图 API 路由** -- 从 `function_hubs.chart.flowchart_api` 挂载到 `/api` 路径。
3. **根路径重定向** -- `GET /` 重定向到 `/static/index.html`。
4. **静态文件服务** -- Web UI 从 `function_hubs/chart/web/` 目录提供服务，挂载到 `/static` 路径。

### 入口函数

```python
async def main():
    os.makedirs("../../function_hubs/chart/web", exist_ok=True)
    os.makedirs("../../function_hubs/chart/web/css", exist_ok=True)
    os.makedirs("../../function_hubs/chart/web/js", exist_ok=True)
    create_static_files("../../function_hubs/chart")
    app.mount("/static", StaticFiles(directory="../../function_hubs/chart/web"), name="web")

    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="请生成一个软件开发流程图，包括需求分析、设计、编码、测试和部署阶段",
            port=8081,
        )
```

1. 如果 Web 目录结构不存在则创建。
2. 生成 Mermaid 编辑器 UI 的静态文件（HTML、CSS、JS）。
3. 在 FastAPI 应用上挂载静态文件。
4. 在端口 **8081**（非默认的 8080）上启动 MAS Web 服务，并发送一个初始流程图生成请求。

## 使用方法

1. **默认查询**：程序启动后会自动执行初始流程图生成请求（软件开发流程图）。
2. **自定义查询**：在 Web 界面输入框中输入流程图描述，例如："生成一个项目管理流程图"、"创建一个用户注册流程图"、"画一个订单处理的流程图"。
3. **查看结果**：流程图会自动在浏览器中打开，HTML 文件保存在项目目录中。
4. **编辑和预览**：在流程图页面中可直接编辑 Mermaid 代码，点击"更新预览"按钮实时查看修改效果，支持多种预设模板选择。
5. **导出图表**：点击"导出 SVG"或"导出 PNG"按钮将流程图导出为对应格式。

## 核心概念

- **Mermaid.js** -- 一个基于 JavaScript 的图表库，从文本定义渲染图表。生成的流程图是嵌入 HTML 文件中的 Mermaid 语法。
- **`prompt_template`** -- 完整的系统提示词模板，完全替换默认代理提示词（与追加到默认提示词的 `additional_prompt` 不同）。
- **主代理直接工具访问** -- 主代理在拥有子代理的同时还设置了 `tools=["flow_image_gen_tools", "open_chart_tools"]`，允许它直接调用工具而无需委派给子代理。
- **自定义 FastAPI 集成** -- 本示例展示了如何使用自定义 API 路由和静态文件服务扩展 OxyGent Web 服务，在不同端口上与 MAS 服务一起运行。
- **静态文件生成** -- `create_static_files()` 在启动时以编程方式生成 Web 编辑器 UI 文件（HTML/CSS/JS）。

## 预期行为

1. Web 服务在 `http://127.0.0.1:8081` 启动。
2. 静态 Mermaid 编辑器 UI 可通过 `http://127.0.0.1:8081/static/index.html` 访问。
3. 首个查询要求代理生成一个软件开发流程图。
4. 主代理将请求路由到 `image_gen_agent`，后者调用 `generate_flow_chart` 生成 Mermaid 流程图 HTML 文件。
5. 生成的流程图自动在浏览器中打开，显示需求分析、设计、编码、测试和部署等阶段。
6. 用户可以继续交互 -- 要求生成新的流程图、打开已有的流程图，或获取编辑/导出的操作指导。

## 故障排除

1. **API 连接失败**：检查 `.env` 文件中的 API 配置，验证网络连接和 API 服务状态。系统会自动降级到示例流程图。
2. **端口占用**：默认端口 8081 被占用时，修改 `port` 参数；或使用 `pkill -f create_flow_image_demo.py` 清理进程。
3. **文件路径问题**：确保有足够的文件系统权限，检查输出目录是否存在。
4. **静态文件缺失**：系统会自动创建必要的静态文件，如有问题请检查 `create_static_files` 函数执行是否正常。

启用调试模式获取详细日志：

```bash
export LOG_LEVEL=DEBUG
python examples/other/create_flow_image_demo.py
```
