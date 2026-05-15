# How to Enable Agent Reflexion?

## Using ReActAgent for Reflexion

`oxy.ReActAgent` supports passing a reflexion function. As long as the maximum reflexion count has not been reached, the Agent can redo based on the reflexion result until the required output is returned.

The reflexion function is very flexible in form. You can require specific answers for specific questions, or require filtering certain responses. If the reflexion result is not `None`, the Agent will redo based on the reflexion:

```python
def custom_reflexion(response: str, oxy_request: OxyRequest) -> str:
    """Custom reflexion function to evaluate response quality.
    
    Args:
        response (str): The agent's response to evaluate
        query (str): The original user query
        oxy_request: The current request context
        
    Returns:
        tuple[bool, str]: (is_acceptable, reflection_message)
    """
    # Basic checks from default implementation
    if not response or len(response.strip()) < 5:
        return "The response is too short or empty. Please provide a more detailed and helpful answer."
    
    # Custom business logic checks
    if "hello" in oxy_request.get_query().lower():
        # For greeting queries, expect friendly response
        if not any(word in response.lower() for word in ["hello", "hi", "hey", "greetings", "welcome"]):
            return "This is a greeting. Please respond in a more friendly and welcoming manner."
    
    if "math" in oxy_request.get_query().lower() or "calculate" in oxy_request.get_query().lower():
        # For math queries, expect numerical content
        if not any(char.isdigit() for char in response):
            return "This seems to be a math-related question but your answer doesn't contain any numbers. Please provide a numerical answer or calculation."
    
    if "explain" in oxy_request.get_query().lower():
        # For explanation requests, expect detailed responses
        if len(response.split()) < 20:
            return "The user asked for an explanation, but your response is too brief. Please provide a more detailed explanation."
    
    # Check for common unhelpful responses
    unhelpful_phrases = [
        "i don't know",
        "i can't help",
        "sorry, i cannot",
        "i'm not sure",
        "not possible"
    ]
    
    if any(phrase in response.lower() for phrase in unhelpful_phrases):
        return "Your response seems unhelpful. Please try to provide a more constructive answer or suggest alternative solutions."
    
    return None
```

Reflexion functions can be nested. If you want stricter reflexion for mathematical computations, such as requiring the Agent to output detailed steps, you can use the following approach:

```python
def math_reflexion(response: str, oxy_request: OxyRequest) -> str:
    """Specialized reflexion function for mathematical problems."""
    # First apply basic checks
    basic_msg = custom_reflexion(response, oxy_request)
    if basic_msg:
        return basic_msg
    
    # Math-specific checks
    if any(word in oxy_request.get_query().lower() for word in ["calculate", "compute", "solve", "math", "equation"]):
        # Expect step-by-step solution
        if "step" not in response.lower() and "=" not in response:
            return "For mathematical problems, please provide a step-by-step solution showing your work."
    
    return None
```

Reflexion needs to be specified for `oxy.ReActAgent` execution. It is worth noting that if you want the Master Agent to output reflexion-improved results, you need to add reflexion at each level.

```python
    oxy.ReActAgent(
        name="math_agent",
        desc="A specialized agent for mathematical problems with advanced reflexion",
        llm_model="default_llm",
        func_reflexion=math_reflexion, # key parameter
        max_react_rounds=30, # specify maximum redo count
        # ...
    ),
    # Master agent that coordinates others
    oxy.ReActAgent(
        name="master_agent",
        sub_agents=["basic_agent", "smart_agent", "math_agent"],
        is_master=True,
        llm_model="default_llm",
        func_reflexion=math_reflexion,
        # ...
    ),
```

## Using Flows for Reflexion

We provide [Flows](./preset-flows.md): `oxy.Reflexion` for general task reflexion, and `oxy.MathReflexion` for computation task reflexion or verification. You can invoke them as follows:

```python
    Reflexion(
        name="general_reflexion",
        worker_agent="worker_agent", # worker agent
        reflexion_agent="reflexion_agent", # reflexion agent
        evaluation_template="...", # reflexion template
        max_reflexion_rounds=3, # reflexion rounds
    ),
    
    MathReflexion(
        name="math_reflexion", 
        worker_agent="worker_agent", # worker agent
        reflexion_agent="reflexion_agent", # reflexion agent
        evaluation_template="...", # reflexion template
        max_reflexion_rounds=3, # reflexion rounds
    ),
```


## Using Workflows for Reflexion

In some cases, you may want to use an agent rather than a fixed method for reflexion. In this case, you can designate a `oxy.ChatAgent` or another type of Agent to perform reflexion:

```python
    # Reflexion Agent - responsible for evaluating answer quality
    oxy.ChatAgent(
        name="reflexion_agent",
        desc="Reflexion agent responsible for evaluating answer quality and providing improvement suggestions",
        llm_model="default_llm",
    ),
```

You can use a [workflow](./workflow.md) to manage the reflexion process. The following demonstrates the full reflexion flow using query updates:

```python
# Reflexion Workflow Core Logic
async def reflexion_workflow(oxy_request: OxyRequest):
    """
    Workflow implementing external reflexion process:
    1. Get user query
    2. Let worker_agent generate initial answer
    3. Let reflexion_agent evaluate answer quality
    4. If unsatisfactory, provide improvement suggestions and regenerate
    5. Return final satisfactory answer
    """
    
    # Step 1: Get the original query
    user_query = oxy_request.get_query(master_level=True)
    print(f"=== User Query ===\n{user_query}\n")
    
    max_iterations = 3
    current_iteration = 0
    
    while current_iteration < max_iterations:
        current_iteration += 1
        print(f"=== Reflexion Round {current_iteration} ===")
        
        # Step 2: Execute
        worker_resp = await oxy_request.call(
            callee="worker_agent",
            arguments={"query": user_query}
        )
        worker_answer = worker_resp.output
        print(f"Worker Answer:\n{worker_answer}\n")
        
        # Step 3: Input the content for reflexion
        evaluation_query = f"""
Please evaluate the quality of the following answer:

Original Question: {user_query}

Answer: {worker_answer}

Please return evaluation results in the following format:
Evaluation Result: [Satisfactory/Unsatisfactory]
Evaluation Reason: [Specific reason]
Improvement Suggestions: [If unsatisfactory, provide specific improvement suggestions]
"""
        
        reflexion_resp = await oxy_request.call(
            callee="reflexion_agent",
            arguments={"query": evaluation_query}
        )
        reflexion_result = reflexion_resp.output
        print(f"Reflexion Evaluation:\n{reflexion_result}\n")
        
        # Step 4: Get reflexion results
        if "Satisfactory" in reflexion_result and "Unsatisfactory" not in reflexion_result:
            print("=== Reflexion Complete, Answer Quality Satisfactory ===")
            return f"Final answer optimized through {current_iteration} rounds of reflexion:\n\n{worker_answer}"
        
        # Step 5: Update query with reflexion results
        improvement_suggestion = ""
        lines = reflexion_result.split('\n')
        for line in lines:
            if "Improvement Suggestions" in line:
                improvement_suggestion = line.split(":", 1)[-1].strip()
                break
        
        if improvement_suggestion:
            user_query = f"{oxy_request.get_query(master_level=True)}\n\nPlease note the following improvement suggestions: {improvement_suggestion}"
            print(f"Updated query with improvement suggestions:\n{user_query}\n")
    
    # If maximum redo count is exhausted, return the current best result
    print(f"=== Reached maximum iterations ({max_iterations}), returning current best answer ===")
    return f"Answer after {max_iterations} rounds of reflexion attempts:\n\n{worker_answer}"
```

Finally, you need to use `oxy.WorkflowAgent` to manage the reflexion process:

```python
    oxy.WorkflowAgent(
        name="general_reflexion_agent",
        desc="Workflow agent that optimizes answer quality through external reflexion",
        sub_agents=["worker_agent", "reflexion_agent"],
        func_workflow=reflexion_workflow,
        llm_model="default_llm",
    ),
```

[Previous: Handling LLM and Agent Output](./handle-output.md)
[Next: Creating Workflows](./workflow.md)
[Back to Home](../readme.md)

---

## Related Examples

- [ReActAgent Example](../../examples/agents/demo_react_agent.md) -- Demonstrates the basic usage of ReActAgent, including the reflexion feature
- [Reflexion Flow Example](../../examples/flows/reflexion_agent_demo.md) -- Demonstrates how to use the Reflexion flow for automatic reflexion and optimization
