# 通过子类化扩展 Oxy 组件

**源文件:** `examples/backend/demo_rewrite_oxy.py`

## 概述

本示例演示如何通过子类化扩展 OxyGent 的内置组件。示例创建了一个自定义的 `MyHttpLLM` 类，重写 `HttpLLM` 的 `_execute` 方法以实现完全自定义的 LLM API HTTP 请求。当你需要自定义 LLM 请求格式、添加自定义请求头、处理非标准 API 响应或集成具有独特 API 规范的 LLM 提供商时，此模式非常有用。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Python 依赖包：`httpx`

## 运行方式

```bash
python -m examples.backend.demo_rewrite_oxy
```

## 代码详解

### 自定义组件：MyHttpLLM

```python
class MyHttpLLM(oxy.HttpLLM):
    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        headers = {"Content-Type": "application/json"}
        headers.update(self.headers(oxy_request))

        payload = {
            "messages": await self._get_messages(oxy_request),
            "model": self.model_name,
        }
        for k, v in self.llm_params.items():
            payload[k] = v
        for k, v in oxy_request.arguments.items():
            if k == "messages":
                continue
            payload[k] = v

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            http_response = await client.post(
                self.base_url, headers=headers, json=payload
            )
            http_response.raise_for_status()
            data = http_response.json()
            response_message = data["choices"][0]["message"]
            result = response_message.get("content")
            return OxyResponse(state=OxyState.COMPLETED, output=result)
```

自定义类的实现：
1. 使用 `Content-Type` 加上父类 `headers()` 方法返回的请求头构建 headers。
2. 使用消息（来自 Oxy 生命周期）、模型名称、LLM 参数和请求中的额外参数构建 payload。
3. 使用 `httpx` 发送原始 HTTP POST 请求。
4. 解析 OpenAI 兼容的响应格式并提取内容。
5. 返回包含结果的 `OxyResponse`。

### 组件 (`oxy_space`)

| 组件 | 类型 | 关键参数 |
|------|------|----------|
| `default_llm` | `MyHttpLLM` | `HttpLLM` 的自定义子类，重写了 `_execute` 方法 |

### 入口函数

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.call(
        callee="default_llm",
        arguments={
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "hello"},
            ],
            "llm_params": {"temperature": 0.2},
        },
    )
```

本示例不使用 `chat_with_agent`，而是通过 `mas.call()` 直接调用 LLM，展示了任何 Oxy 组件都可以通过名称直接调用。

## 核心概念

- **子类化 Oxy 组件**：任何 Oxy 组件（`HttpLLM`、`BaseAgent`、`BaseTool` 等）都可以通过子类化并重写 `_execute`（智能体则为 `execute`）来扩展。
- **_execute 与 execute**：`_execute` 是 Oxy 生命周期中包含核心逻辑的底层方法。它被 Oxy 生命周期钩子（`_pre_process`、`_post_process`、重试逻辑等）包裹。
- **mas.call()**：通过名称直接调用任何已注册的 Oxy 组件，绕过智能体路由。适用于测试或构建自定义编排逻辑。
- **OxyResponse 构建**：构建自定义组件时，必须返回包含适当 `OxyState` 和输出的 `OxyResponse`。

## 预期行为

1. MAS 使用自定义 `MyHttpLLM` 组件初始化。
2. `mas.call()` 调用向配置的 LLM API 发送聊天补全请求。
3. 自定义 `_execute` 方法构建并发送 HTTP 请求，解析响应，返回 LLM 的回复。
4. 响应以 `state=OxyState.COMPLETED` 的 `OxyResponse` 形式返回。
