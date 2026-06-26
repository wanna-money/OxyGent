# 高级功能示例

本章节涵盖OxyGent的高级功能，包括多模态智能体、自定义解析器、工具检索、执行控制以及训练数据生成等。

---

### 自定义智能体输入模式

**文件:** `examples/advanced/demo_custom_agent_input_schema.py`

演示如何在WorkflowAgent上定义自定义`input_schema`，使主智能体传递结构化参数而非纯文本查询。本示例中WorkflowAgent声明了两个必填字段（`query`和`precision`），并实现了一个工作流函数，根据请求的精度返回对应位数的圆周率。主ReActAgent会自动将其工具调用格式化为符合该模式的结构。

**核心组件:** `HttpLLM`, `ReActAgent`, `WorkflowAgent(input_schema)`

**[详细文档 →](./demo_custom_agent_input_schema.md)**

---

### 多模态（视觉）智能体

**文件:** `examples/advanced/demo_multimodal.py`

展示如何构建一个使用视觉语言模型（VLM）处理图像的ChatAgent。HttpLLM配置了`is_multimodal_supported=True`和`is_convert_url_to_base64=True`，使图像URL或本地文件路径在发送给模型之前自动转换为base64编码的载荷。该智能体可以回答关于所提供图像内容的问题。

**核心组件:** `HttpLLM(is_multimodal_supported, is_convert_url_to_base64)`, `ChatAgent`

**[详细文档 →](./demo_multimodal.md)**

---

### 多模态转换

**文件:** `examples/advanced/demo_multimodal_transfer.py`

在单个多智能体系统中结合图像理解和图像生成能力。一个具备视觉能力的ChatAgent负责解析上传的图像，而ReActAgent使用预设的`image_gen_tools`根据视觉智能体的描述生成新图像（例如卡通版本）。两个独立的HttpLLM实例分别服务于VLM和文本LLM。

**核心组件:** `HttpLLM` (x2), `preset_tools.image_gen_tools`, `ChatAgent`, `ReActAgent`

**[详细文档 →](./demo_multimodal_transfer.md)**

---

### 信任模式

**文件:** `examples/advanced/demo_trust_mode.py`

对比ReActAgent中`trust_mode=True`和`trust_mode=False`的行为差异。启用信任模式时，智能体会自动执行工具调用而无需等待用户确认；禁用时，每次工具调用都需要用户明确批准。两个智能体使用相同的StdioMCPClient时间工具，便于直观观察执行流程的差异。

**核心组件:** `HttpLLM`, `StdioMCPClient`, `ReActAgent(trust_mode=True/False)`

**[详细文档 →](./demo_trust_mode.md)**

---

### 继续/重启执行

**文件:** `examples/advanced/demo_continue_exec.py`

演示如何使用`restart_node_id`从中间节点继续或重启智能体执行。在首次运行完成后，可以在请求载荷中传入`restart_node_id`（以及可选的`restart_node_output`），从执行追踪中的特定节点开始重放。这对于调试、修正中间结果或分支执行路径非常有用。

**核心组件:** `HttpLLM`, `StdioMCPClient`, `ReActAgent`, `restart_node_id`, `restart_node_output`

**[详细文档 →](./demo_continue_exec.md)**

---

### 从工具发送消息

**文件:** `examples/advanced/demo_send_message_from_tool.py`

展示FunctionHub工具如何在执行过程中向用户发送消息并中断任务执行。示例定义了一个`calc_pi`工具，在计算出指定精度的圆周率后，调用`oxy_request.send_message()`将结果推送到前端，然后调用`oxy_request.break_task()`提前终止智能体循环。当工具直接产出最终答案且无需进一步LLM推理时，此模式非常实用。

**核心组件:** `HttpLLM`, `FunctionHub`, `ReActAgent`, `oxy_request.send_message()`, `oxy_request.break_task()`

**[详细文档 →](./demo_send_message_from_tool.md)**

---

### GRPO风格重采样

**文件:** `examples/advanced/demo_grpo_resample.py`

展示如何重放已完成任务追踪中的LLM节点，以生成多个不同的答案，这些答案可作为GRPO风格流水线中的SFT（监督微调）训练数据。示例首先运行一个多智能体任务，通过`get_task_info`获取追踪中的所有LLM节点，然后通过`restart_node_id`并发重放每个节点以产生多样化的输出。

**核心组件:** `HttpLLM`, `preset_tools`（time、file、math）, `ReActAgent` (x4), `get_task_info`, `restart_node_id`

**[详细文档 →](./demo_grpo_resample.md)**

---

### 自定义LLM响应解析器

**文件:** `examples/advanced/demo_custom_llm_parser.py`

通过在ReActAgent上设置`func_parse_llm_response`，将默认的JSON格式LLM响应解析器替换为自定义的XML格式解析器。自定义解析器从XML标签（`<tool>`、`<answer>`）中提取工具调用和答案，而非JSON格式，返回带有相应`LLMState`的结构化`LLMResponse`对象。同时提供了配套的XML格式提示词来指导LLM。当使用输出非标准格式的模型时，此功能非常有用。

**核心组件:** `HttpLLM`, `StdioMCPClient` (x2), `ReActAgent(func_parse_llm_response)`, `LLMResponse`, `LLMState`

**[详细文档 →](./demo_custom_llm_parser.md)**

---

### Top-K工具检索

**文件:** `examples/advanced/demo_top_k_tools.py`

演示通过向量相似度进行自动Top-K工具检索。在ReActAgent上设置`top_k_tools=N`后，每轮对话中仅将与当前查询最相关的N个工具（按嵌入相似度排序）包含在LLM提示词中。当智能体注册了大量工具时，此功能可以有效缩减提示词长度并提高工具选择的准确性。使用此功能需要配置Vearch向量数据库和嵌入模型。

**核心组件:** `HttpLLM`, `StdioMCPClient` (x2), `ReActAgent(top_k_tools=3)`, Vearch向量数据库

**[详细文档 →](./demo_top_k_tools.md)**

---

### 运行时 Oxy 管理

**文件:** `examples/advanced/demo_oxy_manage.py`

演示如何使用内置的 `oxy_manage_tools` FunctionHub 在运行时动态管理智能体组织架构。一个配备了 `oxy_manage_tools` 的"doctor_agent"可以创建新的智能体、分配工具、在父节点之间移动 Oxy 实例以及删除智能体 — 所有操作均在系统运行过程中完成。示例使用 `first_query` 的 `list[str]` 形式依次发出四条指令：创建数学智能体、解决数学问题、重组智能体结构、查询时间。

**核心组件:** `HttpLLM`, `preset_tools`（math、time、file）, `ReActAgent` (x3), `preset_tools.oxy_manage_tools`, `first_query`（`list[str]` 形式）

**[详细文档 →](./demo_oxy_manage.md)**
