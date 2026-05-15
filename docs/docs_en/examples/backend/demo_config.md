# Loading Configuration from a JSON File

**Source:** `examples/backend/demo_config.py`

## Overview

This example demonstrates how to load OxyGent configuration from a JSON file using `Config.load_from_json()`. The configuration system supports environment-based profile layering -- a `"default"` profile is merged with an environment-specific overlay (e.g., `"dev"`, `"prod"`). This pattern is essential for managing different configurations across development, staging, and production environments without changing code.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- A `config.json` file in the working directory (with at least a `"default"` profile)

## How to Run

```bash
python -m examples.backend.demo_config
```

## Code Walkthrough

### Configuration

```python
Config.load_from_json("./config.json", env="default")
Config.set_agent_llm_model("default_llm")
```

- `Config.load_from_json("./config.json", env="default")`: Loads configuration from the specified JSON file. The `env` parameter selects which profile to use. The system merges the `"default"` profile with the specified environment profile. At deploy time, you can set the `APP_ENV` environment variable to switch profiles automatically.
- `Config.set_agent_llm_model("default_llm")`: Sets the default LLM model name for all agents, so individual agents do not need to specify `llm_model`.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | Standard LLM credentials from environment |
| `master_agent` | `ReActAgent` | No explicit `llm_model` -- uses the globally configured default |

Note that `master_agent` does not specify `llm_model` because it was set globally via `Config.set_agent_llm_model()`.

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="hello")
```

## Key Concepts

- **Config.load_from_json()**: Loads configuration from a JSON file with environment-based profile layering. The JSON file should have a `"default"` key and optional environment keys (e.g., `"dev"`, `"prod"`).
- **Environment profiles**: The configuration system merges `"default"` settings with the selected environment's settings. Values in the environment profile override those in `"default"`.
- **APP_ENV**: An environment variable that, when set, automatically selects the configuration profile to use.
- **${VAR} substitution**: The config system supports environment variable substitution within config values using `${VAR_NAME}` syntax.
- **Config.set_agent_llm_model()**: A convenience method to set the default LLM model name for all agents globally.

## Expected Behavior

1. The configuration is loaded from `./config.json` with the `"default"` profile.
2. The default LLM model is set globally to `"default_llm"`.
3. The `ReActAgent` is created without an explicit `llm_model` and uses the global default.
4. The web service starts and processes the initial query `"hello"` using the configured LLM.
