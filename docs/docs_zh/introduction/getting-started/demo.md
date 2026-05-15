# 如何运行demo？

使用`python`直接运行我们的任意一个demo。

### 为什么下载后直接运行demo系统不启动？
---
OxyGent只是智能体系统框架，本身不提供LLM服务。因此您需要在`.env`中设置自己的LLM api。
```bash
   export DEFAULT_LLM_API_KEY="your_api_key"
   export DEFAULT_LLM_BASE_URL="your_base_url"  # if you want to use a custom base URL
   export DEFAULT_LLM_MODEL_NAME="your_model_name"  
```
```bash
   # create a .env file
   DEFAULT_LLM_API_KEY="your_api_key"
   DEFAULT_LLM_BASE_URL="your_base_url"
   DEFAULT_LLM_MODEL_NAME="your_model_name"
```

### 为什么我填好了环境变量，但是运行demo时报404？
---
首先，请您检查是否引入了不存在的环境变量。
如果不能解决问题，请查看[关于llm api](../agents/select-llm.md)。

### 如何获得帮助？
---
您可以通过以下方式获得帮助：

+ 在Github提交issue
+ 加入交流讨论群（参见readme）
+ 如果您有企业内部Slack，请直接联系OxyGent Core团队。

OxyGent未来将提供更完整的社区服务。

[上一章：安装OxyGent](./install.md)
[下一章：创建第一个智能体](../agents/create-agent.md)
[回到首页](../readme.md)

---

## 相关示例

- [单 Agent 示例](../../examples/agents/demo_single_agent.md) — 最简单的 ChatAgent 配置
- [Ollama 本地模型示例](../../examples/llms/demo_ollama.md) — 使用 Ollama 部署的本地模型
- [流式输出 Chat Agent 示例](../../examples/agents/demo_chat_agent_stream.md) — 流式输出的 ChatAgent
