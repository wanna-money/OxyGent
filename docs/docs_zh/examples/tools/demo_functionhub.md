# FunctionHub 自定义工具示例

**源文件:** `examples/tools/demo_functionhub.py`

## 概述

本示例演示如何使用 `FunctionHub` 装饰器模式创建自定义工具，并将其绑定到 ReAct 智能体。示例中定义了一个简单的笑话工具，将其注册到 `FunctionHub`，然后交给 `ReActAgent` 在推理过程中调用。智能体通过 Web UI 启动，并以"请讲一个笑话"作为初始查询。

## 前置条件

- 环境变量（在 `.env` 或终端中设置）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥
  - `DEFAULT_LLM_BASE_URL` -- LLM API 的基础 URL
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符（如 `gpt-4`）
- Python 3.10+ 且已安装项目依赖（`pip install -r requirements.txt`）

## 运行方式

```bash
python -m examples.tools.demo_functionhub
```

## 代码详解

### 配置

使用环境变量创建名为 `"default_llm"` 的 `HttpLLM` 实例，包含 API 密钥、基础 URL 和模型名称。未设置额外的 LLM 参数，使用框架默认值。

### 组件（`oxy_space`）

`oxy_space` 列表包含三个组件：

1. **`HttpLLM("default_llm")`** -- 智能体用于推理的语言模型。
2. **`FunctionHub("joke_tools")`** -- 工具集，将一个或多个 Python 函数注册为可调用工具。通过 `@fh_joke_tools.tool()` 装饰器注册了一个 `joke_tool` 工具。
3. **`ReActAgent("joke_agent")`** -- ReAct 风格的智能体，在 `tools` 列表中引用 `"joke_tools"`。执行过程中，智能体可在推理-行动循环中调用 `joke_tool`。

### 工具定义

`joke_tool` 函数使用 `@fh_joke_tools.tool(description="a tool for telling jokes")` 装饰。该函数接收一个 `joke_type` 参数（通过 Pydantic `Field` 提供描述元数据），从预设列表中随机返回一个笑话。`Field(description=...)` 注解确保 LLM 在获取工具 schema 时能看到清晰的参数描述。

### 入口点

`main()` 协程创建 `MAS`（多智能体系统）上下文管理器，传入 `oxy_space`，然后以初始查询 `"Please tell a joke"` 启动 Web 服务。默认在 `127.0.0.1:8080` 启动 FastAPI 服务器及内置 Web UI。

## 核心概念

- **FunctionHub** -- 一种轻量级方式，将普通 Python 函数封装为智能体可调用的工具。通过 `@hub.tool()` 装饰的每个函数都可以被引用该 hub 名称的智能体发现和调用。
- **Pydantic Field 元数据** -- 在函数参数上使用 `Field(description=...)` 能确保 LLM 获得准确的工具参数描述，提高工具调用准确性。
- **ReActAgent** -- 遵循推理-行动循环的智能体：先推理任务，决定调用哪个工具，观察结果，重复此过程直到得出最终答案。
- **oxy_space** -- 包含所有 Oxy 组件（LLM、工具、智能体）的扁平列表，MAS 运行时通过名称引用将它们连接在一起。

## 预期行为

1. Web 服务器在 `http://127.0.0.1:8080` 启动。
2. 智能体收到查询"Please tell a joke"。
3. 智能体判断应使用 `joke_tool`，并调用该工具（可能传入笑话类型）。
4. 工具从预设列表中随机返回一个笑话。
5. 智能体将笑话展示在 Web UI 中。
