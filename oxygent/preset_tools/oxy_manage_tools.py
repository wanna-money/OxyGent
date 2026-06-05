"""Runtime CRUD operations for the OxyGent agent organization tree.

Provides system-level management tools that allow the master agent to
create, delete, move, and modify Oxy instances (agents, tools, LLMs)
through conversational commands at runtime.
"""

import json
import logging

from pydantic import Field

from oxygent.oxy import FunctionHub
from oxygent.schemas import OxyRequest

logger = logging.getLogger(__name__)

oxy_manage_tools = FunctionHub(name="oxy_manage_tools")

AGENT_TYPE_MAP = {}


def _get_agent_type_map() -> dict:
    """Lazy-load agent type map to avoid circular imports."""
    if not AGENT_TYPE_MAP:
        from oxygent.oxy import (
            ChatAgent,
            PlanAndSolveAgent,
            RAGAgent,
            ReActAgent,
            ShellUseAgent,
            SkillAgent,
            WorkflowAgent,
        )

        AGENT_TYPE_MAP.update(
            {
                "ReActAgent": ReActAgent,
                "ChatAgent": ChatAgent,
                "WorkflowAgent": WorkflowAgent,
                "PlanAndSolveAgent": PlanAndSolveAgent,
                "ShellUseAgent": ShellUseAgent,
                "SkillAgent": SkillAgent,
                "RAGAgent": RAGAgent,
            }
        )
    return AGENT_TYPE_MAP


def _ok(message: str, data: dict = None) -> str:
    return json.dumps(
        {"success": True, "message": message, "data": data or {}}, ensure_ascii=False
    )


def _err(message: str) -> str:
    return json.dumps({"success": False, "message": message}, ensure_ascii=False)


def _is_local_agent(oxy) -> bool:
    from oxygent.oxy.agents.local_agent import LocalAgent

    return isinstance(oxy, LocalAgent)


async def _notify_org_updated(oxy_request: OxyRequest) -> None:
    await oxy_request.send_message({"type": "organization_updated"})


@oxy_manage_tools.tool(
    description="List all registered Oxy instances with their types, categories, and relationships. Use category_filter to filter by 'agent', 'tool', or 'llm'."
)
async def list_oxys(
    category_filter: str = Field(
        default="",
        description="Filter by category: 'agent', 'tool', 'llm', or empty for all",
    ),
    oxy_request: OxyRequest = None,
) -> str:
    mas = oxy_request.mas
    results = []

    for name, oxy in mas.oxy_name_to_oxy.items():
        category = oxy.category
        if category_filter and category != category_filter:
            continue

        info = {
            "name": name,
            "category": category,
            "class_name": oxy.class_name,
            "desc": oxy.desc[:100] if oxy.desc else "",
        }

        if _is_local_agent(oxy):
            info["sub_agents"] = oxy.sub_agents
            info["tools"] = oxy.tools
            info["is_master"] = getattr(oxy, "is_master", False)

        results.append(info)

    return _ok(f"Found {len(results)} oxy instances", {"oxys": results})


@oxy_manage_tools.tool(
    description="Get detailed information about a specific registered Oxy instance including all its configuration fields"
)
async def get_oxy_info(
    oxy_name: str = Field(description="The name of the Oxy instance to inspect"),
    oxy_request: OxyRequest = None,
) -> str:
    mas = oxy_request.mas
    if oxy_name not in mas.oxy_name_to_oxy:
        return _err(f"Oxy '{oxy_name}' not found")

    oxy = mas.oxy_name_to_oxy[oxy_name]
    info = {
        "name": oxy.name,
        "desc": oxy.desc,
        "category": oxy.category,
        "class_name": oxy.class_name,
        "permitted_tool_name_list": oxy.permitted_tool_name_list,
    }

    if _is_local_agent(oxy):
        info.update(
            {
                "llm_model": oxy.llm_model,
                "prompt": oxy.prompt[:500] if oxy.prompt else "",
                "sub_agents": oxy.sub_agents,
                "tools": oxy.tools,
                "banks": oxy.banks,
                "is_master": getattr(oxy, "is_master", False),
                "short_memory_size": oxy.short_memory_size,
                "team_size": oxy.team_size,
            }
        )

    return _ok(f"Info for '{oxy_name}'", info)


@oxy_manage_tools.tool(
    description="Create and register a new agent in the MAS at runtime. Supported types: ReActAgent, ChatAgent, WorkflowAgent, PlanAndSolveAgent, ShellUseAgent, SkillAgent, RAGAgent"
)
async def create_agent(
    agent_name: str = Field(description="Unique name for the new agent"),
    agent_type: str = Field(
        default="ReActAgent",
        description="Agent type: ReActAgent, ChatAgent, WorkflowAgent, PlanAndSolveAgent, ShellUseAgent, SkillAgent, RAGAgent",
    ),
    desc: str = Field(default="", description="Description of the agent's functionality"),
    llm_model: str = Field(
        default="", description="Name of the LLM to use (must be already registered)"
    ),
    prompt: str = Field(default="", description="System prompt for the agent"),
    sub_agents: str = Field(
        default="",
        description="Comma-separated names of sub-agents this agent can delegate to",
    ),
    tools: str = Field(
        default="",
        description="Comma-separated names of tools available to this agent",
    ),
    parent_agent: str = Field(
        default="",
        description="Name of the parent agent to attach this agent to as a sub-agent",
    ),
    oxy_request: OxyRequest = None,
) -> str:
    mas = oxy_request.mas
    type_map = _get_agent_type_map()

    if agent_type not in type_map:
        return _err(
            f"Unknown agent type '{agent_type}'. Supported: {list(type_map.keys())}"
        )
    if agent_name in mas.oxy_name_to_oxy:
        return _err(f"Oxy '{agent_name}' already exists")

    # Resolve llm_model default
    if not llm_model:
        from oxygent.config import Config

        llm_model = Config.get_agent_llm_model()

    if llm_model not in mas.oxy_name_to_oxy:
        return _err(f"LLM model '{llm_model}' not registered in MAS")

    # Parse comma-separated lists
    sub_agents_list = [s.strip() for s in sub_agents.split(",") if s.strip()]
    tools_list = [s.strip() for s in tools.split(",") if s.strip()]

    # Validate referenced sub_agents and tools exist
    for sa in sub_agents_list:
        if sa not in mas.oxy_name_to_oxy:
            return _err(f"Sub-agent '{sa}' not found in MAS")
    for t in tools_list:
        if t not in mas.oxy_name_to_oxy:
            return _err(f"Tool '{t}' not found in MAS")

    # Validate parent if specified
    if parent_agent:
        if parent_agent not in mas.oxy_name_to_oxy:
            return _err(f"Parent agent '{parent_agent}' not found")
        if not mas.is_agent(parent_agent):
            return _err(f"'{parent_agent}' is not an agent")

    # Create the agent
    agent_cls = type_map[agent_type]
    kwargs = {
        "name": agent_name,
        "desc": desc,
        "llm_model": llm_model,
        "sub_agents": sub_agents_list,
        "tools": tools_list,
        "use_live_prompt": False,
    }
    if prompt:
        kwargs["prompt"] = prompt

    try:
        agent = agent_cls(**kwargs)
        mas.add_oxy(agent)
        agent.set_mas(mas)
        await agent.init()
    except Exception as e:
        # Rollback if init fails
        mas.oxy_name_to_oxy.pop(agent_name, None)
        return _err(f"Failed to create agent: {e}")

    # Attach to parent
    if parent_agent:
        parent = mas.oxy_name_to_oxy[parent_agent]
        if _is_local_agent(parent):
            parent.sub_agents.append(agent_name)
            parent.add_permitted_tool(agent_name)

    mas.init_agent_organization()
    await _notify_org_updated(oxy_request)
    return _ok(
        f"Agent '{agent_name}' ({agent_type}) created successfully",
        {"name": agent_name, "type": agent_type, "parent": parent_agent},
    )


@oxy_manage_tools.tool(
    description="Delete a registered Oxy instance and clean up all references to it from parent agents. Cannot delete the master agent."
)
async def delete_oxy(
    oxy_name: str = Field(description="The name of the Oxy instance to delete"),
    oxy_request: OxyRequest = None,
) -> str:
    mas = oxy_request.mas
    if oxy_name not in mas.oxy_name_to_oxy:
        return _err(f"Oxy '{oxy_name}' not found")

    if oxy_name == mas.master_agent_name:
        return _err("Cannot delete the master agent")

    oxy = mas.oxy_name_to_oxy[oxy_name]

    # Cleanup the oxy instance
    try:
        await oxy.cleanup()
    except Exception as e:
        logger.warning(f"Cleanup for '{oxy_name}' raised: {e}")

    # Remove references from all parent agents
    for _, other in mas.oxy_name_to_oxy.items():
        if not _is_local_agent(other):
            continue
        if oxy_name in other.sub_agents:
            other.sub_agents.remove(oxy_name)
        if oxy_name in other.tools:
            other.tools.remove(oxy_name)
        if oxy_name in other.permitted_tool_name_list:
            other.permitted_tool_name_list.remove(oxy_name)

    del mas.oxy_name_to_oxy[oxy_name]
    mas.init_agent_organization()
    await _notify_org_updated(oxy_request)
    return _ok(f"Oxy '{oxy_name}' deleted successfully")


@oxy_manage_tools.tool(
    description="Move a sub-agent or tool from one parent agent to another parent agent"
)
async def move_oxy(
    oxy_name: str = Field(description="The name of the Oxy instance to move"),
    from_parent: str = Field(description="The name of the current parent agent"),
    to_parent: str = Field(description="The name of the new parent agent"),
    oxy_request: OxyRequest = None,
) -> str:
    mas = oxy_request.mas
    for name in (oxy_name, from_parent, to_parent):
        if name not in mas.oxy_name_to_oxy:
            return _err(f"Oxy '{name}' not found")

    if not mas.is_agent(from_parent):
        return _err(f"'{from_parent}' is not an agent")
    if not mas.is_agent(to_parent):
        return _err(f"'{to_parent}' is not an agent")

    src = mas.oxy_name_to_oxy[from_parent]
    dst = mas.oxy_name_to_oxy[to_parent]

    if not _is_local_agent(src) or not _is_local_agent(dst):
        return _err("Both parent agents must be local agents")

    # Remove from source
    is_sub_agent = oxy_name in src.sub_agents
    is_tool = oxy_name in src.tools

    if not is_sub_agent and not is_tool and oxy_name not in src.permitted_tool_name_list:
        return _err(f"'{oxy_name}' is not a child of '{from_parent}'")

    if is_sub_agent:
        src.sub_agents.remove(oxy_name)
    if is_tool:
        src.tools.remove(oxy_name)
    if oxy_name in src.permitted_tool_name_list:
        src.permitted_tool_name_list.remove(oxy_name)

    # Add to destination
    if mas.is_agent(oxy_name):
        if oxy_name not in dst.sub_agents:
            dst.sub_agents.append(oxy_name)
    else:
        if oxy_name not in dst.tools:
            dst.tools.append(oxy_name)
    dst.add_permitted_tool(oxy_name)

    mas.init_agent_organization()
    await _notify_org_updated(oxy_request)
    return _ok(f"Moved '{oxy_name}' from '{from_parent}' to '{to_parent}'")


@oxy_manage_tools.tool(
    description="Modify a field on an existing Oxy instance. For list fields (sub_agents, tools), provide a JSON array string. Supports: prompt, desc, llm_model, sub_agents, tools, short_memory_size, and other fields."
)
async def modify_oxy(
    oxy_name: str = Field(description="The name of the Oxy instance to modify"),
    field_name: str = Field(
        description="The field to modify (e.g., 'prompt', 'desc', 'llm_model', 'sub_agents', 'tools')"
    ),
    field_value: str = Field(
        description="The new value. Use JSON for lists/dicts (e.g., '[\"a\", \"b\"]'). Plain string for scalar fields."
    ),
    oxy_request: OxyRequest = None,
) -> str:
    mas = oxy_request.mas
    if oxy_name not in mas.oxy_name_to_oxy:
        return _err(f"Oxy '{oxy_name}' not found")

    oxy = mas.oxy_name_to_oxy[oxy_name]

    # Prevent modifying critical identity fields
    if field_name in ("name", "mas", "class_name"):
        return _err(f"Cannot modify protected field '{field_name}'")

    if not hasattr(oxy, field_name):
        return _err(f"Oxy '{oxy_name}' has no field '{field_name}'")

    # Parse value: try JSON first, fall back to plain string
    try:
        parsed_value = json.loads(field_value)
    except (json.JSONDecodeError, TypeError):
        parsed_value = field_value

    # Type-check for numeric fields
    current_value = getattr(oxy, field_name)
    if isinstance(current_value, int) and not isinstance(parsed_value, int):
        try:
            parsed_value = int(parsed_value)
        except (ValueError, TypeError):
            return _err(
                f"Field '{field_name}' expects an integer, got '{field_value}'"
            )

    # Apply the change
    try:
        setattr(oxy, field_name, parsed_value)
    except Exception as e:
        return _err(f"Failed to set '{field_name}': {e}")

    # If sub_agents or tools changed, rebuild permitted list
    structural_fields = ("sub_agents", "tools", "banks")
    if field_name in structural_fields and _is_local_agent(oxy):
        # Clear and rebuild permitted_tool_name_list
        oxy.permitted_tool_name_list = []
        try:
            oxy._init_available_tool_name_list()
        except Exception as e:
            return _err(
                f"Field updated but failed to rebuild tool list: {e}"
            )
        mas.init_agent_organization()
        await _notify_org_updated(oxy_request)

    return _ok(f"Updated '{oxy_name}.{field_name}' successfully")
