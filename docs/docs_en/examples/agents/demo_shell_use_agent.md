# Shell Use Agent (Remote SSH)

**Source:** `examples/agents/demo_shell_use_agent.py`

## Overview

This example demonstrates the `ShellUseAgent`, which connects to a remote machine via SSH and executes shell commands autonomously. It uses a specialized system prompt (`SYSTEM_PROMPT_SHELL_USE`) and OxyGent's built-in `preset_tools.ssh_tools` to perform tasks on a remote server, such as cloning a Git repository and running a Python script. This pattern is ideal for DevOps automation, server management, and any scenario requiring remote command execution guided by LLM reasoning.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`
- A reachable SSH server at the specified hostname/port with valid credentials
- The remote server should have Git and Python installed (for the demo task)

## How to Run

```bash
python -m examples.agents.demo_shell_use_agent
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars |
| `ssh_tools` | `preset_tools.ssh_tools` | Built-in SSH tool FunctionHub for executing remote commands |
| `shell_use_agent` | `ShellUseAgent` | `auth_info` (SSH credentials); `prompt=SYSTEM_PROMPT_SHELL_USE`; `tools=["ssh_tools"]`; `max_react_rounds=64`; `is_discard_react_memory=False` |

**`auth_info`** contains the SSH connection details:

```python
auth_info={
    "hostname": "127.0.0.1",
    "port": 22,
    "username": "root",
    "password": "admin",
}
```

**Key agent parameters:**
- `prompt=SYSTEM_PROMPT_SHELL_USE` -- a specialized system prompt imported from `oxygent.prompts` that instructs the agent on how to interact with shell environments effectively.
- `max_react_rounds=64` -- allows up to 64 ReAct reasoning/action cycles, accommodating complex multi-step shell tasks.
- `is_discard_react_memory=False` -- retains all ReAct reasoning history across rounds, allowing the agent to reference earlier commands and outputs.

### Entry Point

```python
await mas.start_web_service(
    first_query="Please run the demo.py from https://github.com/jd-opensource/OxyGent.git"
)
```

Launches the web service with a task that requires cloning a repository and running a script.

## Key Concepts

- **`ShellUseAgent`** -- a specialized agent designed for remote shell interaction. It wraps SSH connectivity with LLM-driven reasoning to execute commands autonomously.
- **`auth_info`** -- SSH connection credentials passed directly to the agent. Supports `hostname`, `port`, `username`, and `password`.
- **`SYSTEM_PROMPT_SHELL_USE`** -- a built-in prompt from `oxygent.prompts` tailored for shell interaction scenarios, providing the agent with guidelines on command execution, error handling, and task completion.
- **`max_react_rounds`** -- the maximum number of ReAct cycles the agent can perform. Shell tasks often require many steps (clone, install dependencies, run, debug errors), so a high limit is appropriate.
- **`is_discard_react_memory`** -- when `False`, the agent retains the full history of its reasoning and command outputs, which is critical for shell tasks where later commands depend on earlier results.
- **`preset_tools.ssh_tools`** -- built-in tools for executing commands over SSH, handling output capture, and managing the remote session.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The query instructs the agent to run `demo.py` from the OxyGent GitHub repository.
3. The agent reasons through the steps and executes SSH commands:
   - Clones the Git repository on the remote server.
   - Navigates to the project directory.
   - Installs any required dependencies.
   - Runs `demo.py`.
4. Each command's output is observed, and the agent adapts its next action based on results or errors.
5. The final response summarizes the execution results.

**Note:** The default `auth_info` uses `127.0.0.1` with `root/admin` credentials. You must update these to match your actual SSH server configuration before running.
