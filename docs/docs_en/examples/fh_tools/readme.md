# FunctionHub Tools Examples

Examples demonstrating how to use `FunctionHub`-based custom Python tools with OxyGent agents.

---

## Examples

### Shortest Path Demo

**File:** `examples/fh_tools/shortest_path/shortest_path_demo.py`

This example demonstrates using a `FunctionHub` with Google OR-Tools to solve shortest-path problems between cities. The FunctionHub (imported from `function_hubs/shortest_path.py`) provides two tools: `info_update` reads city and distance data from an Excel file into memory using pandas, and `shortest_path` computes the shortest path between two cities using the OR-Tools `min_cost_flow` solver, then visualizes the result with matplotlib and networkx, saving the graph as a PNG image. The multi-agent system includes a `shortest_path_agent` for computing paths, an `excel_agent` for reading file information, and a master `ReActAgent` that coordinates the two. The demo starts a web service where users can upload Excel files with city/distance data and query for shortest paths.

**Key Components:**
- `HttpLLM` -- LLM backend configured from environment variables
- `FunctionHub` ("shortest_path_tools") -- custom Python tools for Excel data ingestion and shortest-path computation using OR-Tools
- `ReActAgent` ("shortest_path_agent") -- agent for computing shortest paths between cities
- `ReActAgent` ("excel_agent") -- agent for reading Excel file information
- `ReActAgent` ("master_agent") -- orchestrator coordinating the Excel and shortest-path agents
- `MAS` -- runtime container launching the web service

**[Detailed Guide →](./shortest_path/shortest_path_demo.md)**

---
