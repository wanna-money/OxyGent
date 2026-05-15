# LLM Schemas

---
类所在位置：

```
oxygent/schemas/llm.py
```

---

## 简介

本模块定义了 LLM 响应状态枚举和解析后的响应容器。Agent 使用这些数据结构来解释 LLM 调用的输出——判断 LLM 是要调用工具、提供回答，还是遇到了解析错误。

## LLMState (Enum)

| 成员          | 值               | 描述                             |
| ------------- | ---------------- | -------------------------------- |
| `TOOL_CALL`   | `"tool_call"`    | LLM 请求调用工具。              |
| `ANSWER`      | `"answer"`       | LLM 提供最终回答。              |
| `ERROR_PARSE` | `"error_parse"`  | LLM 输出解析失败。              |
| `ERROR_CALL`  | `"error_call"`   | LLM 调用过程中发生错误。        |

## LLMResponse (BaseModel)

### 参数

| 参数           | 类型 / 允许值                | 默认值     | 描述                                         |
| -------------- | ---------------------------- | ---------- | -------------------------------------------- |
| `state`        | `LLMState`                   | （必填）   | LLM 响应的解析状态。                         |
| `output`       | `Union[str, list, dict]`     | （必填）   | 解析后的输出内容。                           |
| `ori_response` | `str`                        | `""`       | 解析前的 LLM 原始响应文本。                  |
