# 向 MAS 添加自定义 FastAPI 路由

**源文件:** `examples/backend/demo_add_router.py`

## 概述

本示例演示如何使用自定义 FastAPI 路由扩展 MAS 内置的 Web 服务。通过向 `MAS` 构造函数传入 `APIRouter`，可以在默认的 `/chat`、`/sse/chat` 等 MAS 端点之外暴露额外的 HTTP 接口。当你的智能体系统需要为智能体或外部客户端提供辅助 API 时，此模式非常实用。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Python 依赖包：`httpx`、`fastapi`

## 运行方式

```bash
python -m examples.backend.demo_add_router
```

## 代码详解

### 自定义路由

创建一个 FastAPI `APIRouter` 并注册一个端点：

```python
router = APIRouter()

@router.get("/api_name")
def api_name():
    return WebResponse(data={"key": "value"}).to_dict()
```

该端点定义了 `GET /api_name` 接口，返回包含 `{"key": "value"}` 的 `WebResponse`。

### 工作流函数

`workflow` 函数是一个异步可调用对象，作为智能体的执行逻辑。它使用 `httpx.AsyncClient` 调用同一服务器上的自定义 `/api_name` 端点：

```python
async def workflow(oxy_request: OxyRequest):
    async with httpx.AsyncClient() as client:
        response = await client.get(url="http://127.0.0.1:8080/api_name")
        return response.json()
```

这表明智能体可以调用同一 MAS Web 服务上托管的自定义 API 路由。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `HttpLLM` | 从环境变量获取的标准 LLM 凭证 |
| `master_agent` | `WorkflowAgent` | 通过 `func_workflow=workflow` 定义执行逻辑 |

### 入口函数

`MAS` 使用 `routers=[router]` 参数实例化，该参数将自定义路由注册到 FastAPI 应用中：

```python
async with MAS(oxy_space=oxy_space, routers=[router]) as mas:
    await mas.start_web_service(first_query="hello")
```

## 核心概念

- **自定义路由**：`MAS` 构造函数接受 `routers` 参数（`APIRouter` 实例列表），将额外的端点挂载到内置 FastAPI 服务器上。
- **WorkflowAgent**：一种智能体类型，其逻辑完全由用户提供的异步函数（`func_workflow`）定义，绕过 LLM 驱动的推理流程。
- **自引用 API 调用**：运行在 MAS 内部的智能体可以调用同一 MAS Web 服务的端点，实现模块化的 API 驱动架构。

## 预期行为

1. MAS Web 服务在 `127.0.0.1:8080` 上启动。
2. 自定义 `/api_name` 端点变为可用。
3. 当智能体处理初始查询 `"hello"` 时，工作流函数调用 `GET /api_name` 并返回 JSON 响应 `{"key": "value"}`。
4. Web UI 打开并显示结果。
