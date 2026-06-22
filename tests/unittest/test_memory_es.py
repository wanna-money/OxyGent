"""Unit tests for oxygent.databases.db_es.memory_es (MemoryEs)."""

import pytest

from oxygent.databases.db_es.memory_es import MemoryEs


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset MemoryEs singleton between tests."""
    MemoryEs._singleton = None
    yield
    MemoryEs._singleton = None


@pytest.fixture
def es():
    return MemoryEs()


# ──────────────────────────────────────────────────────────────────────────────
# create_index
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_create_index(es):
    result = await es.create_index("idx", {"mappings": {}})
    assert result["acknowledged"] is True


@pytest.mark.asyncio
async def test_create_index_empty_name_returns_none(es):
    """BaseDB retry decorator catches ValueError and returns None."""
    result = await es.create_index("", {"mappings": {}})
    assert result is None


@pytest.mark.asyncio
async def test_create_index_empty_body_returns_none(es):
    result = await es.create_index("idx", {})
    assert result is None


# ──────────────────────────────────────────────────────────────────────────────
# CRUD: index, exists, search, delete
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_index_and_exists(es):
    await es.create_index("idx", {"mappings": {}})
    await es.index("idx", "doc1", {"title": "hello"})
    assert await es.exists("idx", "doc1") is True
    assert await es.exists("idx", "doc_missing") is False


@pytest.mark.asyncio
async def test_search_returns_indexed_docs(es):
    await es.create_index("idx", {"mappings": {}})
    await es.index("idx", "d1", {"name": "alice", "age": 30})
    await es.index("idx", "d2", {"name": "bob", "age": 25})

    result = await es.search("idx", {})
    hits = result["hits"]["hits"]
    assert len(hits) == 2


@pytest.mark.asyncio
async def test_search_with_size(es):
    await es.create_index("idx", {"mappings": {}})
    for i in range(5):
        await es.index("idx", f"d{i}", {"val": i})

    result = await es.search("idx", {"size": 2})
    assert len(result["hits"]["hits"]) == 2


@pytest.mark.asyncio
async def test_delete(es):
    await es.create_index("idx", {"mappings": {}})
    await es.index("idx", "d1", {"val": 1})

    result = await es.delete("idx", "d1")
    assert result["result"] == "deleted"
    assert await es.exists("idx", "d1") is False


@pytest.mark.asyncio
async def test_delete_not_found(es):
    result = await es.delete("idx", "nonexistent")
    assert result["result"] == "not_found"


# ──────────────────────────────────────────────────────────────────────────────
# update
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_update_merges(es):
    await es.index("idx", "d1", {"name": "alice", "age": 30})
    await es.update("idx", "d1", {"age": 31, "city": "NY"})

    result = await es.search("idx", {})
    doc = result["hits"]["hits"][0]["_source"]
    assert doc["name"] == "alice"
    assert doc["age"] == 31
    assert doc["city"] == "NY"


@pytest.mark.asyncio
async def test_update_creates_if_missing(es):
    await es.update("idx", "new_doc", {"field": "value"})
    assert await es.exists("idx", "new_doc") is True


# ──────────────────────────────────────────────────────────────────────────────
# get_by_node_id / update_by_node_id
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_by_node_id(es):
    await es.index("idx", "d1", {"node_id": "n1", "data": "hello"})
    await es.index("idx", "d2", {"node_id": "n2", "data": "world"})

    result = await es.get_by_node_id("idx", "n1")
    assert result is not None
    assert result["_source"]["data"] == "hello"


@pytest.mark.asyncio
async def test_get_by_node_id_not_found(es):
    result = await es.get_by_node_id("idx", "nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_update_by_node_id(es):
    await es.index("idx", "d1", {"node_id": "n1", "status": "pending"})
    result = await es.update_by_node_id("idx", "n1", {"status": "done"})
    assert result["result"] == "updated"

    doc = await es.get_by_node_id("idx", "n1")
    assert doc["_source"]["status"] == "done"


@pytest.mark.asyncio
async def test_update_by_node_id_not_found(es):
    result = await es.update_by_node_id("idx", "missing", {"x": 1})
    assert result["result"] == "not_found"


# ──────────────────────────────────────────────────────────────────────────────
# close
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_close(es):
    assert await es.close() is True


# ──────────────────────────────────────────────────────────────────────────────
# Singleton behavior
# ──────────────────────────────────────────────────────────────────────────────
def test_singleton():
    a = MemoryEs()
    b = MemoryEs()
    assert a is b


# ──────────────────────────────────────────────────────────────────────────────
# Deep copy isolation
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_deep_copy_isolation(es):
    """Modifying the original dict after indexing should not affect stored data."""
    doc = {"key": "original"}
    await es.index("idx", "d1", doc)
    doc["key"] = "mutated"

    result = await es.search("idx", {})
    stored = result["hits"]["hits"][0]["_source"]
    assert stored["key"] == "original"
