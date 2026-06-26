# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Added `ActorLLM` — a new LLM backend that runs inference on local transformer models via Ray actors
- Added `upsert()` method to all ES clients (`BaseEs`, `JesEs`, `LocalEs`, `MemoryEs`) providing create-or-update semantics
- Added "Locate" button on agent log nodes for jumping to the corresponding node in the Trace Graph
- Added chat message click-to-jump: clicking a chat message navigates to the frame where it first appeared
- Added Trace Graph node highlighting that syncs with the current timeline position
- Added rerun divider in chat history to visually separate conversation turns across reruns

### Changed
- Optimized `LocalEs` with write-behind caching for significantly improved concurrent write performance
- Changed `_pre_save_data` and `_post_save_data` in `Oxy` to use `upsert()` instead of `index()`/`update()`, eliminating race conditions in concurrent node persistence
- Improved input MD5 hash computation to be deterministic for `set` and `dict` types
- Improved session serialization format (v2) for save/load/export/import with full branch and trace state preservation
- Improved rerun flow: new branch now forks from the owner of the rerun node with correct chat history restoration
- Changed timeline and Trace Graph highlight color from blue to amber for better visual distinction

### Fixed
- Fixed node data loss (`input`/`output` fields missing) under high-concurrency parallel agent execution
- Fixed rerun node SSE notification to frontend

---

## [1.1.2] - 2026-06-05

### Added
- Added `oxy_manage_tools` — system-level FunctionHub for runtime CRUD on the agent organization tree (list, get, create, delete, move, modify Oxy instances)
- Added fine-grained cache token tracking across 5 LLM providers
- Added support for `first_query` to accept `list[str]` with frontend querys panel

---

## [1.1.1] - 2026-05-16

### Added
- Added A2A (Agent-to-Agent) gateway/client architecture with interoperability demos
- Added trace graph visualization with timeline, node highlighting, and rerun capability
- Added continue-execute support for breakpoint restart
- Added Markdown rendering in chat messages
- Added skill recall support
- Added thumbnail preview for file attachments
- Added memory persistence to Elasticsearch
- Added background asyncio tasks management keyed by trace_id
- Added allow-origins CORS configuration
- Added resizable panel support in web UI

### Changed
- Optimized code structure and comments
- Modified chat API response format
- Stored original payload in trace table

### Fixed
- Fixed trace graph rendering issues
- Fixed local ES query bugs
- Fixed file upload API
- Fixed restart node output

---

## [1.0.13] - 2026-04-06

### Added
- Added token usage tracking and configuration support
- Added mount support for tools

### Fixed
- Fixed CWE-22 path traversal vulnerabilities in OxyBank
- Restricted file access permissions
- Fixed group_data override in MAS and added missing `replanner_agent_name`

### Changed
- Optimized prompt of SkillAgent

---

## [1.0.12] - 2026-03-08

### Added
- Added SkillAgent with integrated skill capabilities
- Added ShellUseAgent for shell-based operations
- Added trigger service for event-driven agent invocation

### Fixed
- Fixed trust mode of ReActAgent
- Fixed SSH tool issues
- Fixed OxyBank dependency issues
- Fixed unit test bugs

---

## [1.0.11] - 2026-01-23

### Added
- Added History management UI with search and filter support
- Added Prompt optimization functionality
- Added first response time metric in `shared_data`
- Added PlanAndSolveAgent — supports dynamic decision of "re-plan, continue, or abort", see [./examples/agents/demo_plan_and_solve_agent.py](./examples/agents/demo_plan_and_solve_agent.py)
- Added Agent discovery endpoint `/get_description` (SSEOxyGent auto-calls on init)
- Added OxyBank for standardized agent input
- Added message rating and conversation history features with UI
- Added version coordination across multiple MAS instances

### Changed
- Live prompt management disabled by default
- Enhanced `trust_mode` capabilities and removed redundant answer prefix
- Optimized prompts

---

## [1.0.10] - 2025-12-26

### Added
- Added Prompt management UI for online prompt editing
- Added LocalLLM class for local model support
- Added `oxy.BaseBank` for standardizing agent input
- Added SSEOxyGent agent and SSE utilities
- Added live prompt hot-reload system backed by Elasticsearch
- Added async trace API (`/async/chat` and `/async/trace`)
- Added SSE exponential backoff retry mechanism
- Added user feedback interface `/feedback` for human-in-the-loop, see [./examples/backend/demo_human_in_the_loop.py](./examples/backend/demo_human_in_the_loop.py)

### Changed
- Replaced `elasticsearch[async]` with `elasticsearch` package
- Modified attachment description format
- Enhanced code abstraction

---

## [1.0.9] - 2025-12-12

### Added
- Added `BaseLLM` parameter for custom multimodal base64 prefixes
- Added `func_process_message` method to MAS for unified message processing, see [./examples/backend/demo_process_message.py](./examples/backend/demo_process_message.py)
- Added `stream_end` message as streaming end indicator
- Stream messages now support batch storage
- Added pre-logging of payloads for easier troubleshooting
- Standardized SSE message fields: `id`, `event`, `data`
- SSEOxyGent now forwards headers transparently
- Added parameter to configure uvicorn workers
- Added K8s MCP server

### Changed
- Messages sent only in SSE mode by default
- Modified message table structure with new fields
- When storing in history table, memory `answer` field is force-converted to string

### Fixed
- `chat_with_agent` no longer sends messages when `send_msg_key` is empty
- Fixed stream mode of LLM

### Security
- Prevented RCE attacks by blocking dangerous classes in OxyFactory

---

## [1.0.8] - 2025-11-14

### Added
- Added streaming output capability to the frontend
- Added Agent name field to think messages
- Added document processing tool collection (PDF, Word, Excel)
- Added MCP `timeout` parameter support
- Added TTS demo using MCP tools

### Changed
- Changed LLM parameter `stream` default value to `True`
- Made LocalRedis asynchronous

### Fixed
- Removed duplicate code in base_oxy.py

---

## [1.0.7] - 2025-10-27

### Added
- Added fine-grained message storage, see [./examples/advanced/demo_save_message.py](./examples/advanced/demo_save_message.py)
- Added custom agent input schema example, see [./examples/advanced/demo_custom_agent_input_schema.py](./examples/advanced/demo_custom_agent_input_schema.py)
- Added multimodal information transfer between agents, see [./examples/advanced/demo_multimodal_transfer.py](./examples/advanced/demo_multimodal_transfer.py)
- Added MCP tool `functions` support
- Added MAS hook example
- Added Code Interpreter tools (later removed)
- Added `sql_tools` to preset tools
- Added middleware and interceptor support
- Added `delete_file` directory deletion support

### Changed
- Renamed Vearch config parameter `tool_df_space_name` to `tool_space_name`
- Modified environment variable names in `config.json`
- Automatically generate externally accessible Web links after uploading attachments
- Adjusted examples directory structure

### Fixed
- Fixed multiple agent interactions not correctly recorded in single conversation history
- Fixed upload directory not exists bug
- Fixed breakpoint restart logic
- Fixed required param without default value in function_tools

### Removed
- Removed support for `web_file_url_list` in `payload`

---

## [1.0.6] - 2025-09-21

### Added
- Added RAG Agent support
- Added async API endpoint
- Added image generation tool
- Added train tickets tool
- Added Baidu search tools
- Added tests for shell-tools and math_tools

### Changed
- Enhanced math_tool with generic computation capabilities
- Support adding custom routers

### Fixed
- Fixed message ES table issues
- Fixed bug of required param without default value in function_tools
- Dynamically import modules to avoid conflicts

---

## [1.0.5] - 2025-09-01

### Added
- Added `group_data` logic for data isolation
- Added trace_id attachment when logging
- Added get/set utility functions
- Saved shared_data in trace table
- Added dynamic headers support for MCP
- Added ES schema definitions
- Added Optional type support for tool parameters

### Changed
- Support settings when creating ES tables

---

## [1.0.4] - 2025-08-25

### Added
- Added Python and Shell preset tools
- Added SQL tools
- Added web API endpoints
- Added async function support for tools
- Added automatic MCP reconnection

### Changed
- Support short memory size per agent
- Support global max memory rounds
- Support full memory in arguments
- Support modifying Redis DB number
- MCP tools no longer require maintaining long connections

### Fixed
- Fixed input format issues
- Fixed unittest errors

---

## [1.0.3] - 2025-08-15

### Added
- Added global data support
- Added custom schema for OxyRequest
- Added file attachments support
- Added request_id tracking
- Added Streamable MCP tool support
- Added group_id support for multi-tenant isolation
- Added shared data schema configuration
- Added Gemini API support

### Changed
- Moved shared data into node
- Set default env file
- Support interceptor for all Oxy instances
- Updated MCP requirements version

### Fixed
- Fixed streaming output
- Fixed shared data handling
- Fixed dict parameter description
- Fixed callee not exist message
- Fixed plan_and_solve duplicated line
- Fixed the streaming output bug of the Deepseek model

---

## [1.0.2] - 2025-07-30

### Added
- Added support for appending prompts
- Added Reflexion agent rebuild
- Added Ollama support for HttpLLM
- Added user guide documentation (Simplified Chinese)
- Added browser operation tools demo

### Changed
- Auto-fill URL for HttpLLM

### Fixed
- Fixed local ES node query and list form
- Fixed shared data conversion
- Fixed team work copy in LocalAgent
- Fixed HTTP LLM dropping invalid payload keys
- Fixed aioredis Python 3.13 compatibility bug

---

## [1.0.1] - 2025-07-21

### Added
- Initial release of OxyGent multi-agent framework
- Core Oxy abstraction with unified execution lifecycle
- ReActAgent, ChatAgent, ParallelAgent, WorkflowAgent
- FunctionHub and FunctionTool system
- MCP tool integration (StdioMCPClient)
- HttpLLM and OpenAILLM support
- MAS runtime container with CLI and Web service
- Elasticsearch and Redis storage backends
- SSE streaming support
- Built-in preset tools (file, math, time, http, string, system, ssh)
- Web UI for chat interaction
