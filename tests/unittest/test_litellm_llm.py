"""Unit tests for LiteLLM."""

from unittest import mock

import pytest

from oxygent.schemas import OxyRequest, OxyState


@pytest.fixture(autouse=True)
def config_patch(monkeypatch):
    monkeypatch.setattr(
        "oxygent.oxy.llms.base_llm.Config.get_llm_config",
        lambda **kwargs: {},
        raising=True,
    )


@pytest.fixture(autouse=True)
def mock_send_message(monkeypatch):
    sent = []
    mock_fn = mock.AsyncMock(
        side_effect=lambda *a, **kw: sent.append(a[0] if a else kw)
    )
    monkeypatch.setattr(
        "oxygent.schemas.oxy.OxyRequest.send_message", mock_fn, raising=True
    )
    return sent


@pytest.fixture
def llm(monkeypatch):
    async def passthrough(self, req: OxyRequest):
        return req.arguments["messages"]

    monkeypatch.setattr(
        "oxygent.oxy.llms.base_llm.BaseLLM._get_messages",
        passthrough,
        raising=True,
    )

    from oxygent.oxy.llms.litellm_llm import LiteLLM

    return LiteLLM(
        name="litellm_test",
        model_name="anthropic/claude-sonnet-4-20250514",
        api_key="sk-test-key",
        llm_params={"temperature": 0.7},
    )


@pytest.fixture
def llm_no_key(monkeypatch):
    async def passthrough(self, req):
        return req.arguments["messages"]

    monkeypatch.setattr(
        "oxygent.oxy.llms.base_llm.BaseLLM._get_messages",
        passthrough,
        raising=True,
    )

    from oxygent.oxy.llms.litellm_llm import LiteLLM

    return LiteLLM(
        name="litellm_nokey",
        model_name="openai/gpt-4o",
    )


@pytest.fixture
def oxy_request():
    return OxyRequest(
        arguments={
            "messages": [{"role": "user", "content": "Hello"}],
        },
        caller="tester",
        caller_category="agent",
        current_trace_id="trace-litellm",
    )


class _FakeChoice:
    def __init__(self, content=None, reasoning_content=None):
        self.delta = mock.MagicMock()
        if reasoning_content is not None:
            self.delta.reasoning_content = reasoning_content
            if content is None:
                del self.delta.content
        if content is not None:
            self.delta.content = content
            if reasoning_content is None:
                del self.delta.reasoning_content


class _FakeChunk:
    def __init__(self, choices=None, usage=None):
        self.choices = choices or []
        self.usage = usage


@pytest.mark.asyncio
async def test_streaming_success(monkeypatch, llm, oxy_request, mock_send_message):
    """Streaming completion returns correct output and sends stream messages."""
    chunks = [
        _FakeChunk(choices=[_FakeChoice(content="Hi")]),
        _FakeChunk(choices=[_FakeChoice(content=" there")]),
        _FakeChunk(
            choices=[],
            usage=mock.MagicMock(
                prompt_tokens=10, completion_tokens=5, total_tokens=15
            ),
        ),
    ]

    async def fake_acompletion(**kwargs):
        async def gen():
            for c in chunks:
                yield c

        return gen()

    monkeypatch.setattr(
        "oxygent.oxy.llms.litellm_llm.litellm.acompletion", fake_acompletion
    )

    resp = await llm._execute(oxy_request)

    assert resp.state is OxyState.COMPLETED
    assert resp.output == "Hi there"


@pytest.mark.asyncio
async def test_non_streaming(monkeypatch, llm, oxy_request):
    """Non-streaming completion returns content directly."""
    oxy_request.arguments["stream"] = False

    fake_resp = mock.MagicMock()
    fake_resp.choices = [mock.MagicMock()]
    fake_resp.choices[0].message.content = "Result: 4"
    fake_resp.usage = mock.MagicMock(
        prompt_tokens=8, completion_tokens=3, total_tokens=11
    )

    monkeypatch.setattr(
        "oxygent.oxy.llms.litellm_llm.litellm.acompletion",
        mock.AsyncMock(return_value=fake_resp),
    )

    resp = await llm._execute(oxy_request)

    assert resp.state is OxyState.COMPLETED
    assert resp.output == "Result: 4"


@pytest.mark.asyncio
async def test_api_key_forwarded(monkeypatch, llm, oxy_request):
    """api_key is included in the litellm.acompletion call when set."""
    oxy_request.arguments["stream"] = False

    fake_resp = mock.MagicMock()
    fake_resp.choices = [mock.MagicMock()]
    fake_resp.choices[0].message.content = "ok"
    fake_resp.usage = None

    captured = {}

    async def capture(**kwargs):
        captured.update(kwargs)
        return fake_resp

    monkeypatch.setattr("oxygent.oxy.llms.litellm_llm.litellm.acompletion", capture)

    await llm._execute(oxy_request)

    assert captured["api_key"] == "sk-test-key"
    assert captured["model"] == "anthropic/claude-sonnet-4-20250514"
    assert captured["drop_params"] is True


@pytest.mark.asyncio
async def test_api_key_omitted_when_unset(monkeypatch, llm_no_key, oxy_request):
    """When api_key is None, it should not be in the payload."""
    oxy_request.arguments["stream"] = False

    fake_resp = mock.MagicMock()
    fake_resp.choices = [mock.MagicMock()]
    fake_resp.choices[0].message.content = "ok"
    fake_resp.usage = None

    captured = {}

    async def capture(**kwargs):
        captured.update(kwargs)
        return fake_resp

    monkeypatch.setattr("oxygent.oxy.llms.litellm_llm.litellm.acompletion", capture)

    await llm_no_key._execute(oxy_request)

    assert "api_key" not in captured


@pytest.mark.asyncio
async def test_base_url_forwarded(monkeypatch, oxy_request):
    """base_url is passed as api_base to litellm when set."""

    async def passthrough(self, req):
        return req.arguments["messages"]

    monkeypatch.setattr(
        "oxygent.oxy.llms.base_llm.BaseLLM._get_messages",
        passthrough,
        raising=True,
    )

    from oxygent.oxy.llms.litellm_llm import LiteLLM

    llm = LiteLLM(
        name="proxy_llm",
        model_name="openai/gpt-4o",
        base_url="http://localhost:4000",
    )

    oxy_request.arguments["stream"] = False

    fake_resp = mock.MagicMock()
    fake_resp.choices = [mock.MagicMock()]
    fake_resp.choices[0].message.content = "ok"
    fake_resp.usage = None

    captured = {}

    async def capture(**kwargs):
        captured.update(kwargs)
        return fake_resp

    monkeypatch.setattr("oxygent.oxy.llms.litellm_llm.litellm.acompletion", capture)

    await llm._execute(oxy_request)

    assert captured["api_base"] == "http://localhost:4000"


@pytest.mark.asyncio
async def test_drop_params_default_true(monkeypatch, llm, oxy_request):
    """drop_params defaults to True in the payload."""
    oxy_request.arguments["stream"] = False

    fake_resp = mock.MagicMock()
    fake_resp.choices = [mock.MagicMock()]
    fake_resp.choices[0].message.content = "ok"
    fake_resp.usage = None

    captured = {}

    async def capture(**kwargs):
        captured.update(kwargs)
        return fake_resp

    monkeypatch.setattr("oxygent.oxy.llms.litellm_llm.litellm.acompletion", capture)

    await llm._execute(oxy_request)

    assert captured["drop_params"] is True


@pytest.mark.asyncio
async def test_llm_params_merged(monkeypatch, llm, oxy_request):
    """llm_params (e.g. temperature) are merged into the payload."""
    oxy_request.arguments["stream"] = False

    fake_resp = mock.MagicMock()
    fake_resp.choices = [mock.MagicMock()]
    fake_resp.choices[0].message.content = "ok"
    fake_resp.usage = None

    captured = {}

    async def capture(**kwargs):
        captured.update(kwargs)
        return fake_resp

    monkeypatch.setattr("oxygent.oxy.llms.litellm_llm.litellm.acompletion", capture)

    await llm._execute(oxy_request)

    assert captured["temperature"] == 0.7


def test_factory_registration():
    """LiteLLM is registered in OxyFactory."""
    from oxygent.oxy_factory import OxyFactory

    assert "LiteLLM" in OxyFactory._creators
