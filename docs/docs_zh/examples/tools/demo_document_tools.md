# 文档处理工具集示例

**源文件:** `examples/tools/demo_document_tools.py`

## 概述

本示例全面演示了 OxyGent 内置文档处理工具的多种使用方式，支持处理 PDF、Word (.docx) 和 Excel (.xlsx) 文件。包含五个子示例，从基础格式检测到智能体驱动的文档分析，涵盖直接 API 调用、批量处理和智能体工作流。

## 前置条件

- 环境变量（在 `.env` 或终端中设置，智能体相关示例需要）：
  - `DEFAULT_LLM_API_KEY` -- LLM 服务的 API 密钥
  - `DEFAULT_LLM_BASE_URL` -- LLM API 的基础 URL
  - `DEFAULT_LLM_MODEL_NAME` -- 模型标识符
- 额外 Python 依赖包：`PyMuPDF`、`pdfplumber`、`python-docx`、`openpyxl`
  ```bash
  pip install PyMuPDF pdfplumber python-docx openpyxl
  ```
- `./test_documents` 目录中放置 PDF、Word 或 Excel 测试文件（目录不存在会自动创建）
- 项目中需包含 `function_hubs/document_tools` 模块

## 运行方式

```bash
python -m examples.tools.demo_document_tools
```

## 代码详解

### 配置

`load_config()` 辅助函数验证所有必需的 LLM 环境变量是否已设置。如果缺失，智能体相关示例（示例2和4）会优雅跳过，非 LLM 示例仍然正常运行。

### 示例1：基础文档处理

**函数:** `demo_basic_document_processing()`

直接调用 `function_hubs.document_tools` 模块中的 `detect_document_format()` 函数，检测给定文件的格式、大小和支持的工具。这是最底层的用法——直接调用工具函数，不涉及任何智能体或 MAS。

### 示例2：文档处理智能体

**函数:** `demo_document_agent()`

创建名为 `"document_agent"` 的 `ReActAgent`，配置了：
- `preset_tools.document_tools` -- 内置文档工具集
- 详细的系统提示词，指导智能体检测文档类型、选择合适的工具并清晰地呈现结果

智能体通过 `mas.start_web_service()` 启动，初始查询要求其描述文档处理能力。

### 示例3：批量文档处理

**函数:** `demo_batch_processing()`

扫描 `./test_documents` 目录中的所有 PDF、Word 和 Excel 文件，逐一处理：
1. 使用 `detect_document_format()` 检测文档格式
2. 对 PDF 文件使用 `get_pdf_info()` 获取详细信息
3. 收集结果并生成汇总报告，保存为 `batch_report.json`

这演示了无需 LLM 参与的程序化批量处理。

### 示例4：文档内容分析智能体

**函数:** `demo_document_analysis_agent()`

高级智能体配置，组合了 `document_tools` 和 `file_tools`（用于保存报告）。智能体使用专门的分析提示词，引导其按结构化流程工作：识别文档类型、提取内容、深入分析、生成结构化报告。

### 示例5：直接调用工具 API

**函数:** `demo_direct_tool_usage()`

打印代码片段，展示如何直接调用各文档工具函数：
- `extract_pdf_text()` -- 提取指定 PDF 页面的文本
- `get_pdf_info()` -- 获取 PDF 元数据和统计信息
- `merge_pdfs()` -- 合并多个 PDF 文件
- `split_pdf()` -- 按页码范围拆分 PDF
- `read_docx()` -- 读取 Word 文档段落
- `read_excel()` -- 读取 Excel 工作表数据

### 入口点

`main()` 函数依次运行所有五个示例。非 LLM 示例先执行，随后是智能体相关示例。键盘中断和异常都有优雅的错误处理。

## 核心概念

- **preset_tools** -- OxyGent 的内置工具集合（如 `preset_tools.document_tools`、`preset_tools.file_tools`），可直接添加到 `oxy_space` 中，无需手动定义工具。
- **直接工具调用** -- 文档工具函数可直接从 Python 导入调用，用于脚本化和批量工作流，完全绕过智能体层。
- **智能体驱动的文档处理** -- 将文档工具与 ReActAgent 及精心设计的系统提示词结合，智能体可根据文档类型和用户请求自主选择使用哪些工具。
- **Config.set_agent_llm_model()** -- 全局设置所有智能体的默认 LLM 模型名称，避免在每个智能体上单独指定 `llm_model`。
- **结构化工具输出** -- 所有文档工具返回 JSON 字符串，便于程序化解析处理。

## 预期行为

1. **示例1**：如果 `./test_documents/example.pdf` 存在，打印其格式、大小和支持的工具；否则显示跳过信息。
2. **示例2**：Web 服务器启动，文档处理智能体描述其处理能力。
3. **示例3**：扫描 `./test_documents` 中的所有文档，生成 JSON 报告。
4. **示例4**：Web 服务器启动，高级分析智能体可生成结构化文档报告。
5. **示例5**：在控制台打印直接调用工具 API 的代码片段。
