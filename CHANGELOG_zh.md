# Changelog

所有重要变更将在此文件中记录。

## [Unreleased]

### Added
- 新增 `oxy_manage_tools` — 系统级 FunctionHub，支持运行时对 Agent 组织架构进行 CRUD 操作（列出、查看、创建、删除、移动、修改 Oxy 实例）
- 新增细粒度缓存 Token 追踪，覆盖 5 个 LLM 供应商
- 新增 `first_query` 支持 `list[str]` 类型，前端新增 querys 面板

---

## [1.1.1] - 2026-05-16

### Added
- 新增 A2A（Agent-to-Agent）网关/客户端架构，含互操作性示例和文档
- 新增 Trace 图可视化，支持时间线、节点高亮和重新运行
- 新增断点续执行能力
- 新增聊天消息 Markdown 渲染
- 新增技能（Skill）召回机制
- 新增文件附件缩略图预览
- 新增 Memory 持久化到 Elasticsearch
- 新增后台异步任务管理（按 trace_id 索引）
- 新增 CORS 跨域源配置
- 新增 Web UI 面板拖拽调整大小

### Changed
- 优化代码结构和注释
- 修改 chat API 响应格式
- 在 trace 表中存储原始 payload

### Fixed
- 修复 Trace 图渲染问题
- 修复本地 ES 查询 Bug
- 修复文件上传接口
- 修复重启节点输出问题

---

## [1.0.13] - 2026-04-06

### Added
- 新增 Token 用量追踪和配置支持
- 新增工具挂载（mounts）支持

### Fixed
- 修复 OxyBank 中的 CWE-22 路径穿越漏洞
- 限制文件访问权限
- 修复 MAS 中 group_data 被覆盖的问题，补充 `replanner_agent_name`

### Changed
- 优化 SkillAgent 的提示词

---

## [1.0.12] - 2026-03-08

### Added
- 新增 SkillAgent，集成技能能力
- 新增 ShellUseAgent，支持 Shell 操作
- 新增 Trigger 服务，支持事件驱动的 Agent 调用

### Fixed
- 修复 ReActAgent 的 trust_mode
- 修复 SSH 工具问题
- 修复 OxyBank 依赖问题
- 修复单元测试 Bug

---

## [1.0.11] - 2026-01-23

### Added
- 新增 History 管理界面，支持按条件搜索历史对话内容
- 新增 Prompt 优化功能
- 在 shared_data 中新增首响耗时统计项
- 新增 PlanAndSolveAgent，支持动态判断下一步"重新规划、继续执行或直接中断"，详见 [./examples/agents/demo_plan_and_solve_agent.py](./examples/agents/demo_plan_and_solve_agent.py)
- 新增 Agent 发现接口 `/get_description`，SSEOxyGent 初始化时自动调用该接口
- 新增 OxyBank，用于标准化智能体输入
- 新增消息评价和对话历史功能及 UI
- 新增多实例间版本协调

### Changed
- 动态提示词管理功能默认修改为不开启
- 丰富 trust_mode 能力，并去除 trust_mode 模式下 answer 的多余前缀
- 优化提示词

---

## [1.0.10] - 2025-12-26

### Added
- 新增 Prompt 管理界面，支持在线修改 Prompt
- 支持本地大模型 LocalLLM 类
- 新增 `oxy.BaseBank`，用于标准化智能体输入信息
- 新增 SSEOxyGent 和 SSE 工具类
- 新增 Live Prompt 热加载系统（基于 Elasticsearch）
- 新增异步 Trace API（`/async/chat` 和 `/async/trace`）
- 支持 SSE 重试的指数退避机制
- 新增用户反馈接口 `/feedback`，用于实现 human-in-the-loop，详见 [./examples/backend/demo_human_in_the_loop.py](./examples/backend/demo_human_in_the_loop.py)

### Changed
- 修改 ES 包，由 `elasticsearch[async]` 改为 `elasticsearch`
- 修改描述附件的格式
- 增强代码抽象

---

## [1.0.9] - 2025-12-12

### Added
- 新增 oxy.BaseLLM 参数，支持自定义多模态 base64 前缀
- MAS 类新增 `func_process_message` 方法，用于统一处理消息，详见 [./examples/backend/demo_process_message.py](./examples/backend/demo_process_message.py)
- 新增流式消息结束标识的 `stream_end` 消息
- stream 消息支持分批存储
- 前置打印 payload 日志，便于排查
- 标准化 SSE 消息字段 `id`、`event`、`data`
- SSEOxyGent 透传 headers
- 新增 uvicorn workers 数量配置参数
- 新增 K8s MCP Server

### Changed
- 默认仅在 SSE 模式下发送消息
- 修改 message 表结构，新增字段
- history 表存储时，memory 的 answer 字段强转 str

### Fixed
- `chat_with_agent` 函数入参 `send_msg_key` 参数为空时，修改为不发送消息
- 修复 LLM 流式模式 Bug

### Security
- 通过在 OxyFactory 中阻止危险类来防止 RCE 攻击

---

## [1.0.8] - 2025-11-14

### Added
- 新增前端的流式输出能力
- think 消息增加 Agent 名称字段
- 新增文档处理工具集（支持 PDF、Word、Excel 等格式）
- 新增 MCP `timeout` 参数支持
- 新增 TTS 演示（使用 MCP 工具）

### Changed
- LLM 参数 `stream` 默认值修改为 `True`
- LocalRedis 改为异步实现

### Fixed
- 移除 base_oxy.py 中的重复代码

---

## [1.0.7] - 2025-10-27

### Added
- 新增细粒度的消息存储，详见 [./examples/advanced/demo_save_message.py](./examples/advanced/demo_save_message.py)
- 新增自定义智能体输入结构体示例，详见 [./examples/advanced/demo_custom_agent_input_schema.py](./examples/advanced/demo_custom_agent_input_schema.py)
- 新增智能体之间的多模态信息传递机制，详见 [./examples/advanced/demo_multimodal_transfer.py](./examples/advanced/demo_multimodal_transfer.py)
- 新增 MCP 工具 `functions` 支持
- 新增 MAS Hook 示例
- 新增 Code Interpreter 工具（后移除）
- 新增 `sql_tools` 预置工具
- 新增中间件和拦截器支持
- `delete_file` 支持目录递归删除

### Changed
- Vearch 配置参数 `tool_df_space_name` 更名为 `tool_space_name`
- 修改 `config.json` 中引用的环境变量名称
- 上传附件后，自动生成外部可访问的 Web 链接
- 调整示例目录结构

### Fixed
- 修复一轮对话中，多智能体之间多次交互未正确记录历史的问题
- 修复上传目录不存在的 Bug
- 修复断点重启逻辑
- 修复 function_tools 中必填参数无默认值的 Bug

### Removed
- 移除对 `payload` 中 `web_file_url_list` 的支持

---

## [1.0.6] - 2025-09-21

### Added
- 新增 RAG Agent 支持
- 新增异步 API 接口
- 新增图像生成工具
- 新增火车票工具
- 新增百度搜索工具
- 新增 shell-tools 和 math_tools 的单元测试

### Changed
- 增强 math_tool 的通用计算能力
- 支持添加自定义 Routers

### Fixed
- 修复 message ES 表问题
- 修复 function_tools 必填参数无默认值 Bug
- 动态导入模块以避免冲突

---

## [1.0.5] - 2025-09-01

### Added
- 新增 `group_data` 数据隔离逻辑
- 日志中附加 trace_id
- 新增 get/set 工具函数
- trace 表中存储 shared_data
- 新增 MCP 动态 headers 支持
- 新增 ES Schema 定义
- 工具参数支持 Optional 类型

### Changed
- 创建 ES 表时支持自定义 settings

---

## [1.0.4] - 2025-08-25

### Added
- 新增 Python 和 Shell 预置工具
- 新增 SQL 工具
- 新增 Web API 接口
- 工具支持异步函数
- 新增 MCP 自动重连机制

### Changed
- 支持每个 Agent 独立的短期记忆大小
- 支持全局最大记忆轮次
- 支持 arguments 中存储完整 memory
- 支持修改 Redis 数据库编号
- MCP 工具不再需要维持长连接

### Fixed
- 修复输入格式问题
- 修复单元测试错误

---

## [1.0.3] - 2025-08-15

### Added
- 新增全局数据（global_data）支持
- 新增自定义 OxyRequest Schema
- 新增文件附件支持
- 新增 request_id 追踪
- 新增 Streamable MCP 工具支持
- 新增 group_id 多租户隔离支持
- 新增 shared_data Schema 配置
- 新增 Gemini API 支持

### Changed
- shared_data 移入 node 中
- 设置默认环境变量文件
- 所有 Oxy 支持拦截器
- 更新 MCP requirements 版本

### Fixed
- 修复流式输出问题
- 修复 shared_data 处理
- 修复 dict 参数描述
- 修复 callee 不存在时的提示信息
- 修复 plan_and_solve 重复行
- 修复 Deepseek 模型流式输出 Bug

---

## [1.0.2] - 2025-07-30

### Added
- 新增追加 Prompt 能力
- 重构 Reflexion Agent
- 新增 Ollama 支持（HttpLLM）
- 新增用户指南文档（简体中文）
- 新增浏览器操作工具示例

### Changed
- HttpLLM 自动补全 URL

### Fixed
- 修复本地 ES 节点查询和列表格式
- 修复 shared_data 转换问题
- 修复 LocalAgent 的 team_work 拷贝问题
- 修复 HttpLLM 丢弃无效 payload 键
- 修复 aioredis 在 Python 3.13 的兼容性 Bug

---

## [1.0.1] - 2025-07-21

### Added
- OxyGent 多智能体框架首次发布
- 核心 Oxy 抽象，统一的执行生命周期
- ReActAgent、ChatAgent、ParallelAgent、WorkflowAgent
- FunctionHub 和 FunctionTool 系统
- MCP 工具集成（StdioMCPClient）
- HttpLLM 和 OpenAILLM 支持
- MAS 运行时容器，含 CLI 和 Web 服务
- Elasticsearch 和 Redis 存储后端
- SSE 流式推送支持
- 内置预置工具（file、math、time、http、string、system、ssh）
- Web UI 聊天交互界面
