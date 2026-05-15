# Live Prompts Examples

These examples demonstrate OxyGent's live prompt system, which enables hot-reloadable prompts that can be updated at runtime without restarting the application.

---

## Examples

### Live Prompt with Multi-Agent System

**File:** `examples/live_prompts/demo.py`

Demonstrates the live prompt system in a multi-agent hierarchy with four agents. Three specialized sub-agents (`time_agent`, `file_agent`, `math_agent`) are coordinated by a master ReActAgent. Each agent showcases a different prompt strategy: `time_agent` has `use_live_prompt=False` with a code-defined prompt, meaning it always uses the static prompt from the code; `file_agent` also has `use_live_prompt=False`, using only its code-level prompt parameter; `math_agent` leaves `use_live_prompt` at its default (enabled), so its prompt can be dynamically updated via the live prompt system at runtime; and `master_agent` similarly uses live prompts. The global LLM model is configured via `Config.set_agent_llm_model()`. This example illustrates how to mix static and dynamic prompt strategies within the same multi-agent system.

**Key Components:**
- `HttpLLM` -- language model backend
- `Config.set_agent_llm_model` -- global LLM configuration
- `preset_tools` -- time_tools, file_tools, math_tools for the sub-agents
- `ReActAgent` (x4) -- master agent and three sub-agents with varying `use_live_prompt` settings

**[Detailed Guide →](./demo.md)**

---

### Live Prompt Key Sharing

**File:** `examples/live_prompts/demo_live_prompt.py`

Demonstrates how multiple agents can share the same live prompt through the `prompt_key` parameter. Three ChatAgents are defined: `chat_agent1` and `chat_agent2` both set `prompt_key="my_prompt"`, meaning they will look up the same live prompt entry in the prompt store and share identical dynamically-managed prompts. `chat_agent3` sets `use_live_prompt=False`, opting out of the live prompt system entirely and using only its static code-level prompt. This example shows how `prompt_key` enables centralized prompt management -- updating the `my_prompt` entry in the live prompt store will simultaneously update the prompt for all agents that reference it.

**Key Components:**
- `HttpLLM` -- language model backend
- `ChatAgent` (x3) -- three agents demonstrating prompt_key sharing and use_live_prompt toggling
- `prompt_key` -- shared key for centralized live prompt lookup
- `use_live_prompt` -- flag to opt in or out of the live prompt system

**[Detailed Guide →](./demo_live_prompt.md)**
