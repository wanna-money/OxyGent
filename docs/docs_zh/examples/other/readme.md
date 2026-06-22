# 其他示例

展示 OxyGent 在标准智能体和工具模式之外的其他功能的杂项示例。

---

## 示例

### 流程图图像生成示例

**文件:** `examples/other/create_flow_image_demo.py`

本示例使用 OxyGent 构建了一个交互式 Mermaid 流程图生成与查看应用。它搭建了一个包含两个专业子智能体的多智能体系统：`image_gen_agent` 配备 `flow_image_gen_tools`，用于根据文本描述生成 Mermaid 流程图并渲染为 HTML；`open_chart_agent` 配备 `open_chart_tools`，用于在浏览器中打开已有的流程图 HTML 文件。主控 `ReActAgent` 使用详细的中文提示词进行意图识别，判断是生成新流程图、打开已有流程图，还是提供编辑指导。该示例还创建了一个自定义 FastAPI 应用，包含 CORS 中间件、流程图 API 路由和静态文件服务，OxyGent Web 服务运行在 8081 端口。默认任务生成一个涵盖需求分析、设计、编码、测试和部署阶段的软件开发流程图。

**核心组件:**
- `HttpLLM` -- 通过 OpenAI 兼容的环境变量配置的 LLM 后端
- `FunctionHub`（"flow_image_gen_tools"）-- 用于生成交互式 HTML 格式 Mermaid 流程图的工具
- `FunctionHub`（"open_chart_tools"）-- 用于在浏览器中打开已有流程图 HTML 文件的工具
- `ReActAgent`（"image_gen_agent"）-- 专门负责流程图生成的子智能体
- `ReActAgent`（"open_chart_agent"）-- 专门负责打开和展示流程图的子智能体
- `ReActAgent`（"master_agent"）-- 具备意图识别能力的编排器，路由与流程图相关的任务
- `FastAPI` -- 自定义 Web 应用，包含 CORS、API 路由和静态文件服务
- `MAS` -- 在自定义端口启动 Web 服务的运行时容器

**[详细文档 →](./create_flow_image_demo.md)**
