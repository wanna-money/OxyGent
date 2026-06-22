"""Unit tests for JimdbApRedis."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from oxygent.databases.db_redis.jimdb_ap_redis import JimdbApRedis
except Exception:
    pytest.skip("aioredis not available in this environment", allow_module_level=True)


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def redis_client(monkeypatch):
    """Create JimdbApRedis with mocked redis_pool."""
    with patch(
        "oxygent.databases.db_redis.jimdb_ap_redis.Redis.from_url"
    ) as mock_from_url:
        mock_pool = AsyncMock()
        mock_from_url.return_value = mock_pool
        # pipeline() is a sync method returning an async context manager
        mock_pool.pipeline = MagicMock()

        client = JimdbApRedis("localhost", 6379, "pass")
        client.redis_pool = mock_pool
        yield client


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_set_get_exists_delete(redis_client):
    r = redis_client.redis_pool
    r.set.return_value = True
    r.get.return_value = b"val"
    r.exists.return_value = 1
    r.delete.return_value = 1

    assert await redis_client.set("k", "v") is True
    assert await redis_client.get("k") == b"val"
    assert await redis_client.exists("k") == 1
    assert await redis_client.delete("k") == 1


@pytest.mark.asyncio
async def test_mset_mget(redis_client):
    r = redis_client.redis_pool
    r.mset.return_value = True
    r.mget.return_value = [b"a", b"b"]

    items = {"x": "1", "y": "2"}
    assert await redis_client.mset(items) is True
    assert await redis_client.mget(["x", "y"]) == [b"a", b"b"]


@pytest.mark.asyncio
async def test_expire(redis_client):
    r = redis_client.redis_pool
    r.expire.return_value = True

    assert await redis_client.expire("k", 10) is True


@pytest.mark.asyncio
async def test_expire_none(redis_client):
    """expire with ex=None returns True without calling redis."""
    result = await redis_client.expire("k", None)
    assert result is True


def _make_pipe_mock(execute_return=None):
    """Create a mock pipeline that works as an async context manager."""
    pipe = MagicMock()
    pipe.__aenter__ = AsyncMock(return_value=pipe)
    pipe.__aexit__ = AsyncMock(return_value=False)
    pipe.execute = AsyncMock(return_value=execute_return or [1, True, True])
    return pipe


@pytest.mark.asyncio
async def test_lpush_with_pipeline(redis_client):
    """lpush uses pipeline to atomically push, trim, and expire."""
    r = redis_client.redis_pool
    pipe = _make_pipe_mock([3, True, True])
    r.pipeline.return_value = pipe

    result = await redis_client.lpush("mylist", "val1", "val2", max_size=10, ex=60)
    assert result == 3
    pipe.lpush.assert_called_once_with("mylist", "val1", "val2")
    pipe.ltrim.assert_called_once_with("mylist", 0, 9)
    pipe.expire.assert_called_once_with("mylist", 60)


@pytest.mark.asyncio
async def test_lpush_truncates_long_values(redis_client):
    """lpush truncates string values exceeding max_length."""
    r = redis_client.redis_pool
    pipe = _make_pipe_mock([1, True, True])
    r.pipeline.return_value = pipe

    long_value = "a" * 100
    await redis_client.lpush("k", long_value, max_length=10, max_size=5, ex=30)
    # The pushed value should be truncated to 10 chars
    call_args = pipe.lpush.call_args
    assert len(call_args[0][1]) == 10


@pytest.mark.asyncio
async def test_lpush_dict_value(redis_client):
    """lpush serializes dict values to JSON."""
    r = redis_client.redis_pool
    pipe = _make_pipe_mock([1, True, True])
    r.pipeline.return_value = pipe

    await redis_client.lpush("k", {"key": "val"}, max_size=5, ex=30)
    call_args = pipe.lpush.call_args
    pushed_val = call_args[0][1]
    assert '"key"' in pushed_val
    assert '"val"' in pushed_val


@pytest.mark.asyncio
async def test_lpush_unsupported_type(redis_client):
    """lpush raises ValueError for unsupported value types."""
    with pytest.raises(ValueError, match="Unsupported value type"):
        await redis_client.lpush("k", [1, 2, 3], max_size=5, ex=30)


@pytest.mark.asyncio
async def test_rpop(redis_client):
    r = redis_client.redis_pool
    r.rpop.return_value = b"val"

    result = await redis_client.rpop("mylist")
    assert result == b"val"
    r.rpop.assert_called_once_with("mylist")


@pytest.mark.asyncio
async def test_lrange(redis_client):
    r = redis_client.redis_pool
    r.lrange.return_value = [b"a", b"b", b"c"]

    result = await redis_client.lrange("mylist", 0, -1)
    assert result == [b"a", b"b", b"c"]


@pytest.mark.asyncio
async def test_llen(redis_client):
    r = redis_client.redis_pool
    r.llen.return_value = 5

    result = await redis_client.llen("mylist")
    assert result == 5


@pytest.mark.asyncio
async def test_close(redis_client):
    r = redis_client.redis_pool
    r.close = AsyncMock()
    r.connection_pool = AsyncMock()
    r.connection_pool.disconnect = AsyncMock()

    await redis_client.close()
    r.close.assert_called_once()
    r.connection_pool.disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_close_with_no_pool():
    """close does nothing when redis_pool is None."""
    with patch("oxygent.databases.db_redis.jimdb_ap_redis.Redis.from_url"):
        client = JimdbApRedis("localhost", 6379, "pass")
        client.redis_pool = None
        await client.close()  # Should not raise
