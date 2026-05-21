"""End-to-end tests for the OxyGent HTTP API endpoints.

Tests the FastAPI routes defined in ``oxygent/routes.py`` (shared router)
using ``httpx.AsyncClient`` with the ASGI transport — no real server needed.

NOTE: Endpoints defined inline in ``MAS.start_web_service()`` (e.g. /chat,
/get_organization) are not on the shared router. We test those by constructing
a minimal FastAPI app that includes the shared router and manually mounting
the MAS-specific endpoints.
"""

import json

import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient

from oxygent.mas import MAS
from oxygent.oxy.agents.chat_agent import ChatAgent
from oxygent.oxy.llms.mock_llm import MockLLM
from oxygent.routes import router
from oxygent.schemas import WebResponse
from oxygent.utils.common_utils import generate_uuid

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_llm(response: str = "API test response") -> MockLLM:
    async def _fn(oxy_request):
        return response

    return MockLLM(name="default_llm", func_mock_process=_fn)


def _make_chat_agent() -> ChatAgent:
    return ChatAgent(
        name="chat_agent",
        desc="Test chat agent",
        llm_model="default_llm",
        is_master=True,
    )


def _build_app_with_mas(mas):
    """Build a FastAPI app with MAS-specific endpoints."""
    app = FastAPI()
    app.include_router(router)

    @app.api_route("/chat", methods=["GET", "POST"])
    async def chat(request: Request):
        if request.method == "GET":
            params = dict(request.query_params)
            payload = json.loads(params.get("payload", "{}"))
        else:
            payload = await request.json()

        if "query" not in payload:
            payload["query"] = ""
        if "current_trace_id" not in payload:
            payload["current_trace_id"] = generate_uuid()
        if "shared_data" not in payload:
            payload["shared_data"] = {}

        oxy_response = await mas.chat_with_agent(payload=payload)
        return {
            "answer": oxy_response.output,
            "current_trace_id": oxy_response.oxy_request.current_trace_id,
        }

    @app.get("/get_organization")
    def get_organization():
        return WebResponse(data={"organization": mas.agent_organization}).to_dict()

    @app.get("/get_welcome_message")
    def get_welcome_message():
        return WebResponse(
            data={"welcome_message": mas.welcome_message or ""}
        ).to_dict()

    @app.get("/get_agents")
    def get_agents():
        agents = []

        def extract_agents(node):
            if isinstance(node, dict):
                if node.get("type") == "agent":
                    agents.append({"name": node.get("name", "")})
                children = node.get("children", [])
                if isinstance(children, list):
                    for child in children:
                        extract_agents(child)

        if mas.agent_organization:
            extract_agents(mas.agent_organization)
        return WebResponse(data={"agents": agents}).to_dict()

    return app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def app_with_router():
    """Create a minimal FastAPI app with the shared router only."""
    app = FastAPI()
    app.include_router(router)
    return app


# ---------------------------------------------------------------------------
# Tests: Shared router endpoints
# ---------------------------------------------------------------------------


class TestSharedRouterEndpoints:
    """Tests for endpoints defined on the shared router in routes.py."""

    @pytest.mark.asyncio
    async def test_check_alive(self, app_with_router):
        transport = ASGITransport(app=app_with_router)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/check_alive")
        assert response.status_code == 200
        data = response.json()
        assert data["alive"] == 1

    @pytest.mark.asyncio
    async def test_root_redirects(self, app_with_router):
        transport = ASGITransport(app=app_with_router)
        async with AsyncClient(
            transport=transport, base_url="http://test", follow_redirects=False
        ) as client:
            response = await client.get("/")
        assert response.status_code in (307, 308)
        assert "web/index.html" in response.headers.get("location", "")


# ---------------------------------------------------------------------------
# Tests: MAS-specific endpoints
# ---------------------------------------------------------------------------


class TestMASEndpoints:
    """Tests for endpoints that require a live MAS instance.

    Each test creates its own MAS + app to avoid async fixture issues.
    """

    @pytest.mark.asyncio
    async def test_chat_endpoint(self):
        async with MAS(oxy_space=[_make_mock_llm(), _make_chat_agent()]) as mas:
            app = _build_app_with_mas(mas)
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.post(
                    "/chat",
                    json={"query": "Hello from API test"},
                )
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert data["answer"] == "API test response"
            assert "current_trace_id" in data

    @pytest.mark.asyncio
    async def test_chat_endpoint_empty_query(self):
        async with MAS(oxy_space=[_make_mock_llm(), _make_chat_agent()]) as mas:
            app = _build_app_with_mas(mas)
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.post("/chat", json={})
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data

    @pytest.mark.asyncio
    async def test_get_organization(self):
        async with MAS(oxy_space=[_make_mock_llm(), _make_chat_agent()]) as mas:
            app = _build_app_with_mas(mas)
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/get_organization")
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "organization" in data["data"]
            org = data["data"]["organization"]
            assert org["name"] == "chat_agent"

    @pytest.mark.asyncio
    async def test_get_welcome_message(self):
        async with MAS(oxy_space=[_make_mock_llm(), _make_chat_agent()]) as mas:
            app = _build_app_with_mas(mas)
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/get_welcome_message")
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "welcome_message" in data["data"]

    @pytest.mark.asyncio
    async def test_get_agents(self):
        async with MAS(oxy_space=[_make_mock_llm(), _make_chat_agent()]) as mas:
            app = _build_app_with_mas(mas)
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/get_agents")
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "agents" in data["data"]
            agent_names = [a["name"] for a in data["data"]["agents"]]
            assert "chat_agent" in agent_names

    @pytest.mark.asyncio
    async def test_chat_with_trace_id(self):
        """Verify that providing a current_trace_id is echoed back."""
        async with MAS(oxy_space=[_make_mock_llm(), _make_chat_agent()]) as mas:
            app = _build_app_with_mas(mas)
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.post(
                    "/chat",
                    json={
                        "query": "trace test",
                        "current_trace_id": "test-trace-abc",
                    },
                )
            assert response.status_code == 200
            data = response.json()
            assert data["current_trace_id"] == "test-trace-abc"
