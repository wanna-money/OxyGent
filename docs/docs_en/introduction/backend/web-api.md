When you call `mas.start_web_service()`, OxyGent starts a FastAPI server that listens on `http://127.0.0.1:8080` by default. This service provides a built-in Web UI and a set of HTTP API endpoints that you can use to interact with the agent system.

> To change the port: `Config.set_server_port(8082)` or `await mas.start_web_service(port=8082)`

Below are all available API endpoints and data format descriptions.

# Status Code Definitions
```json
200: Success
400: Failure
500: Server Error
```

# Response Structure Definition
```json
{
    "code": 200,
    "message": "SUCCESS",
    "data": {}
}
```

# API Definitions
## Get Agent Architecture

```json
url = "/get_organization"
method = "GET"
params = {}
response = {
    "code": 200,
    "message": "SUCCESS",
    "data": {
        "id_dict": {"math_agent": 0, "time_agent": 1},
        "organization": {
            "name": "math_agent",
            "type": "agent",
            "children": [
                {
                    "name": "time_agent",
                    "type": "agent",
                    "children": [
                        {
                            "name": "get_current_time",
                            "type": "tool",
                            "path": ["math_agent", "time_agent", "get_current_time"],
                            "is_remote": true,
                        },
                        {
                            "name": "convert_time",
                            "type": "tool",
                            "path": ["math_agent", "time_agent", "convert_time"],
                            "is_remote": true,
                        },
                    ],
                    "path": ["math_agent", "time_agent"],
                },
                {"name": "power", "type": "tool", "path": ["math_agent", "power"]},
                {"name": "pi", "type": "tool", "path": ["math_agent", "pi"]},
            ],
            "path": ["math_agent"],
        },
    }
}
```

## Get Welcome Message

```json
url = "/get_welcome_message"
method = "GET"
params = {}
response = {
    "code": 200,
    "message": "SUCCESS",
    "data": {
        "first_query": "Hi, I'm OxyGent. How can I assist you?"
    }
}
```

## Get First Query

```json
url = "/get_first_query"
method = "GET"
params = {}
response = {
    "code": 200,
    "message": "SUCCESS",
    "data": {
        "first_query": "Please calculate the 20 positions of Pi"
    }
}
```

## Upload Attachment

```json
url = "/upload"
method = "POST"
datas = {
    file
}
response = {
    "code": 200,
    "message": "SUCCESS",
    "data": {
        "file_name": "123.jpg"
    }
}
```

## Ask a Question (SSE Connection)

```json
url = "/sse/chat"
method = "POST"
datas = {
    "query": "What time is it now",
    "from_trace_id": "from_trace_id"
}

// The frontend listens to the following four types of messages:
{
    "type": "tool_call",
    "content": {
        "node_id": "njU9muAZqAXtnTCR",
        "call_stack": ["user", "math_agent", "time_agent"],
        "caller": "math_agent",
        "caller_category": "agent",
        "callee": "time_agent",
        "callee_category": "agent",
        "arguments": {"query": "What time is it now"}
    }
}

{
    "type": "observation",
    "content": {
        "node_id": "njU9muAZqAXtnTCR",
        "current_trace_id": "R7nPP3b5MGVMLczk",
        "call_stack": ["user", "math_agent", "time_agent"],
        "caller": "math_agent",
        "caller_category": "agent",
        "callee": "time_agent",
        "callee_category": "agent",
        "output": "The current time is 14:37 Beijing Time."
    }
}

{
    "type": "think", 
    "content": "The user wants to know the current time. I should call the get_current_time function to get the current time."
}

{
    "type": "answer", 
    "content": "Rounded to 30 decimal places: 3.14159265358979323846264338328"
}
```

---

## Related Examples

- [Launch MAS Service Example](../../examples/backend/demo_launch_mas.md) -- Demonstrates how to start the web service
- [Add Custom Router Example](../../examples/backend/demo_add_router.md) -- Demonstrates how to add custom API routes to MAS
