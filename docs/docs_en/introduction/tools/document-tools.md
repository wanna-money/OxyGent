# Document Processing Toolkit User Guide

> OxyGent Document Processing Toolkit - Supports intelligent processing of multiple document formats including PDF, Word, Excel, and more

## Table of Contents

- [Introduction](#introduction)
- [Feature Highlights](#feature-highlights)
- [Installing Dependencies](#installing-dependencies)
- [Quick Start](#quick-start)
- [Tool API Reference](#tool-api-reference)
- [Use Cases](#use-cases)
- [Performance Benchmarks](#performance-benchmarks)

---

## Introduction

The Document Processing Toolkit is a built-in document processing module in OxyGent that provides comprehensive support for mainstream document formats. Whether it's simple text extraction or complex document analysis, it can handle it with ease.

### Supported Formats

| Format | Read | Write | Table Extraction | Image Extraction | Metadata |
|------|------|------|----------|----------|--------|
| **PDF** | Supported | Not Supported | Supported | Supported | Supported |
| **Word (.docx)** | Supported | Not Supported* | Supported | Not Supported | Not Supported |
| **Excel (.xlsx)** | Supported | Not Supported* | N/A | Not Supported | Supported |
| **PowerPoint (.pptx)** | In Development | Not Supported | Not Supported | Not Supported | Not Supported |

*Note: Write support will be available in future versions

---

## Feature Highlights

### High Performance
- **10-50x faster than PyPDF2**: Uses PyMuPDF's C++ underlying engine
- **Memory optimized**: Stream processing for large files to avoid memory overflow
- **Concurrency support**: Supports parallel processing of batch documents

### High Accuracy
- **90%+ table recognition rate**: Uses pdfplumber's advanced algorithms
- **Intelligent layout analysis**: Accurately identifies document structure
- **Full Chinese and English support**: Handles multilingual documents perfectly

### Ease of Use
- **Unified API design**: All tools follow the same invocation pattern
- **Detailed error messages**: Clear error information and resolution suggestions
- **JSON format returns**: Structured data, easy for programmatic processing

### AI Integration
- **Native Agent support**: Can be directly registered as an Agent tool
- **Intelligent document analysis**: Combines LLM for deep content understanding
- **RAG optimized**: Specially optimized for Retrieval-Augmented Generation scenarios

---

## Installing Dependencies

### Full Installation (Recommended)

```bash
# Install all document processing dependencies
pip install PyMuPDF pdfplumber python-docx openpyxl
```

### Install as Needed

```bash
# PDF processing only
pip install PyMuPDF pdfplumber

# Word processing only
pip install python-docx

# Excel processing only
pip install openpyxl
```


### Dependency Details

| Library | Version Requirement | Purpose | License |
|--------|----------|------|--------|
| PyMuPDF | >=1.23.0 | Core PDF processing | AGPL/Commercial dual license |
| pdfplumber | >=0.10.0 | Precise table extraction | MIT |
| python-docx | >=1.1.0 | Word document processing | MIT |
| openpyxl | >=3.1.0 | Excel document processing | MIT |

---

## Quick Start

### Method 1: Direct Tool API Calls

The simplest approach, suitable for scripted processing:

```python
from oxygent.preset_tools.document_tools import extract_pdf_text
import json

# Extract PDF text
result = extract_pdf_text("report.pdf", page_range="1-5")
data = json.loads(result)

if data['success']:
    for page in data['pages']:
        print(f"Page {page['page_number']}:")
        print(page['text'][:200])  # Print first 200 characters
```

### Method 2: Intelligent Processing with an Agent

Let AI understand the document processing requirements:

```python
import asyncio
from oxygent import MAS, Config, oxy, preset_tools

Config.set_agent_llm_model("default_llm")

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key="your_api_key",
        base_url="your_base_url",
        model_name="your_model",
    ),
    preset_tools.document_tools,  # Register document tools
    oxy.ReActAgent(
        name="doc_agent",
        desc="Document processing assistant",
        tools=["document_tools"],
    ),
]

async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Extract all table data from this PDF: report.pdf"
        )

asyncio.run(main())
```

### Method 3: Integrate into an Existing Agent

```python
# Add document processing capabilities to an existing Agent
oxy_space = [
    your_llm,
    preset_tools.document_tools,  # Add document tools
    preset_tools.file_tools,       # File operations
    preset_tools.http_tools,       # HTTP requests
    oxy.ReActAgent(
        name="multi_skill_agent",
        tools=[
            "document_tools",  # Document processing
            "file_tools",      # File operations
            "http_tools"       # Network requests
        ],
    ),
]
```

---

## Tool API Reference

### PDF Processing Tools

#### 1. extract_pdf_text - Extract PDF Text

```python
extract_pdf_text(
    path: str,                      # PDF file path
    page_range: Optional[str] = None,  # Page range: "1-5" or "1,3,5"
    max_chars_per_page: int = 10000    # Maximum characters per page
) -> str  # Returns a JSON string
```

**Return Example:**
```json
{
  "success": true,
  "file_path": "document.pdf",
  "total_pages": 10,
  "extracted_pages": 5,
  "pages": [
    {
      "page_number": 1,
      "text": "Page text content...",
      "char_count": 1523,
      "has_images": true
    }
  ]
}
```

**Use Cases:**
- Document content extraction and analysis
- Document preprocessing for RAG systems
- Text search and index building

#### 2. extract_pdf_tables - Extract PDF Tables

```python
extract_pdf_tables(
    path: str,
    page_range: Optional[str] = None,
    table_settings: Optional[Dict] = None  # Table recognition parameters
) -> str
```

**Return Example:**
```json
{
  "success": true,
  "table_count": 2,
  "tables": [
    {
      "page": 1,
      "table_index": 1,
      "headers": ["Name", "Age", "City"],
      "rows": [
        ["Zhang San", "30", "Beijing"],
        ["Li Si", "25", "Shanghai"]
      ],
      "row_count": 2,
      "column_count": 3
    }
  ]
}
```

**Advanced Configuration:**
```python
# Custom table recognition strategy
table_settings = {
    "vertical_strategy": "lines",    # Vertical line recognition strategy
    "horizontal_strategy": "lines",  # Horizontal line recognition strategy
    "snap_tolerance": 3,             # Line alignment tolerance
    "join_tolerance": 3              # Table merge tolerance
}

result = extract_pdf_tables(
    "complex_table.pdf",
    table_settings=table_settings
)
```

#### 3. extract_pdf_images - Extract PDF Images

```python
extract_pdf_images(
    path: str,
    output_dir: str,             # Image save directory
    page_range: Optional[str] = None,
    min_size: int = 1024        # Minimum image size (bytes)
) -> str
```

**Return Example:**
```json
{
  "success": true,
  "output_dir": "./images",
  "image_count": 5,
  "images": [
    {
      "page": 1,
      "filename": "image_p1_1.png",
      "path": "./images/image_p1_1.png",
      "size_bytes": 45678,
      "format": "png",
      "width": 800,
      "height": 600
    }
  ]
}
```

#### 4. merge_pdfs - Merge PDFs

```python
merge_pdfs(
    pdf_paths: List[str],           # List of PDF files
    output_path: str,               # Output file path
    include_bookmarks: bool = True  # Whether to preserve bookmarks
) -> str
```

**Example:**
```python
result = merge_pdfs(
    pdf_paths=[
        "chapter1.pdf",
        "chapter2.pdf",
        "chapter3.pdf"
    ],
    output_path="full_book.pdf"
)
```

#### 5. split_pdf - Split PDF

```python
split_pdf(
    path: str,
    split_ranges: List[str],  # Split range list
    output_dir: str,
    name_prefix: str = "split"
) -> str
```

**Example:**
```python
# Split a 100-page PDF into 3 files
result = split_pdf(
    path="large_document.pdf",
    split_ranges=["1-30", "31-70", "71-100"],
    output_dir="./chapters"
)
```

#### 6. get_pdf_info - Get PDF Metadata

```python
get_pdf_info(path: str) -> str
```

**Returned Information:**
- Document properties (title, author, subject, keywords)
- Page information (total pages, page dimensions)
- Technical information (PDF version, encryption status)
- Content statistics (text volume, image count)

### Word Document Tools

#### 7. read_docx - Read Word Document

```python
read_docx(
    path: str,
    include_tables: bool = True,
    max_paragraphs: int = 1000
) -> str
```

**Return Example:**
```json
{
  "success": true,
  "statistics": {
    "paragraph_count": 25,
    "table_count": 2,
    "word_count": 1523,
    "char_count": 8965
  },
  "paragraphs": [
    {
      "index": 1,
      "text": "Paragraph content...",
      "style": "Heading 1"
    }
  ],
  "tables": [
    {
      "table_index": 1,
      "row_count": 5,
      "column_count": 3,
      "headers": ["Column 1", "Column 2", "Column 3"],
      "rows": [["Data 1", "Data 2", "Data 3"]]
    }
  ]
}
```

#### 8. extract_docx_text - Extract Word Plain Text

```python
extract_docx_text(path: str) -> str
```

Quickly extracts all text content without formatting information.

### Excel Document Tools

#### 9. read_excel - Read Excel

```python
read_excel(
    path: str,
    sheet_name: Optional[str] = None,  # Worksheet name
    max_rows: int = 100,               # Maximum rows
    has_header: bool = True            # Whether there is a header row
) -> str
```

**Return Example:**
```json
{
  "success": true,
  "sheet_name": "Sales Data",
  "available_sheets": ["Sales Data", "Statistical Report"],
  "statistics": {
    "row_count": 50,
    "column_count": 5,
    "has_header": true
  },
  "headers": ["Date", "Product", "Quantity", "Unit Price", "Total"],
  "rows": [
    ["2024-01-01", "Product A", 10, 99.9, 999],
    ["2024-01-02", "Product B", 20, 49.9, 998]
  ]
}
```

#### 10. list_excel_sheets - List Worksheets

```python
list_excel_sheets(path: str) -> str
```

Returns the names and basic information of all worksheets.

### General Tools

#### 11. detect_document_format - Detect Document Format

```python
detect_document_format(path: str) -> str
```

**Return Example:**
```json
{
  "success": true,
  "filename": "report.pdf",
  "extension": ".pdf",
  "size_mb": 2.5,
  "format_info": {
    "type": "PDF",
    "category": "Portable Document Format",
    "supported": true,
    "tools": [
      "extract_pdf_text",
      "extract_pdf_tables",
      "extract_pdf_images"
    ]
  }
}
```

---

## Use Cases

### Scenario 1: Intelligent Document Q&A System (RAG)

```python
from oxygent.preset_tools.document_tools import extract_pdf_text
from oxygent.databases.db_vector import VectorDB
import json

# 1. Extract PDF content
result = extract_pdf_text("knowledge_base.pdf")
data = json.loads(result)

# 2. Chunk and store in vector database
vector_db = VectorDB()
for page in data['pages']:
    chunks = split_text(page['text'], chunk_size=500)
    for chunk in chunks:
        embedding = get_embedding(chunk)
        vector_db.add(
            text=chunk,
            embedding=embedding,
            metadata={
                "page": page['page_number'],
                "source": "knowledge_base.pdf"
            }
        )

# 3. Use Agent to answer questions
query = "What does the document say about XX?"
relevant_chunks = vector_db.search(query, top_k=5)
answer = agent.ask(query, context=relevant_chunks)
```

### Scenario 2: Batch Report Processing

```python
import json
from pathlib import Path
from oxygent.preset_tools.document_tools import (
    read_excel,
    extract_pdf_tables
)

reports_dir = Path("./monthly_reports")
all_data = []

# Process Excel reports
for excel_file in reports_dir.glob("*.xlsx"):
    result = read_excel(str(excel_file))
    data = json.loads(result)
    if data['success']:
        all_data.extend(data['rows'])

# Process PDF reports
for pdf_file in reports_dir.glob("*.pdf"):
    result = extract_pdf_tables(str(pdf_file))
    data = json.loads(result)
    if data['success']:
        for table in data['tables']:
            all_data.extend(table['rows'])

# Generate summary report
generate_summary_report(all_data)
```

### Scenario 3: Document Content Audit

```python
from oxygent.preset_tools.document_tools import (
    extract_pdf_text,
    get_pdf_info
)

def audit_document(pdf_path):
    """Audit document content and detect sensitive information"""
    # Get document info
    info = json.loads(get_pdf_info(pdf_path))
    
    # Extract full text
    text_result = json.loads(extract_pdf_text(pdf_path))
    
    # Sensitive word detection
    sensitive_words = ["confidential", "classified", "internal"]
    found_sensitive = []
    
    for page in text_result['pages']:
        for word in sensitive_words:
            if word in page['text']:
                found_sensitive.append({
                    "page": page['page_number'],
                    "keyword": word
                })
    
    # Generate audit report
    return {
        "file": pdf_path,
        "pages": info['document_properties']['page_count'],
        "author": info['document_metadata']['author'],
        "sensitive_items": found_sensitive,
        "risk_level": "high" if found_sensitive else "low"
    }
```

### Scenario 4: Multilingual Document Translation

```python
async def translate_document(pdf_path, target_lang="en"):
    """Extract document content and translate"""
    from oxygent import MAS, oxy, preset_tools
    
    # Extract original text
    result = extract_pdf_text(pdf_path)
    data = json.loads(result)
    
    # Use Agent for translation
    oxy_space = [
        your_llm,
        preset_tools.document_tools,
        oxy.ReActAgent(
            name="translator_agent",
            desc=f"Translate text into {target_lang}",
            tools=["document_tools"]
        )
    ]
    
    translations = []
    async with MAS(oxy_space=oxy_space) as mas:
        for page in data['pages']:
            query = f"Translate the following content into {target_lang}: {page['text'][:500]}"
            response = await mas.ask("translator_agent", query)
            translations.append(response)
    
    return translations
```

---

## Performance Benchmarks

### Test Environment
- CPU: Intel i7-12700K
- RAM: 32GB
- File: 100-page PDF, 10MB

### Performance Comparison

| Operation | PyMuPDF | PyPDF2 | pdfplumber | Improvement |
|------|---------|--------|------------|----------|
| Text extraction | 0.3s | 1.2s | 2.5s | **4-8x** |
| Table extraction | 1.5s | N/A | 3.8s | **2.5x** |
| Image extraction | 0.8s | 2.1s | N/A | **2.6x** |
| PDF merge | 0.5s | 1.8s | N/A | **3.6x** |
| Memory usage | 80MB | 150MB | 200MB | **50% savings** |

### Large File Processing Capacity

| File Size | Pages | Processing Time | Peak Memory |
|---------|------|---------|----------|
| 1MB | 10 pages | 0.1s | 50MB |
| 10MB | 100 pages | 0.8s | 120MB |
| 50MB | 500 pages | 3.5s | 280MB |
| 100MB | 1000 pages | 7.2s | 450MB |

---



## Best Practices

### 1. Error Handling

```python
import json
from oxygent.preset_tools.document_tools import extract_pdf_text

def safe_extract_pdf(pdf_path):
    """Safe PDF extraction with comprehensive error handling"""
    try:
        result_str = extract_pdf_text(pdf_path)
        result = json.loads(result_str)
        
        if result.get('success'):
            return result
        else:
            logger.error(f"Extraction failed: {result.get('error')}")
            return None
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unknown error: {e}")
        return None
```

### 2. Performance Optimization

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_documents_parallel(file_list):
    """Process multiple documents in parallel"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                extract_pdf_text,
                file_path
            )
            for file_path in file_list
        ]
        results = await asyncio.gather(*tasks)
    
    return results
```

### 3. Result Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def extract_pdf_cached(pdf_path, page_range):
    """Cache PDF extraction results"""
    return extract_pdf_text(pdf_path, page_range)

# Or use file content hash as cache key
def get_file_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

cache = {}

def extract_with_content_cache(pdf_path):
    file_hash = get_file_hash(pdf_path)
    
    if file_hash in cache:
        return cache[file_hash]
    
    result = extract_pdf_text(pdf_path)
    cache[file_hash] = result
    return result
```

---

## Related Examples

- [Document Tool Usage Example](../../examples/tools/demo_document_tools.md) -- Demonstrates the complete workflow of document processing tools
- [Document Analysis Agent Example](../../examples/agents/demo_document_analysis_agent.md) -- Demonstrates how to build a document analysis agent
- [RAG Agent Example](../../examples/agents/demo_rag_agent.md) -- Demonstrates retrieval-augmented generation based on documents
