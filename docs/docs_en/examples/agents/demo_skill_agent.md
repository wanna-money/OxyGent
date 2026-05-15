# Skill Agent

**Source:** `examples/agents/demo_skill_agent.py`

## Overview

This example demonstrates the `SkillAgent`, which loads and executes pre-defined skill files from a local directory. Skills are modular, reusable task definitions that the agent can discover and invoke. Combined with file viewing and shell execution tools, the `SkillAgent` can read skill definitions and carry them out. This pattern is ideal for building extensible agents whose capabilities can be expanded by simply adding new skill files.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`
- A `./skills` directory with skill definition files (or a parent directory containing skill folders)

## How to Run

```bash
python -m examples.agents.demo_skill_agent
```

## Code Walkthrough

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars |
| `file_tools` | `preset_tools.file_tools` | Built-in file operation tools (provides `view_text_file` among others) |
| `shell_tools` | `preset_tools.shell_tools` | Built-in shell execution tools (provides `execute_shell_command` among others) |
| `skill_agent` | `SkillAgent` | `llm_model="default_llm"`; `tools=["view_text_file", "execute_shell_command"]`; `skills=["./skills"]` |

**Key parameters on `SkillAgent`:**
- `tools=["view_text_file", "execute_shell_command"]` -- the required base tools that enable the agent to read skill files and execute commands. These are specific tool names from the `file_tools` and `shell_tools` FunctionHub instances.
- `skills=["./skills"]` -- a list of paths pointing to skill directories. Each path can be a single skill folder or a parent directory containing multiple skill folders.

### Entry Point

```python
await mas.start_web_service(first_query="What skills do you have?")
```

Launches the web service with a meta-query asking the agent to list its available skills.

## Key Concepts

- **`SkillAgent`** -- a specialized agent that discovers and executes skill definitions from the filesystem. Skills are loaded from the paths specified in the `skills` parameter.
- **Skills directory** -- skill files are stored in `./skills` (or any specified path). Each skill typically defines a task with instructions, required tools, and execution steps.
- **Tool composition** -- the `SkillAgent` requires specific tool names (not tool group names) in its `tools` list. Here, `"view_text_file"` and `"execute_shell_command"` are individual tools extracted from `preset_tools.file_tools` and `preset_tools.shell_tools` respectively.
- **Extensibility** -- new capabilities can be added by creating new skill files in the skills directory, without modifying the agent code.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The initial query "What skills do you have?" is sent.
3. The `SkillAgent` scans the `./skills` directory, discovers available skill definitions, and lists them in its response.
4. Users can then ask the agent to execute specific skills by name or description.
5. The agent uses `view_text_file` to read skill definitions and `execute_shell_command` to carry out any shell-based steps within those skills.
