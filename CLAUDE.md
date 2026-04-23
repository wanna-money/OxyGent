# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OxyGent is an open-source multi-agent collaboration framework by JD.com. It unifies tools, models, and agents into modular "Oxy" components that snap together to build, run, and evolve multi-agent systems. Python 3.10+.

## Development Setup

```bash
# Create environment (conda or uv)
conda create -n oxy_env python==3.10 && conda activate oxy_env
# or
uv venv .venv --python 3.10 && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Node.js required if using MCP tools
```

Environment variables go in `.env` (auto-loaded via `dotenv`):
```
DEFAULT_LLM_API_KEY=...
DEFAULT_LLM_BASE_URL=...
DEFAULT_LLM_MODEL_NAME=...
```

## Common Commands

```bash
# Run demo
python demo.py

# Run a single-agent example
python -m examples.agents.demo_single_agent

# Unit tests
pytest test/unittest

# Run a single test file
pytest test/unittest/test_react_agent.py

# Integration tests (requires LLM/DB credentials)
pytest test/integration

# Format code
ruff format .
docformatter -r -i --wrap-summaries 88 --wrap-descriptions 88 oxygent/
```

CI (`ci.yml`) runs `ruff format .` then `pytest test/unittest` on Python 3.10.

## Architecture

### Core Abstraction: Oxy

Everything is an **Oxy** (`oxygent/oxy/base_oxy.py`). The `Oxy` class is a Pydantic `BaseModel` + `ABC` that defines a unified execution lifecycle:

```
_pre_process -> _pre_log -> _pre_save_data -> _format_input -> _pre_send_message
  -> _before_execute -> _execute (abstract, with retry) -> _after_execute
  -> _post_process -> _post_log -> _post_save_data -> _format_output -> _post_send_message
```

Every component (agents, tools, LLMs, flows) inherits from `Oxy` and implements `_execute()`.

### Class Hierarchy

```
Oxy (base_oxy.py)
├── BaseTool (base_tool.py) ─── tools, MCP clients, function tools
├── BaseLLM (llms/base_llm.py) ─── HttpLLM, OpenAILLM, LocalLLM, MockLLM
└── BaseFlow (base_flow.py)
    ├── BaseAgent (agents/base_agent.py)
    │   └── LocalAgent → ReActAgent, ChatAgent, ParallelAgent,
    │       PlanAndSolveAgent, WorkflowAgent, RAGAgent, ShellUseAgent, SkillAgent
    │   └── RemoteAgent, SSEOxyGent
    └── Flows: Workflow, PlanAndSolve, Reflexion, MathReflexion
```

### MAS (Multi-Agent System) - `oxygent/mas.py`

The runtime container. `MAS` registers all Oxy instances into `oxy_name_to_oxy` (a name-to-instance dict), initializes DB connections, builds the agent organization tree, and provides:
- `start_web_service()` - FastAPI + SSE server with built-in web UI
- `start_cli_mode()` - Interactive REPL
- `start_batch_processing()` - Concurrent batch execution
- `chat_with_agent()` - Core entry point that routes to the master agent

Usage pattern (async context manager):
```python
async with MAS(oxy_space=[...]) as mas:
    await mas.start_web_service()
```

### Request/Response Flow

- `OxyRequest` (`oxygent/schemas/oxy.py`) - carries trace_id, caller/callee names, arguments, shared_data
- `OxyResponse` - carries output, state (OxyState enum), extra data
- Tracing: each call gets a `trace_id`; conversation history links via `from_trace_id`

### Key Terminology (from schemas/oxy.py)

- **mas**: runtime container that routes messages among agents/tools
- **oxy**: an autonomous object (agent or tool) callable by others
- **trace**: a conversation thread (sessions can branch into traces)
- **caller/callee**: parent node / the node being entered during a nested call

### Config System - `oxygent/config.py`

`Config` is a classmethod-based singleton. Loads from `config.json` with environment layering (`default` -> `APP_ENV`). Supports `${VAR}` env-var substitution. Key sections: `llm`, `agent`, `tool`, `server`, `es`, `redis`, `message`, `token_tracking`, `live_prompt`.

### Tool Types

- **FunctionHub / FunctionTool** (`oxy/function_tools/`) - Python function wrappers
- **MCPTool** with **StdioMCPClient / StreamableMCPClient / SSEMCPClient** (`oxy/mcp_tools/`) - MCP protocol tools
- **HttpTool** (`oxy/api_tools/`) - HTTP API wrappers
- **BankTool / BankClient** (`oxy/bank_tools/`) - FastAPI router-based tool banks
- **Preset tools** (`oxygent/preset_tools/`) - built-in tools: file, math, time, shell, python, http, image_gen, ssh, string, system

### Storage Layer

- **Elasticsearch** (or local fallback `LocalEs`) - traces, nodes, messages, prompts, ratings
- **Redis** (or local fallback `LocalRedis`) - SSE message queuing between backend and frontend
- **Vearch** (optional) - vector DB for tool retrieval

### Web Service

FastAPI app at `127.0.0.1:8080` (default). Key endpoints:
- `POST /chat` - synchronous chat
- `POST /sse/chat` - SSE streaming chat
- `POST /async/chat` - async chat with trace polling
- `GET /get_organization` - agent tree structure
- Static web UI served from `oxygent/web/`

### Live Prompt Management - `oxygent/live_prompt/`

Hot-reloadable prompt system backed by ES. Allows runtime prompt updates without restart.

## Package Layout

- `oxygent/` - main package
- `oxygent/oxy/` - core Oxy classes (agents, flows, tools, LLMs)
- `oxygent/schemas/` - Pydantic models (OxyRequest, OxyResponse, OxyState, Memory, etc.)
- `oxygent/utils/` - utilities (common, data, env, token, SSE)
- `oxygent/databases/` - DB abstractions (ES, Redis, Vearch)
- `oxygent/preset_tools/` - built-in FunctionHub tools
- `oxygent/live_prompt/` - hot-reload prompt management
- `mcp_servers/` - standalone MCP server implementations (browser, delivery, inventory, etc.)
- `function_hubs/` - additional function hub definitions
- `examples/` - usage examples organized by feature area
- `test/unittest/` - unit tests (mocked, no external services)
- `test/integration/` - integration tests (require running services)
- `applications/` - full application examples


现在只能选中实线箭头，不能选中虚线箭头，但其实实线箭头和虚线箭头是同一个节点，所以请改成选中后实线箭头和虚线箭头都高亮。
在oxygent/web/index.html页面，对话的输入框目前只允许单行，请改成多行。另外，因为“@Agent”设计的原因，导致输入框的顶部预留就空白了，请解决。