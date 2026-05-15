"""Demo: ParallelAgent that dispatches a query to multiple expert agents concurrently."""

import asyncio
import os

from oxygent import MAS, Config, oxy

Config.set_agent_llm_model("default_llm")

oxy_space = [
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
    ),
    oxy.ChatAgent(
        name="tech_expert",
        prompt="You are a senior technical architect. Evaluate tech stack, architecture, challenges, and resource needs. Output a feasibility score (1-10) with key recommendations.",
    ),
    oxy.ChatAgent(
        name="business_expert",
        prompt="You are a business analyst. Evaluate market opportunity, business model, ROI, and go-to-market strategy. Output a feasibility score (1-10) with key recommendations.",
    ),
    oxy.ChatAgent(
        name="risk_expert",
        prompt="You are a risk management expert. Only analyze risks: technical, market, operational, and compliance. Rate each risk (probability/impact/level) and propose mitigations.",
    ),
    oxy.ChatAgent(
        name="legal_expert",
        prompt="You are a legal expert for AI products. Only analyze legal aspects: data compliance, AI governance, IP protection, and contracts. Provide compliance advice and a legal risk checklist.",
    ),
    oxy.ParallelAgent(
        name="expert_panel",
        permitted_tool_name_list=[
            "tech_expert",
            "business_expert",
            "risk_expert",
            "legal_expert",
        ],
        is_master=True,
    ),
]


async def main():
    query = (
        "We are a mid-sized e-commerce company (50 support staff, 5000+ daily inquiries). "
        "We want to build an AI customer service system that auto-handles 80%+ common questions, "
        "provides 24/7 support, cuts labor costs by 30%, and achieves 90%+ satisfaction. "
        "Budget: 2M RMB, timeline: 6-month MVP, team: 10 devs (2 AI engineers), "
        "data: 500K historical records. Requirements: text+voice, CRM integration, "
        "multi-turn dialogue, human handoff, 99.9% availability. "
        "Please evaluate whether we should proceed."
    )
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(first_query=query)


if __name__ == "__main__":
    asyncio.run(main())
