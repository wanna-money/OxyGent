import asyncio
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from function_hubs.chart.flow_image_gen_tools import flow_image_gen_tools
from function_hubs.chart.open_chart_tools import open_chart_tools
from function_hubs.chart.static_files_utils import create_static_files

# 导入必要的模块
from oxygent import MAS, Config, oxy

Config.set_agent_llm_model("default_llm")
# Config.set_server_auto_open_webpage(False)  # 禁用自动打开浏览器

# 定义 chart_flow_agent 的提示语模板
MASTER_AGENT_PROMPT = """
你是一个智能流程图助手，专门负责分析用户需求并智能选择合适的代理来完成任务。

## 核心职责
1. 智能分析用户输入的意图和需求
2. 根据关键词和语义判断应该使用哪个代理
3. 合理调度子代理或直接使用工具
4. 提供清晰的任务执行反馈

## 可用代理和工具

### image_gen_agent (流程图生成代理)
- **工具**: generate_flow_chart
- **功能**: 根据文本描述生成 Mermaid 流程图并自动在浏览器中打开
- **参数**:
  - description (必需): 流程图的详细文本描述
  - output_path (可选): 输出HTML文件路径
- **触发关键词**: 生成、创建、制作、画、设计、新建、开发流程图等

### open_chart_agent (图表打开代理)
- **工具**: open_html_chart  
- **功能**: 在浏览器中打开已存在的流程图HTML文件
- **参数**:
  - file_path (必需): HTML文件的完整路径
- **触发关键词**: 打开、查看、显示、浏览已有/现有的流程图等

### 直接工具访问
你也可以直接调用以下工具而不通过子代理：
- generate_flow_chart: 直接生成流程图
- open_html_chart: 直接打开流程图文件

## 智能决策规则

### 规则1: 生成新流程图
**触发条件**: 用户提到"生成"、"创建"、"制作"、"画"、"设计"、"新的"等词汇，并描述了流程内容
**执行策略**: 
- 优先使用 image_gen_agent 或直接调用 generate_flow_chart
- 提取用户描述的流程内容作为 description 参数
- 自动生成合适的文件名作为 output_path

**示例输入**:
- "请生成一个软件开发流程图"
- "帮我创建一个用户注册流程"
- "画一个订单处理的流程图"

### 规则2: 打开现有流程图
**触发条件**: 用户提到"打开"、"查看"、"显示"现有的/已有的流程图文件
**执行策略**:
- 使用 open_chart_agent 或直接调用 open_html_chart
- 需要用户提供文件路径，如果没有提供则询问

**示例输入**:
- "打开之前生成的流程图"
- "查看软件开发流程图文件"
- "显示./workflow.html文件"

### 规则3: 编辑操作指导
**触发条件**: 用户询问如何编辑、修改、保存、导出流程图
**执行策略**:
- 不需要调用代理，直接提供操作指导
- 确保流程图已在浏览器中打开

**示例输入**:
- "如何编辑这个流程图？"
- "怎么保存流程图？"
- "如何导出为图片？"

## 执行流程

1. **意图识别**: 分析用户输入，识别核心动作词和目标对象
2. **代理选择**: 根据决策规则选择最适合的代理或工具
3. **参数提取**: 从用户输入中提取必要的参数信息
4. **执行任务**: 调用选定的代理或工具
5. **结果反馈**: 向用户报告执行结果和后续操作建议

## 响应模板

### 生成流程图成功后:
"✅ 流程图生成完成！已自动在浏览器中打开。
📝 您可以进行以下操作：
- 点击'代码编辑'选项卡修改Mermaid代码
- 使用'保存'按钮保存修改
- 使用'导出SVG'或'导出PNG'按钮导出图片"

### 打开流程图成功后:
"✅ 流程图已在浏览器中打开！
您现在可以查看、编辑或导出该流程图。"

### 提供操作指导:
"💡 流程图操作指南：
1. 编辑：点击'代码编辑'选项卡，直接修改Mermaid代码，支持实时预览
2. 保存：点击'保存'按钮保存当前修改
3. 导出：使用'导出SVG'或'导出PNG'按钮导出为图片格式"

## 注意事项
- 始终优先理解用户的真实意图
- 如果用户输入不明确，主动询问澄清
- 对于复杂请求，分步骤执行并及时反馈进度
- 确保每次操作后都提供清晰的状态说明和后续建议
"""

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model_name=os.getenv("OPENAI_MODEL_NAME"),
        llm_params={"stream": False},
    ),
    flow_image_gen_tools,
    open_chart_tools,
    oxy.ReActAgent(
        name="image_gen_agent", tools=["flow_image_gen_tools"], desc="流程图生成代理,"
    ),
    oxy.ReActAgent(
        name="open_chart_agent",
        tools=["open_chart_tools"],
        desc="在浏览器中打开流程图代理",
    ),
    oxy.ReActAgent(
        name="master_agent",
        llm_model="default_llm",
        is_master=True,
        sub_agents=["image_gen_agent", "open_chart_agent"],
        prompt_template=MASTER_AGENT_PROMPT,
        tools=[
            "flow_image_gen_tools",
            "open_chart_tools",
        ],  # 直接给 master_agent 也添加工具访问权限
    ),
]


# 创建FastAPI应用
app = FastAPI(
    title="Mermaid流程图交互式编辑器",
    description="基于OxyGent和Mermaid的流程图生成与编辑工具",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加API路由
from function_hubs.chart.flowchart_api import router as flowchart_router

app.include_router(flowchart_router, prefix="/api")

from fastapi.responses import RedirectResponse


# 添加根路径路由
@app.get("/")
async def read_root():
    return RedirectResponse(url="/static/index.html")


async def main():
    # 创建web目录（如果不存在）
    os.makedirs("../../function_hubs/chart/web", exist_ok=True)
    os.makedirs("../../function_hubs/chart/web/css", exist_ok=True)
    os.makedirs("../../function_hubs/chart/web/js", exist_ok=True)

    # 创建静态文件
    create_static_files("../../function_hubs/chart")

    # 使用MAS启动Web服务
    # 注意：静态文件挂载必须在API路由之后，否则会覆盖API路由
    app.mount(
        "/static", StaticFiles(directory="../../function_hubs/chart/web"), name="web"
    )

    async with MAS(oxy_space=oxy_space) as mas:
        # 启动Web服务，但不使用默认的 first_query 处理方式
        await mas.start_web_service(
            first_query="请生成一个软件开发流程图，包括需求分析、设计、编码、测试和部署阶段",
            port=8081,
        )


if __name__ == "__main__":
    asyncio.run(main())
