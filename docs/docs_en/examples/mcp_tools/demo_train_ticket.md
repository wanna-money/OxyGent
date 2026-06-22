# Train Ticket Query Demo

**Source:** `examples/mcp_tools/demo_train_ticket.py`

## Overview

This example demonstrates a train ticket inquiry agent that queries the China Railway 12306 API for real-time train schedules and ticket availability. The agent uses a custom `FunctionHub` tool set that wraps the 12306 API, allowing users to ask natural-language questions about train tickets between Chinese cities. The agent handles date resolution (e.g., "tomorrow"), station code lookup, and ticket data parsing automatically.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- OxyGent package installed (`pip install -r requirements.txt`)
- `requests` library (included in standard requirements)
- Network access to `https://kyfw.12306.cn` and `https://www.12306.cn` (the 12306 API)
- The `function_hubs/train_ticket_tools.py` module must be importable

## How to Run

```bash
python -m examples.mcp_tools.demo_train_ticket
```

The demo starts a web service with the initial query: "Please help me check train tickets from Xi'an to Beijing tomorrow" (in Chinese) and a bilingual welcome message.

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Role |
|---|---|---|
| `default_llm` | `HttpLLM` | Language model with temperature 0.01, semaphore 4 |
| `train_ticket_tools` | `FunctionHub` | Custom tool set wrapping the 12306 train ticket API |
| `train_ticket_agent` | `ReActAgent` | Agent that uses train ticket tools; `trust_mode=False` |

### FunctionHub Tools

The `train_ticket_tools` FunctionHub (defined in `function_hubs/train_ticket_tools.py`) provides three tools:

1. **`get_stations_of_city(city_names)`**: Looks up station codes for Chinese city names by parsing the 12306 station database. Accepts pipe-separated city names (e.g., `"Beijing|Xi'an"`).

2. **`get_tickets(train_date, from_station_code, to_station_code, purpose_codes)`**: Queries the 12306 API for available tickets on a given date between two station codes. Returns a list of `Ticket` objects with train number, departure/arrival times, duration, availability status, and seat availability/pricing for all classes (business, first, second, soft/hard sleeper, soft/hard seat, no seat).

3. **`get_current_date()`**: Returns the current date in Shanghai timezone (UTC+8) in `yyyy-MM-dd` format. Used for resolving relative dates like "tomorrow" or "next Monday".

### Agent Configuration

```python
oxy.ReActAgent(
    name="train_ticket_agent",
    tools=["train_ticket_tools"],
    trust_mode=False,
    llm_name="default_llm",
)
```

- **`trust_mode=False`**: The agent will validate and reason about tool calls rather than blindly executing them.
- The agent is not marked as `is_master=True`, which means it is the only agent and becomes the default entry point.

### Entry Point

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="...",
            welcome_message="...",
        )
```

The `welcome_message` provides usage examples in both Chinese and English.

## Key Concepts

- **FunctionHub**: A decorator-based system for wrapping Python functions as tools. Each function decorated with `@fh.tool()` becomes a callable tool with Pydantic-validated parameters. The `train_ticket_tools` module demonstrates a real-world FunctionHub with data models (`StationData`, `Ticket`).
- **External API Integration**: The tools make HTTP requests to the 12306 API, parse complex pipe-delimited response formats, and return structured Pydantic models. This shows how OxyGent agents can interact with real-world APIs.
- **Relative Date Resolution**: The agent is expected to call `get_current_date()` first when the user mentions relative dates, then compute the target date before querying tickets.
- **Station Code Lookup**: The agent must call `get_stations_of_city()` to resolve city names to station codes before querying tickets, as the 12306 API requires station codes.
- **`trust_mode=False`**: Instructs the agent to apply additional reasoning before executing tool calls, which is useful when tools interact with external APIs.

## Expected Behavior

1. The web UI opens with a bilingual welcome message and sample queries.
2. The user asks about train tickets (e.g., "train tickets from Xi'an to Beijing tomorrow").
3. The agent calls `get_current_date()` to resolve "tomorrow" to a concrete date.
4. The agent calls `get_stations_of_city("Xi'an|Beijing")` to get station codes.
5. The agent calls `get_tickets()` with the resolved date and station codes.
6. The 12306 API returns raw ticket data, which is parsed into structured `Ticket` objects.
7. The agent formats the results into a human-readable response showing available trains, times, duration, and seat availability.
