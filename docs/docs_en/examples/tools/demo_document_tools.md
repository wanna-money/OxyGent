# Document Processing Tools Demo

**Source:** `examples/tools/demo_document_tools.py`

## Overview

This comprehensive example demonstrates multiple ways to use OxyGent's built-in document processing tools for handling PDF, Word (.docx), and Excel (.xlsx) files. It contains five sub-examples that progress from basic format detection to agent-driven document analysis, covering direct API calls, batch processing, and intelligent agent workflows.

## Prerequisites

- Environment variables (set in `.env` or shell, required for agent-based examples):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM API
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier
- Additional Python packages: `PyMuPDF`, `pdfplumber`, `python-docx`, `openpyxl`
  ```bash
  pip install PyMuPDF pdfplumber python-docx openpyxl
  ```
- A `./test_documents` directory containing sample PDF, Word, or Excel files (created automatically if absent)
- The `function_hubs/document_tools` module must be available in the project

## How to Run

```bash
python -m examples.tools.demo_document_tools
```

## Code Walkthrough

### Configuration

The `load_config()` helper validates that all required LLM environment variables are set. If any are missing, the agent-based examples (2 and 4) are skipped gracefully while the non-LLM examples still run.

### Example 1: Basic Document Processing

**Function:** `demo_basic_document_processing()`

Directly calls `detect_document_format()` from the `function_hubs.document_tools` module to detect the format, size, and supported tools for a given file. This demonstrates the lowest-level usage -- calling tool functions directly without any agent or MAS involvement.

### Example 2: Document Processing Agent

**Function:** `demo_document_agent()`

Creates a `ReActAgent` named `"document_agent"` with:
- `preset_tools.document_tools` -- the built-in document tool hub
- A detailed system prompt instructing the agent to detect document types, choose appropriate tools, and present results clearly

The agent is started via `mas.start_web_service()` with an initial query asking it to describe its document processing capabilities.

### Example 3: Batch Document Processing

**Function:** `demo_batch_processing()`

Scans `./test_documents` for all PDF, Word, and Excel files, then iterates through each one:
1. Detects the document format using `detect_document_format()`
2. For PDF files, retrieves detailed info using `get_pdf_info()`
3. Collects results and generates a summary report saved as `batch_report.json`

This demonstrates programmatic batch processing without any LLM involvement.

### Example 4: Document Content Analysis Agent

**Function:** `demo_document_analysis_agent()`

An advanced agent setup that combines `document_tools` and `file_tools` (for saving reports). The agent uses a specialized analysis prompt that guides it through a structured workflow: identify document type, extract content, perform deep analysis, and produce a structured report.

### Example 5: Direct Tool API Usage

**Function:** `demo_direct_tool_usage()`

Prints code snippets showing how to call each document tool function directly:
- `extract_pdf_text()` -- Extract text from specific PDF pages
- `get_pdf_info()` -- Get PDF metadata and statistics
- `merge_pdfs()` -- Merge multiple PDFs into one
- `split_pdf()` -- Split a PDF by page ranges
- `read_docx()` -- Read Word document paragraphs
- `read_excel()` -- Read Excel worksheet data

### Entry Point

The `main()` function runs all five examples sequentially. Non-LLM examples run first, followed by the agent-based examples. Keyboard interrupts and exceptions are handled gracefully.

## Key Concepts

- **preset_tools** -- OxyGent's built-in tool collections (e.g., `preset_tools.document_tools`, `preset_tools.file_tools`) that can be directly added to an `oxy_space` without manual tool definition.
- **Direct tool invocation** -- Document tool functions can be imported and called directly from Python for scripting and batch workflows, bypassing the agent layer entirely.
- **Agent-driven document processing** -- By combining document tools with a ReActAgent and a well-crafted system prompt, the agent can autonomously choose which tools to use based on the document type and user request.
- **Config.set_agent_llm_model()** -- Sets the default LLM model name for all agents globally, avoiding the need to specify `llm_model` on each agent individually.
- **Structured tool output** -- All document tools return JSON strings, making it easy to parse results programmatically.

## Expected Behavior

1. **Example 1**: If a file `./test_documents/example.pdf` exists, its format, size, and supported tools are printed. Otherwise, a skip message appears.
2. **Example 2**: A web server starts with a document processing agent that describes its capabilities.
3. **Example 3**: All documents in `./test_documents` are scanned and a JSON report is generated.
4. **Example 4**: A web server starts with an advanced analysis agent that can produce structured document reports.
5. **Example 5**: Code snippets demonstrating direct tool API usage are printed to the console.
