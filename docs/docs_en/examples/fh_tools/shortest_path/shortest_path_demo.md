# Shortest Path Agent with FunctionHub Tools

**Source:** `examples/fh_tools/shortest_path/shortest_path_demo.py`

## Overview

This example demonstrates how to build a multi-agent system that computes shortest paths between cities. It uses a custom `FunctionHub` tool backed by Google OR-Tools for graph optimization and matplotlib/networkx for visualization. A master agent coordinates an Excel-reading agent and a shortest-path-computing agent.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Extra Python packages:
  - `ortools` -- Google OR-Tools for min-cost flow / shortest path computation
  - `matplotlib` -- For path visualization
  - `networkx` -- For graph construction and drawing
  - `pandas` -- For reading Excel files
  - `openpyxl` -- Excel engine for pandas (implied by `.read_excel`)

## How to Run

```bash
python -m examples.fh_tools.shortest_path.shortest_path_demo
```

## Code Walkthrough

### Configuration

```python
Config.set_agent_llm_model("default_llm")
```

Sets the global default LLM model.

### FunctionHub Tools (`shortest_path_tools`)

The tool definitions live in `function_hubs/shortest_path.py` and are imported as `shortest_path_tools`. This `FunctionHub` provides two tools:

#### `info_update(file_path, sheet_name=0)`

Reads city and distance data from an Excel file into a module-level `column_data` dictionary. The Excel file is expected to contain columns named `cities`, `start_cities`, `end_cities`, and `distances`. Returns `"File Read Success!"` or `"File is Empty"`.

#### `shortest_path(start_city, end_city)`

Computes the shortest path between two cities using OR-Tools' `SimpleMinCostFlow` solver:

1. Builds a directed graph from the loaded city/distance data.
2. Adds bidirectional arcs for each connection (since roads are bidirectional).
3. Sets supply/demand at the start and end nodes.
4. Solves the min-cost flow problem (equivalent to shortest path for unit capacity).
5. Returns a result dictionary with `status`, `distance`, `solve_time`, `path`, and `path_cities`.
6. Calls `visualize_city_path()` to generate a PNG image (`city_shortest_path.png`) showing the graph with the shortest path highlighted in red.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | Credentials from env vars |
| `shortest_path_tools` | `FunctionHub` | Imported from `function_hubs/shortest_path` |
| `shortest_path_agent` | `ReActAgent` | `tools=["shortest_path_tools"]`, `timeout=30`, `retries=3`, `delay=1`, `semaphore=2` |
| `excel_agent` | `ReActAgent` | `desc="...read file information based on the Excel file path"`, `tools=["shortest_path_tools"]` |
| `master_agent` | `ReActAgent` | `is_master=True`, `sub_agents=["excel_agent", "shortest_path_agent"]` |

### Agent Architecture

The system uses a two-step workflow:

1. **`excel_agent`** -- Reads the Excel file containing city and distance information using `info_update`.
2. **`shortest_path_agent`** -- Computes the shortest path between two specified cities using `shortest_path`.

The **`master_agent`** coordinates both, first delegating to the Excel agent to load data, then to the shortest path agent for computation.

### Entry Point

```python
await mas.start_web_service(first_query="")
```

Starts the web service with an empty initial query, leaving the user to provide the Excel file path and query interactively.

## Key Concepts

- **FunctionHub** -- A tool container that wraps Python functions as callable tools for agents. Tools are registered via the `@fh.tool()` decorator with a description string.
- **Google OR-Tools** -- An open-source optimization library. Here it solves the shortest path as a min-cost flow problem with unit capacity.
- **Agent Factory Function** -- `create_optimal_agent()` demonstrates creating an agent programmatically with fine-grained control over parameters like `timeout`, `retries`, `delay`, and `semaphore`.
- **`semaphore`** -- Limits concurrent executions of the agent to the specified number (2 in this case), preventing resource exhaustion.
- **`retries` / `delay`** -- The agent will retry up to 3 times with a 1-second delay between attempts if execution fails.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The user provides a query referencing an Excel file with city data (columns: `cities`, `start_cities`, `end_cities`, `distances`).
3. The master agent delegates to `excel_agent` to read the Excel file via `info_update`.
4. The master agent then delegates to `shortest_path_agent` to compute the shortest path between two cities via `shortest_path`.
5. The solver returns the optimal path, total distance, and computation time.
6. A visualization is saved as `city_shortest_path.png` showing all cities as nodes, all connections as edges, and the shortest path highlighted in red.
