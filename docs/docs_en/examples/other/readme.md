# Other Examples

Miscellaneous examples that demonstrate additional OxyGent capabilities beyond standard agent and tool patterns.

---

## Examples

### Flow Chart Image Generation Demo

**File:** `examples/other/create_flow_image_demo.py`

This example builds an interactive Mermaid flowchart generation and viewing application using OxyGent. It sets up a multi-agent system with two specialized sub-agents: an `image_gen_agent` equipped with `flow_image_gen_tools` for generating Mermaid flowcharts from text descriptions and rendering them as HTML, and an `open_chart_agent` equipped with `open_chart_tools` for opening existing flowchart HTML files in a browser. The master `ReActAgent` uses a detailed Chinese-language prompt to perform intent recognition, deciding whether to generate a new flowchart, open an existing one, or provide editing guidance. The demo also creates a custom FastAPI application with CORS middleware, a flowchart API router, and static file serving, running the OxyGent web service on port 8081. The default task generates a software development lifecycle flowchart covering requirements analysis, design, coding, testing, and deployment.

**Key Components:**
- `HttpLLM` -- LLM backend configured via OpenAI-compatible environment variables
- `FunctionHub` ("flow_image_gen_tools") -- tools for generating Mermaid flowcharts as interactive HTML
- `FunctionHub` ("open_chart_tools") -- tools for opening existing flowchart HTML files in a browser
- `ReActAgent` ("image_gen_agent") -- sub-agent specialized in flowchart generation
- `ReActAgent` ("open_chart_agent") -- sub-agent specialized in opening and displaying flowcharts
- `ReActAgent` ("master_agent") -- orchestrator with intent recognition for routing chart-related tasks
- `FastAPI` -- custom web application with CORS, API routes, and static file serving
- `MAS` -- runtime container launching the web service on a custom port

**[Detailed Guide →](./create_flow_image_demo.md)**

---
