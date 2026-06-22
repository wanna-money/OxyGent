<!-- Copyright 2022 JD Co.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this project except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. -->

[English](./README.md) | [中文](./README_zh.md)


<p align="center">
  <a href="https://github.com/jd-opensource/OxyGent/pulls">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome">
  </a>
  <a href="https://github.com/jd-opensource/OxyGent/blob/v4/LICENSE">
    <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="license"/>
  </a>
  <a href="https://pypi.org/project/oxygent/">
    <img src="https://img.shields.io/pypi/v/oxygent.svg?logo=pypi&logoColor=white" alt="pip"/>
  </a>
  <a href="https://arxiv.org/abs/2604.25602">
    <img src="https://img.shields.io/badge/Paper-ACL%202026-orange" alt="paper"/>
  </a>

<html>
    <h2 align="center">
      <img src="https://storage.jd.com/ai-gateway-routing/prod_data/oxygent_github_images/banner.jpg" width="1256"/>
    </h2>
    <h3 align="center">
      适用于生产环境的多智能体协作框架
    </h3>
    <h3 align="center">
      访问官方网站:
      <a href="http://oxygent.jd.com">OxyGent</a>
      ｜开源仓库:
      <a href="https://github.com/jd-opensource/OxyGent">Python</a>
      or
      <a href="https://github.com/jd-opensource/JDOxyGent4J">Java</a>
    </h3>
</html>

## 1. 简介
OxyGent 是一个开源框架，将工具、模型、智能体统一为可插拔的原子算子——Oxy。专为开发者设计，OxyGent 让你像搭乐高一样构建灵活的多智能体系统，极致可扩展，每一步决策全链路可追溯。从构建、推理到持续进化，OxyGent 打造了一个闭环智能体流水线——无缝集成 Oxy，弹性扩展，协同创新，驱动 AI 生态无限可能。

## 2. 核心特性
🏎️ **高效开发**
- OxyGent 是模块化多智能体框架，极致高效构建、部署、进化 AI 团队。标准化 Oxy 组件像乐高一样拼装，支持热插拔与跨场景复用：纯净 Python 接口，无需繁杂配置。

🤝 **智能协作**
- 动态规划范式，智能体可智能分解任务、协商解法、实时适应变化。区别于刚性流程，OxyGent 智能体自然应对突发挑战，每一步决策全链路可审计。

🕸️ **弹性架构**
- 底层弹性架构支持任意智能体拓扑：从简单 ReAct 到复杂混合规划。自动依赖映射与可视化调试，轻松优化分布式系统性能。

🔁 **持续进化**
- 每一次交互都是学习机会：内置评估引擎自动生成训练数据。智能体通过知识反馈持续自我进化，且全过程透明可追溯。

📈 **无限扩展**
- 按 Metcalfe 定律线性扩容：分布式调度器让协作智能指数级增长。系统轻松应对全域优化与实时决策，任意规模无压力。

OxyGent最新版本 (July 15, 2025) 在[GAIA](https://huggingface.co/spaces/gaia-benchmark/leaderboard)榜单中分数为59.14，目前开源框架第一OWL为60.8分。

![](https://storage.jd.com/ai-gateway-routing/prod_data/oxygent_github_images/points.png)

## 3. 框架核心类
![](docs/images/structure.png)

## 4. 框架亮点
- 对**开发者**：专注业务逻辑，无需重复造轮子
- 对**企业**：一套框架打通所有智能体，告别信息孤岛，降低沟通成本。
- 对**用户**：畅享智能体生态的无缝协作体验。

## 5. 快速开始
### 步骤1：创建运行环境
- 方式一：conda
   ```bash
   conda create -n oxy_env python==3.10
   conda activate oxy_env
   ```
- 方式二：uv
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv python install 3.10 
   uv venv .venv --python 3.10
   source .venv/bin/activate
   ```
### 步骤2：安装依赖
- 方式一：conda
   ```bash
   pip install oxygent
   ```
- 方式二：uv
   ```bash
   uv pip install oxygent
   ```
- 方式三：开发环境
   ```bash
   git clone https://github.com/jd-opensource/OxyGent.git
   cd OxyGent
   pip install -r requirements.txt # or in uv
   brew install coreutils # maybe essential
   ```

### 步骤3：Node.js环境（如果使用MCP）
- 下载安装 **[Node.js](https://nodejs.org)**

### 步骤4：创建示例
- demo.py
   ```python
   import os
   from oxygent import MAS, Config, oxy, preset_tools

   Config.set_agent_llm_model("default_llm")

   oxy_space = [
      oxy.HttpLLM(
         name="default_llm",
         api_key=os.getenv("DEFAULT_LLM_API_KEY"),
         base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
         model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
      ),
      preset_tools.time_tools,
      oxy.ReActAgent(
         name="time_agent",
         desc="A tool that can query the time",
         tools=["time_tools"],
      ),
      preset_tools.file_tools,
      oxy.ReActAgent(
         name="file_agent",
         desc="A tool that can operate the file system",
         tools=["file_tools"],
      ),
      preset_tools.math_tools,
      oxy.ReActAgent(
         name="math_agent",
         desc="A tool that can perform mathematical calculations.",
         tools=["math_tools"],
      ),
      oxy.ReActAgent(
         is_master=True,
         name="master_agent",
         sub_agents=["time_agent", "file_agent", "math_agent"],
      ),
   ]

   async def main():
      async with MAS(oxy_space=oxy_space) as mas:
         await mas.start_web_service(
            first_query="What time is it now? Please save it into time.txt."
         )

   if __name__ == "__main__":
      import asyncio
      asyncio.run(main())
   ```

### 步骤5：设置环境变量
- 方式一：在终端声明
   ```bash
   export DEFAULT_LLM_API_KEY="your_api_key"
   export DEFAULT_LLM_BASE_URL="your_base_url"
   export DEFAULT_LLM_MODEL_NAME="your_model_name"  
   ```
- 方式二：创建 .env 文件
   ```bash
   DEFAULT_LLM_API_KEY="your_api_key"
   DEFAULT_LLM_BASE_URL="your_base_url"
   DEFAULT_LLM_MODEL_NAME="your_model_name"
   ```

### 步骤6：运行
- 启动多智能体系统
   ```bash
   python demo.py
   ```
### 步骤7：查看可视化结果
- ![](https://storage.jd.com/ai-gateway-routing/prod_data/oxygent_github_images/vision.png)



## 6. 成为贡献者
您可以通过以下方法为 OxyGent 作出贡献:

1. 在Issue中报告问题
2. 提供改进建议
3. 补充文档
    - Fork仓库
    - 修改文档
    - 提出pull request
4. 修改代码
    - Fork仓库
    - 创建新分支
    - 加入您的修改
    - 提出pull request

感谢您的贡献！ 🎉🎉🎉
如果您在开发中遇到问题，请参阅 [OxyGent中文指南](./docs/docs_zh/readme.md) 或者 [OxyGent 文档](http://oxygent.jd.com/docs/)

## 7. 社区支持
如果你在OxyGent的开发或使用过程中遇到任何问题，欢迎在项目的Issue区域提交可复现的步骤或日志片段。
如果您有企业内部Slack，请直接联系OxyGent Core团队。

欢迎沟通和联系我们:

<div align="center">
  <img src="https://pfst.cf2.poecdn.net/base/image/b1e96084336a823af7835f4fe418ff49da6379570f0c32898de1ffe50304d564?w=1760&h=2085&pmaid=425510216" alt="contact" width="50%" height="50%">
</div>

## 8. 致谢
感谢以下为OxyGent作出贡献的[开发者](https://github.com/jd-opensource/OxyGent/graphs/contributors)
<a href="https://github.com/jd-opensource/OxyGent/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=jd-opensource/OxyGent" />
</a>

## 常见问题 (FAQ)

### 基础问题

**OxyGent 是什么？**
OxyGent 是一个开源框架，将工具、模型和智能体统一为模块化的 Oxy 组件。它为开发者提供透明的端到端流水线，用于构建、运行和持续进化多智能体系统。

**OxyGent 与其他多智能体框架有什么不同？**
OxyGent 使用独特的 "Oxy" 抽象来标准化智能体组件，支持热插拔和跨场景复用。与刚性的工作流系统不同，OxyGent 支持动态规划范式，智能体可以智能分解任务并实时适应变化。

**什么是 Oxy 抽象？**
Oxy 是一种标准化的组件模型，可以像乐高积木一样拼装。每个 Oxy 封装了特定的能力（工具、模型或智能体），通过简洁的 Python 接口，实现 AI 团队的快速组装和持续进化。

### 安装与配置

**系统要求是什么？**
- Python 3.10+
- pip 包管理器
- LLM 供应商的 API Key（OpenAI、Anthropic 等）

**如何安装 OxyGent？**
```bash
pip install oxygent
```

**OxyGent 支持本地模型吗？**
支持！OxyGent 兼容任何提供兼容 API 的 LLM 供应商。通过环境变量（`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`）配置本地模型即可。

### 智能体开发

**如何创建自定义 Oxy？**
创建一个继承 Oxy 基类的新类，并实现所需的方法。详见[文档](http://oxygent.jd.com/docs/)。

**OxyGent 支持哪些规划范式？**
OxyGent 支持多种规划范式：
- **ReAct**：推理 + 行动模式，适用于简单任务
- **动态规划**：智能体智能分解任务并协商解决方案
- **混合规划**：组合多种范式以应对复杂场景

**OxyGent 如何处理智能体协作？**
OxyGent 的弹性架构支持任意智能体拓扑。智能体通过标准化接口通信，配合自动依赖映射和可视化调试工具进行优化。

### 部署

**如何部署 OxyGent 应用？**
OxyGent 应用可以作为标准 Python 应用部署：
- **本地开发**：运行 `python demo.py` 进行本地测试
- **生产环境**：使用分布式调度器实现多节点扩展
- **Docker**：将 OxyGent 应用容器化以实现一致的部署

**OxyGent 适合企业使用吗？**
适合！OxyGent 专为企业场景设计，具备以下特性：
- 分布式调度实现水平扩展
- 每一步决策全链路可审计
- 内置评估引擎持续改进
- 支持全域优化和实时决策

### 常见问题排查

**常见问题：**
- **导入错误**：确保已安装 Python 3.10+ 且依赖是最新版本
- **API Key 错误**：检查 LLM 供应商的 API Key 是否正确配置
- **智能体通信异常**：确认所有 Oxy 组件已正确注册

**在哪里获取帮助？**
- [官方文档](http://oxygent.jd.com/docs/)
- [GitHub Issues](https://github.com/jd-opensource/OxyGent/issues)
- 企业内部 Slack（京东员工）

## 9. 许可证
[Apache License]( ./LICENSE.md)

#### OxyGent 由 Oxygen JD.com 提供 
#### 感谢您对OxyGent的关心与贡献!