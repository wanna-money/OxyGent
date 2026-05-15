# 架构总览

> 本文介绍 OxyGent 的整体架构设计，包括统一执行生命周期、类继承层次、请求/响应流程、名称引用机制、MAS 生命周期和部署模式。

---

## Oxy：统一抽象基类

OxyGent 中的所有组件（LLM、Agent、Tool、Flow）都继承自同一个基类 `Oxy`。`Oxy` 基于 Pydantic `BaseModel` 和 Python `ABC`，定义了一套统一的执行生命周期。

### 执行生命周期

每个 Oxy 组件被调用时，都会按以下顺序依次执行各生命周期钩子：

```
调用入口 __call__()
│
├─ _pre_process()         前处理：校验和转换输入
├─ _pre_log()             前置日志：记录请求信息
├─ _pre_save_data()       前置持久化：保存请求到数据库
├─ _format_input()        格式化输入：调用 func_format_input 钩子
├─ _pre_send_message()    前置消息：向前端推送状态
│
├─ _before_execute()      执行前钩子：最后的准备工作
├─ _execute()             核心执行（抽象方法，由子类实现）
│   └─ 支持重试：retries 次数，delay 间隔
├─ _after_execute()       执行后钩子：结果后处理
│
├─ _post_process()        后处理：转换输出
├─ _post_log()            后置日志：记录响应信息
├─ _post_save_data()      后置持久化：保存响应到数据库
├─ _format_output()       格式化输出：调用 func_format_output 钩子
└─ _post_send_message()   后置消息：向前端推送结果
```

每个钩子都可以通过构造参数自定义。例如 `func_process_input` 可在 `_pre_process` 阶段转换请求，`func_format_output` 可在 `_format_output` 阶段格式化响应。

---

## 类继承层次

```
Oxy (oxygent/oxy/base_oxy.py)
│   统一的执行生命周期、并发控制、重试、日志、持久化
│
├── BaseTool (base_tool.py)
│   │   工具基类
│   ├── FunctionHub / FunctionTool    Python 函数工具
│   ├── BaseMCPClient                 MCP 协议客户端基类
│   │   ├── StdioMCPClient            标准输入/输出 MCP
│   │   ├── SSEMCPClient              SSE 协议 MCP
│   │   └── StreamableMCPClient       Streamable 协议 MCP
│   ├── HttpTool                      HTTP API 工具
│   └── BankTool / BankClient         工具银行（跨进程工具服务）
│
├── BaseLLM (llms/base_llm.py)
│   │   大语言模型基类
│   ├── HttpLLM          HTTP API 调用（通用）
│   ├── OpenAILLM        OpenAI SDK 调用
│   ├── LocalLLM         本地 HuggingFace 模型
│   └── MockLLM          测试用模拟模型
│
└── BaseFlow (base_flow.py)
    │   流程基类：包含执行逻辑的组件
    │
    ├── BaseAgent (agents/base_agent.py)
    │   │   智能体基类
    │   ├── LocalAgent           本地智能体基类
    │   │   ├── ChatAgent        基础对话（单轮 LLM 调用）
    │   │   ├── ReActAgent       推理-行动循环
    │   │   ├── ParallelAgent    并行执行
    │   │   ├── PlanAndSolveAgent 先规划后执行
    │   │   ├── WorkflowAgent    自定义工作流
    │   │   ├── RAGAgent         检索增强生成
    │   │   ├── ShellUseAgent    SSH 远程命令
    │   │   └── SkillAgent       动态技能加载
    │   ├── RemoteAgent          远程智能体基类
    │   │   ├── SSEOxyGent       SSE 跨进程连接
    │   │   └── A2AClientAgent   A2A 协议客户端
    │
    └── 预设流程
        ├── Workflow             自定义步骤工作流
        ├── PlanAndSolve         规划-执行流
        ├── Reflexion            反思-重做流
        └── MathReflexion        数学反思流
```

---

## 请求 / 响应流程

下图展示一次用户请求从进入 MAS 到返回结果的完整流程：

```
用户
 │
 ▼
MAS.chat_with_agent(payload)
 │
 ├─ 创建 OxyRequest（trace_id, query, shared_data）
 │
 ▼
Master Agent.__call__(oxy_request)
 │
 ├─ _pre_process  → _pre_log → _pre_save_data
 ├─ _format_input → _pre_send_message
 │
 ├─ _execute()    ← ReActAgent 的推理-行动循环
 │   │
 │   ├─ LLM 推理 → "我需要调用 time_agent"
 │   │
 │   ├─ 调用子智能体 time_agent.__call__(sub_request)
 │   │   ├─ time_agent._execute()
 │   │   │   ├─ LLM 推理 → "调用 get_time 工具"
 │   │   │   ├─ 工具执行 → "2024-01-01 12:00:00"
 │   │   │   └─ LLM 总结 → "当前时间是..."
 │   │   └─ 返回 OxyResponse
 │   │
 │   └─ LLM 总结 → 最终回答
 │
 ├─ _post_process → _post_log → _post_save_data
 ├─ _format_output → _post_send_message
 │
 ▼
OxyResponse（output, state, extra）
 │
 ▼
用户
```

### 核心数据结构

| 结构 | 说明 |
|------|------|
| `OxyRequest` | 请求对象。携带 `trace_id`（追踪标识）、`caller`/`callee`（调用方/被调用方）、`query`（查询内容）、`shared_data`（共享数据） |
| `OxyResponse` | 响应对象。携带 `output`（输出文本）、`state`（`OxyState` 枚举）、`extra`（附加数据） |
| `trace_id` | 唯一追踪标识，贯穿一次完整的调用链 |

---

## 名称引用机制

OxyGent 采用**名称引用**而非 Python 对象引用来连接组件。所有组件在 `oxy_space` 中声明后，由 MAS 统一注册到 `oxy_name_to_oxy` 字典中。

```python
oxy_space = [
    oxy.HttpLLM(name="my_llm", ...),
    oxy.FunctionHub(name="my_tools"),
    oxy.ReActAgent(
        name="my_agent",
        llm_model="my_llm",          # 通过名称引用 LLM
        tools=["my_tools"],           # 通过名称引用工具
        sub_agents=["other_agent"],   # 通过名称引用子智能体
    ),
]
```

这种设计带来以下好处：

- **声明式组装**：组件定义和连接关系分离，便于配置化管理。
- **顺序无关**：`oxy_space` 中的组件不需要按依赖顺序排列。
- **延迟绑定**：实际的引用解析发生在 MAS 初始化阶段，而非组件构造时。

---

## MAS 生命周期

`MAS` 是 OxyGent 的运行时容器，负责管理所有组件的完整生命周期。

```python
async with MAS(oxy_space=oxy_space) as mas:
    # MAS 在此处已完成初始化
    await mas.start_web_service()
# 退出 async with 后，MAS 自动清理资源
```

### 初始化阶段（`__aenter__`）

1. **注册组件**：将 `oxy_space` 中的所有组件注册到 `oxy_name_to_oxy` 字典。
2. **连接数据库**：初始化 Elasticsearch、Redis、Vearch 连接（如果配置了）。
3. **解析引用**：将名称引用解析为实际对象（LLM、工具、子智能体）。
4. **初始化 MCP**：启动所有 MCP 客户端，连接外部工具服务器。
5. **构建组织树**：建立智能体之间的层级关系（`agent_organization`）。
6. **确定入口**：找到 `is_master=True` 的智能体作为 `master_agent_name`。

### 运行阶段

MAS 提供多种运行模式（见下方"部署模式"）。所有模式最终都通过 `chat_with_agent()` 将请求路由到 master 智能体。

### 清理阶段（`__aexit__`）

自动关闭数据库连接、MCP 客户端、后台任务等资源。

---

## 部署模式

MAS 提供四种部署模式，适应不同场景：

### Web 服务模式

启动 FastAPI 服务器，提供 REST API 和内置 Web UI。

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(port=8080)
```

- 默认地址：`http://127.0.0.1:8080`
- 支持同步（`POST /chat`）、SSE 流式（`POST /sse/chat`）、异步（`POST /async/chat`）三种接口。
- 内置可视化调试界面，实时查看智能体推理过程。

### CLI 命令行模式

在终端中交互式对话，适用于开发调试。

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_cli_mode()
```

### 批处理模式

并发执行多个查询，适用于数据处理和评估场景。

```python
async with MAS(oxy_space=oxy_space) as mas:
    results = await mas.start_batch_processing(
        querys=["查询1", "查询2", "查询3"]
    )
```

### 编程式调用

将 MAS 嵌入到应用代码中，适用于后端集成。

```python
async with MAS(oxy_space=oxy_space) as mas:
    response = await mas.chat_with_agent(
        payload={"query": "你好"},
    )
    print(response.output)
```

---

## 总结

| 概念 | 说明 |
|------|------|
| Oxy | 统一抽象基类，定义执行生命周期 |
| 名称引用 | 组件通过 `name` 字符串互相引用 |
| oxy_space | 组件声明列表 |
| MAS | 运行时容器，管理注册、初始化、路由 |
| OxyRequest / OxyResponse | 请求/响应数据结构 |
| trace_id | 调用链追踪标识 |

---

[上一篇: OxyGent 概念总览](./overview.md)
[下一篇: 设置 Config](./config.md)
[返回首页](../readme.md)
