"""Unit tests for oxygent.db_factory (DBFactory)."""

import pytest

from oxygent.db_factory import DBFactory


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def reset_factory():
    """Reset DBFactory singleton state between tests."""
    if hasattr(DBFactory, "_factory_instance"):
        del DBFactory._factory_instance
    DBFactory._instance = None
    DBFactory._created_class = None
    yield
    if hasattr(DBFactory, "_factory_instance"):
        del DBFactory._factory_instance
    DBFactory._instance = None
    DBFactory._created_class = None


# ──────────────────────────────────────────────────────────────────────────────
# Dummy classes for testing
# ──────────────────────────────────────────────────────────────────────────────
class DummyDB:
    def __init__(self, name="default"):
        self.name = name


class AnotherDB:
    pass


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────
def test_first_call_creates_instance():
    factory = DBFactory()
    instance = factory.get_instance(DummyDB, "test")
    assert isinstance(instance, DummyDB)
    assert instance.name == "test"


def test_same_type_returns_cached():
    factory = DBFactory()
    first = factory.get_instance(DummyDB, "test")
    second = factory.get_instance(DummyDB)
    assert first is second


def test_different_type_raises():
    factory = DBFactory()
    factory.get_instance(DummyDB)
    with pytest.raises(Exception, match="single instance"):
        factory.get_instance(AnotherDB)


def test_factory_is_singleton():
    a = DBFactory()
    b = DBFactory()
    assert a is b
