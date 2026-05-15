# How to Debug?

OxyGent recommends using the visual interface for debugging. Below is a guide on debugging:

## Starting the Visual Service

You can start the visual service using `start_web_service`:

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query="How many chars in 'OxyGent'?")
```

If compilation is successful, the command line will display OxyGent's version and other system information; otherwise, an error will be shown.

```apache
   ____             ______           __ 
  / __ \_  ____  __/ ____/__  ____  / /_
 / / / / |/_/ / / / / __/ _ \/ __ \/ __/
/ /_/ />  </ /_/ / /_/ /  __/ / / / /_  
\____/_/|_|\__, /\____/\___/_/ /_/\__/  
          /____/                        
2025-07-20 20:36:03,613 - INFO ================================================================
2025-07-20 20:36:03,613 - INFO 🚀 OxyGent MAS Application Startup Information
2025-07-20 20:36:03,613 - INFO ================================================================
2025-07-20 20:36:03,613 - INFO App Name     : app
2025-07-20 20:36:03,613 - INFO Version      : 1.0.0
2025-07-20 20:36:03,613 - INFO Environment  : default
2025-07-20 20:36:03,613 - INFO Port         : 8080
2025-07-20 20:36:03,613 - INFO Python Ver   : 3.10.18
2025-07-20 20:36:03,613 - INFO Cache Dir    : ./cache_dir
2025-07-20 20:36:03,614 - INFO Start Time   : 2025-07-20 20:36:03
2025-07-20 20:36:03,614 - INFO ================================================================
2025-07-20 20:36:03,616 - INFO 🌐 OxyGent MAS Organization Structure Overview
2025-07-20 20:36:03,616 - INFO ================================================================
```

## Chatting with Agents
![](http://storage.jd.local/ai-gateway-routing/prod_data/oxygent_docs_images/1.png)

The main interface includes the following sections:
+ **MAS Structure**: Contains all registered agents and tools
+ **Chat Panel**: Contains all conversations between users and agents, as well as between agents
+ **Thinking Details**: Contains the internal LLM thinking process and output of agents
+ **File Tools**: Tools for saving and loading MAS

![](http://storage.jd.local/ai-gateway-routing/prod_data/oxygent_docs_images/2.png)

You can type your query directly in the chat panel, or add images or videos as attachments.

If you want to send a message directly to a specific agent, you can use `@`.

## Real-Time Monitoring

![](http://storage.jd.local/ai-gateway-routing/prod_data/oxygent_docs_images/3.png)

The currently active agent will be highlighted in the MAS structure diagram on the left side, and the agent's thinking process and output will be displayed in real time in the chat area.

![](http://storage.jd.local/ai-gateway-routing/prod_data/oxygent_docs_images/4.png)

The debug tools in the upper right corner allow you to trace back through the MAS execution process, including move to start `<<`, move to end `>>`, step backward `<`, step forward `>`, and auto replay `play`. You can use these tools to monitor the MAS execution step by step.

## Viewing Execution Details

![](http://storage.jd.local/ai-gateway-routing/prod_data/oxygent_docs_images/5.png)

Click on any thinking process to enter the agent detail page. This page displays the agent's LLM parameter configuration, the detailed conversation process, and metadata in `json` format. You can click on the structure diagram at the top of the page to switch between LLMs or tools to observe.

![](http://storage.jd.local/ai-gateway-routing/prod_data/oxygent_docs_images/6.png)

## Debugging the Execution Process

![](http://storage.jd.local/ai-gateway-routing/prod_data/oxygent_docs_images/7.png)

You can switch the upper view of the detail page by clicking `View 1 | View 2` to see MAS performance and the lifecycle of each invocation.

![](http://storage.jd.local/ai-gateway-routing/prod_data/oxygent_docs_images/8.png)

The detail page also provides step-by-step debugging tools. You can click `regenerate` to regenerate the output at any node.

[Previous: Generating Training Samples](../advanced/training.md)
[Back to Home](../readme.md)

---

## Related Examples

- [Launch MAS Service Example](../../examples/backend/demo_launch_mas.md) -- Demonstrates how to launch the visual web service for debugging
