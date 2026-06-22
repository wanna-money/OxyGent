# How to Run Agents in a Distributed Manner?

OxyGent MAS supports straightforward distributed invocation. You can use `oxy.SSEOxyGent` to connect to remotely running agents, which can operate in the same way as local agents.

Starting from the example in [How to Customize Prompt Processing?](../advanced/process-input.md), we can create a distributed time-querying agent:

```python
# app_time_agent.py
from oxygent import MAS, Config, oxy
import os

Config.set_app_name("app-time")
Config.set_server_port(8082) # Replace with actual port

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.01},
        semaphore=4,
    ),
    oxy.StdioMCPClient(
        name="time_tools",
        params={
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
        },
    ),
    oxy.ReActAgent(
        name="time_agent",
        desc="A tool for time query",
        is_master=True,
        tools=["time_tools"],
        llm_model="default_llm",
        timeout=10,
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="What time is it now?")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```

Then you can use `oxy.SSEOxyGent` to replace the original time_agent:

```python
oxy.SSEOxyGent(
    name="time_agent",
    desc="Remote time query agent",
    server_url="http://127.0.0.1:8082", # Replace with the actual location of app_time_agent.py
),
```

If you are using localhost, you can use the following simple script to start the distributed services:

```bash
#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

cleanup() {
    log "Cleaning up processes..."
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    log "Cleanup complete"
}

trap cleanup EXIT INT TERM

start_service() {
    local cmd=$1
    local name=$2
    local wait_time=${3:-5}
    
    log "Starting $name..."
    $cmd &
    local pid=$!
    
    sleep $wait_time
    
    # Check if the process is still running
    if kill -0 $pid 2>/dev/null; then
        log "$name started successfully (PID: $pid)"
        return 0
    else
        error "$name failed to start"
        return 1
    fi
}

main() {
    log "Starting distributed services..."

    start_service "python -m app_time_agent" "TimeAgent" 5
    start_service "python -m your_master_agent" "MasterAgent" 5

    log "All services have been started"
    log "Press Ctrl+C to stop all services"

    wait
}

main "$@"
```

## Complete Runnable Example

Below is a complete runnable code example (launching requires the bash script above):
```python
import asyncio

from oxygent import MAS, oxy, Config, OxyRequest
import os
from oxygent import preset_tools

Config.set_agent_llm_model("default_llm")

def update_query(oxy_request: OxyRequest):
    user_query = oxy_request.get_query(master_level=True)
    current_query = oxy_request.get_query()
    oxy_request.set_query(
        f"user query is {user_query}\ncurrent query is {current_query}"
    )
    return oxy_request

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.01},
        semaphore=4,
        timeout=240,
    ),
    oxy.StdioMCPClient(
        name="time_tools",
        params={
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
        },
    ),
    preset_tools.file_tools,
    oxy.ReActAgent(
        name="file_agent",
        desc="A tool that can operate the file system",
        tools=["file_tools"],
        func_process_input=update_query,
    ),
    oxy.SSEOxyGent(
        name="time_agent",
        desc="Remote time query agent",
        server_url="http://127.0.0.1:8082",
    ),
    oxy.ChatAgent(
        name="text_summarizer",
        desc="A tool that can summarize markdown text",
        prompt="You are a text summarizer. Please provide a concise summary of the given text.",
        func_process_input=update_query,
    ),
    oxy.ChatAgent(
        name="data_analyser",
        desc="A tool that can summarize echart data",
        prompt="You are a data analyst. Please analyze the given data and provide insights.",
        func_process_input=update_query,
    ),
    oxy.ChatAgent(
        name="document_checker",
        desc="A tool that can find problems in document",
        prompt="You are a document checker. Please review the document and identify any issues.",
        func_process_input=update_query,
    ),
    oxy.ParallelAgent(
        name="analyzer",
        desc="A tool that analyze markdown document",
        permitted_tool_name_list=["text_summarizer", "data_analyser", "document_checker"],
        func_process_input=update_query,
    ),
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        sub_agents=["file_agent", "time_agent", "analyzer"],
    ),
]


async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello!"
        )


if __name__ == "__main__":
    asyncio.run(main())
```

[Previous: Running Agents in Parallel](./parallel.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Distributed Master Agent Example](../../examples/distributed/app_master_agent.md) -- Demonstrates master agent configuration in a distributed system
- [Distributed Time Agent Example](../../examples/distributed/app_time_agent.md) -- Demonstrates deployment of a remote time query agent
- [Distributed Math Agent Example](../../examples/distributed/app_math_agent.md) -- Demonstrates deployment of a remote math computation agent
