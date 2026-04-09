"""A2A agent card helpers for OxyGent MAS."""

from __future__ import annotations

from typing import Any


def card_identity(mas: Any) -> tuple[str, str]:
    """Resolve card ``name`` and ``description`` from MAS master agent."""
    if not mas:
        return "master_agent", "A2A facade of OxyGent MAS"

    master_name = getattr(mas, "master_agent_name", "") or "master_agent"
    master_oxy = mas.oxy_name_to_oxy.get(master_name)
    if master_oxy:
        name = getattr(master_oxy, "name", "") or master_name
        desc = getattr(master_oxy, "desc", "") or name
        return name, desc
    return master_name, f"{master_name} via A2A"


def effective_target(mas: Any, target_agent_name: str | None = None) -> str:
    """Resolve the target MAS agent used to process incoming A2A requests."""
    if mas and mas.master_agent_name:
        return mas.master_agent_name
    if target_agent_name:
        return target_agent_name
    if mas:
        for oxy_name in mas.oxy_name_to_oxy.keys():
            if mas.is_agent(oxy_name):
                return oxy_name
    return "master_agent"


def build_skills_from_org(
    *, mas: Any, skills_override: list[dict[str, Any]] | None = None
) -> list[dict[str, Any]]:
    """Build card skills from MAS organization tree or static override."""
    if skills_override:
        return skills_override

    card_name, card_desc = card_identity(mas)
    if not mas:
        return [
            {
                "id": f"{card_name}.chat",
                "name": card_name,
                "description": card_desc,
                "tags": ["chat", "oxygent", "a2a"],
                "inputModes": ["text/plain"],
                "outputModes": ["text/plain"],
            }
        ]

    org = mas.agent_organization or {}
    skills: list[dict[str, Any]] = []

    def walk(node: dict[str, Any], path: list[str] | None = None):
        if not isinstance(node, dict):
            return
        curr_path = (path or []) + [node.get("name", "")]
        node_type = node.get("type", "")
        node_name = node.get("name", "")
        if node_type in ("agent", "flow") and node_name:
            desc = ""
            oxy = mas.oxy_name_to_oxy.get(node_name)
            if oxy:
                desc = getattr(oxy, "desc", "") or node_name
            skills.append(
                {
                    "id": ".".join([p for p in curr_path if p]),
                    "name": node_name,
                    "description": desc,
                    "tags": ["oxygent", "a2a", node_type],
                    "inputModes": ["text/plain"],
                    "outputModes": ["text/plain"],
                }
            )
        for child in node.get("children", []) or []:
            walk(child, curr_path)

    walk(org)
    if skills:
        return skills

    return [
        {
            "id": f"{card_name}.chat",
            "name": card_name,
            "description": card_desc,
            "tags": ["chat", "oxygent", "a2a"],
            "inputModes": ["text/plain"],
            "outputModes": ["text/plain"],
        }
    ]


def build_agent_card(
    *,
    request_base_url: str,
    a2a_base_path: str,
    agent_version: str,
    capabilities: dict[str, Any],
    mas: Any,
    skills_override: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build an A2A-compatible agent card response."""
    endpoint = request_base_url.rstrip("/") + a2a_base_path
    skills = build_skills_from_org(mas=mas, skills_override=skills_override)
    card_name, card_desc = card_identity(mas)
    return {
        "name": card_name,
        "description": card_desc,
        "version": agent_version,
        "url": endpoint,
        "capabilities": capabilities,
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "skills": skills,
    }
