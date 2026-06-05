"""Integration tests for the Oxy base class lifecycle.

Tests cover: retry logic, delay between retries, friendly_error_text,
semaphore concurrency limiting, ensure_async helper, func_interceptor,
func_execute override, and CancelledError handling.
"""

import asyncio
import time

import pytest

from oxygent.oxy.base_oxy import Oxy, ensure_async
from oxygent.schemas import OxyRequest, OxyResponse, OxyState

# ---------------------------------------------------------------------------
# Concrete Oxy subclass for testing
# ---------------------------------------------------------------------------


class ConcreteOxy(Oxy):
    """Minimal Oxy subclass that records execute calls."""

    call_count: int = 0
    should_fail_times: int = 0
    _failure_exception: type = Exception

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        self.call_count += 1
        if self.call_count <= self.should_fail_times:
            raise self._failure_exception(f"Failure #{self.call_count}")
        return OxyResponse(state=OxyState.COMPLETED, output="success")


class DummyMAS:
    """Minimal MAS stub for Oxy.execute() lifecycle."""

    def __init__(self):
        self.es_client = None
        self.background_tasks = {}
        self.global_data = {}
        self.message_prefix = "msg"
        self.name = "test_mas"
        self.func_process_message = lambda msg, req: msg

    def add_background_task(self, trace_id, task):
        self.background_tasks.setdefault(trace_id, set()).add(task)
        task.add_done_callback(
            lambda t: self.background_tasks.get(trace_id, set()).discard(t)
        )

    async def send_message(self, message, redis_key, group_id=""):
        pass


def _make_request(mas=None) -> OxyRequest:
    req = OxyRequest(
        arguments={"query": "test"},
        caller="user",
        caller_category="user",
        current_trace_id="trace_test",
    )
    if mas:
        req.set_mas(mas)
    return req


# ---------------------------------------------------------------------------
# Tests: ensure_async
# ---------------------------------------------------------------------------


class TestEnsureAsync:
    @pytest.mark.asyncio
    async def test_sync_function_wrapped(self):
        def sync_fn(x):
            return x * 2

        async_fn = ensure_async(sync_fn)
        assert asyncio.iscoroutinefunction(async_fn)
        result = await async_fn(5)
        assert result == 10

    def test_async_function_unchanged(self):
        async def async_fn(x):
            return x * 3

        result = ensure_async(async_fn)
        assert result is async_fn

    def test_none_returns_none(self):
        assert ensure_async(None) is None


# ---------------------------------------------------------------------------
# Tests: Retry logic
# ---------------------------------------------------------------------------


class TestRetryLogic:
    @pytest.mark.asyncio
    async def test_no_retry_on_success(self):
        oxy = ConcreteOxy(name="ok", retries=3, delay=0)
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        resp = await oxy.execute(req)
        assert resp.state is OxyState.COMPLETED
        assert oxy.call_count == 1

    @pytest.mark.asyncio
    async def test_retries_on_failure_then_succeeds(self):
        oxy = ConcreteOxy(name="retry_ok", retries=3, delay=0, should_fail_times=2)
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        resp = await oxy.execute(req)
        assert resp.state is OxyState.COMPLETED
        assert resp.output == "success"
        assert oxy.call_count == 3

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        oxy = ConcreteOxy(name="fail", retries=2, delay=0, should_fail_times=10)
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        resp = await oxy.execute(req)
        assert resp.state is OxyState.FAILED
        assert "Error executing oxy" in resp.output
        assert oxy.call_count == 2

    @pytest.mark.asyncio
    async def test_delay_between_retries(self):
        oxy = ConcreteOxy(name="delay", retries=2, delay=0.1, should_fail_times=1)
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        start = time.time()
        resp = await oxy.execute(req)
        elapsed = time.time() - start
        assert resp.state is OxyState.COMPLETED
        assert elapsed >= 0.09


# ---------------------------------------------------------------------------
# Tests: friendly_error_text
# ---------------------------------------------------------------------------


class TestFriendlyErrorText:
    @pytest.mark.asyncio
    async def test_friendly_error_replaces_output_on_failure(self):
        oxy = ConcreteOxy(
            name="friendly",
            retries=1,
            delay=0,
            should_fail_times=10,
            friendly_error_text="Something went wrong, please try again.",
        )
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        resp = await oxy.execute(req)
        assert resp.state is OxyState.FAILED
        assert resp.output == "Something went wrong, please try again."

    @pytest.mark.asyncio
    async def test_no_friendly_error_on_success(self):
        oxy = ConcreteOxy(
            name="friendly_ok",
            retries=1,
            delay=0,
            friendly_error_text="oops",
        )
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        resp = await oxy.execute(req)
        assert resp.state is OxyState.COMPLETED
        assert resp.output == "success"


# ---------------------------------------------------------------------------
# Tests: Semaphore
# ---------------------------------------------------------------------------


class TestSemaphore:
    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self):
        concurrent_count = 0
        max_concurrent = 0

        class SlowOxy(Oxy):
            async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
                nonlocal concurrent_count, max_concurrent
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
                await asyncio.sleep(0.05)
                concurrent_count -= 1
                return OxyResponse(state=OxyState.COMPLETED, output="done")

        oxy = SlowOxy(name="slow", semaphore=2, retries=1, delay=0)
        mas = DummyMAS()
        oxy.set_mas(mas)

        tasks = []
        for _ in range(5):
            req = _make_request(mas)
            tasks.append(asyncio.create_task(oxy.execute(req)))
        await asyncio.gather(*tasks)
        assert max_concurrent <= 2


# ---------------------------------------------------------------------------
# Tests: func_interceptor
# ---------------------------------------------------------------------------


class TestFuncInterceptor:
    @pytest.mark.asyncio
    async def test_interceptor_blocks_execution(self):
        async def _block(req):
            return "Blocked by policy"

        oxy = ConcreteOxy(name="blocked", retries=1, delay=0, func_interceptor=_block)
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        resp = await oxy.execute(req)
        assert resp.state is OxyState.SKIPPED
        assert resp.output == "Blocked by policy"
        assert oxy.call_count == 0

    @pytest.mark.asyncio
    async def test_interceptor_allows_execution(self):
        async def _allow(req):
            return None

        oxy = ConcreteOxy(name="allowed", retries=1, delay=0, func_interceptor=_allow)
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        resp = await oxy.execute(req)
        assert resp.state is OxyState.COMPLETED

    @pytest.mark.asyncio
    async def test_sync_interceptor_auto_wrapped(self):
        def _sync_block(req):
            return "sync block"

        oxy = ConcreteOxy(
            name="sync_int", retries=1, delay=0, func_interceptor=_sync_block
        )
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        resp = await oxy.execute(req)
        assert resp.state is OxyState.SKIPPED
        assert resp.output == "sync block"


# ---------------------------------------------------------------------------
# Tests: func_execute override
# ---------------------------------------------------------------------------


class TestFuncExecute:
    @pytest.mark.asyncio
    async def test_func_execute_overrides_internal_execute(self):
        async def _custom(req):
            return OxyResponse(state=OxyState.COMPLETED, output="custom")

        oxy = ConcreteOxy(name="custom_exec", retries=1, delay=0, func_execute=_custom)
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        resp = await oxy.execute(req)
        assert resp.output == "custom"
        assert oxy.call_count == 0


# ---------------------------------------------------------------------------
# Tests: CancelledError
# ---------------------------------------------------------------------------


class TestCancelledError:
    @pytest.mark.asyncio
    async def test_cancelled_error_propagates(self):
        class CancelOxy(Oxy):
            async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
                raise asyncio.CancelledError()

        oxy = CancelOxy(name="cancel", retries=3, delay=0)
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        with pytest.raises(asyncio.CancelledError):
            await oxy.execute(req)


# ---------------------------------------------------------------------------
# Tests: func_process_input / func_process_output
# ---------------------------------------------------------------------------


class TestProcessHooks:
    @pytest.mark.asyncio
    async def test_process_input_modifies_request(self):
        async def _add_field(req):
            req.arguments["injected"] = True
            return req

        class CheckOxy(Oxy):
            async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
                assert oxy_request.arguments.get("injected") is True
                return OxyResponse(state=OxyState.COMPLETED, output="ok")

        oxy = CheckOxy(
            name="check_input", retries=1, delay=0, func_process_input=_add_field
        )
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        resp = await oxy.execute(req)
        assert resp.state is OxyState.COMPLETED

    @pytest.mark.asyncio
    async def test_process_output_modifies_response(self):
        async def _modify_output(resp):
            resp.output = resp.output.upper()
            return resp

        oxy = ConcreteOxy(
            name="upper", retries=1, delay=0, func_process_output=_modify_output
        )
        mas = DummyMAS()
        oxy.set_mas(mas)
        req = _make_request(mas)
        resp = await oxy.execute(req)
        assert resp.output == "SUCCESS"
