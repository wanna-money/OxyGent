# What is ReAct?

**ReAct** (Reasoning + Acting) is a paradigm for building autonomous agents that interleave reasoning with action. Instead of generating an answer in a single pass, a ReAct agent follows an iterative loop:

```
Think  ->  Act  ->  Observe  ->  Repeat
```

1. **Think**: The LLM reasons about the current state and decides what to do next.
2. **Act**: The agent calls a tool or sub-agent based on its reasoning.
3. **Observe**: The agent receives the result of the action.
4. **Repeat**: The agent feeds the observation back into its reasoning and decides whether to take another action or produce a final answer.

This loop continues until the agent has enough information to answer, or until a maximum number of rounds is reached.

---

## Why ReAct?

A plain LLM generates text in a single forward pass. It cannot look up real-time data, perform calculations, or interact with external systems. ReAct solves this by giving the LLM the ability to take actions and learn from the results.

Compared to chain-of-thought prompting (reasoning only) or blind tool calling (acting only), ReAct combines both -- the agent explains its reasoning before each action, making its behavior more transparent and debuggable.

---

## How OxyGent Implements ReAct

OxyGent's `ReActAgent` implements the full ReAct loop:

```python
oxy.ReActAgent(
    name="agent",
    llm_model="default_llm",
    tools=["calculator", "search"],
    max_react_rounds=16,           # Max iterations before stopping
)
```

At each round, `ReActAgent`:
1. Sends the conversation history (including previous observations) to the LLM.
2. Parses the LLM's response for tool calls.
3. Executes the requested tools and collects observations.
4. Appends the observations to the conversation and loops back to step 1.
5. When the LLM produces a final answer (no tool call), the loop ends.

The agent automatically manages memory across rounds. Detailed ReAct memory (tool calls and observations) can be discarded after the loop to keep the conversation history concise for future turns.

---

## Further Reading

- [Agent Types](../agents/agent-types.md) -- Comparison of all agent types
- [ReActAgent API Reference](../../api/agent/react_agent.md) -- Full parameter reference
- [Register a Local Tool](../tools/register-tool.md) -- Add tools for the agent to use
- [Quickstart](../getting-started/quickstart.md) -- Build a ReActAgent in 5 minutes

---

[Back to Concepts](.)
[Back to Home](../readme.md)
