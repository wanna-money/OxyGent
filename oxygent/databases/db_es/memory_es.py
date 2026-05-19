"""memory_es.py – In-memory Elasticsearch implementation.

This module simulates a subset of Elasticsearch by storing documents entirely
in memory (Python dicts).  It is functionally equivalent to LocalEs but:

* **Zero I/O** – no filesystem reads/writes, no temp files, no locks on disk.
* **Fast** – ideal for unit tests, short-lived processes, and benchmarking.
* **Ephemeral** – all data is lost when the process exits.

Data is deep-copied on every read/write boundary to match the serialisation
isolation provided by LocalEs (JSON files) and JesEs (network).

Only the subset of APIs that OxyGent actually uses is implemented.
"""

from __future__ import annotations

import copy
from typing import Any, Optional

from .base_es import BaseEs


class MemoryEs(BaseEs):
    """Pure in-memory ES shim – no persistence, no external dependencies.

    Implements its own singleton pattern so it can be used directly
    (``MemoryEs()``) without going through ``DBFactory``.
    """

    _singleton: "MemoryEs | None" = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "MemoryEs":
        if cls._singleton is None:
            cls._singleton = super().__new__(cls)
            cls._singleton._indices = {}
            cls._singleton._mappings = {}
        return cls._singleton

    def __init__(self) -> None:
        # Already initialised in __new__; nothing to do.
        pass

    # ------------------------------------------------------------------
    # Public ES-like API
    # ------------------------------------------------------------------

    async def create_index(
        self, index_name: str, body: dict[str, Any]
    ) -> dict[str, bool]:
        if not index_name or not body:
            raise ValueError("index_name and body must not be empty")

        self._mappings[index_name] = body
        if index_name not in self._indices:
            self._indices[index_name] = {}
        return {"acknowledged": True}

    async def index(self, index_name: str, doc_id: str, body: dict[str, Any]) -> dict[str, str]:
        self._indices.setdefault(index_name, {})[doc_id] = copy.deepcopy(body)
        return {"_id": doc_id, "result": "created"}

    async def update(self, index_name: str, doc_id: str, body: dict[str, Any]) -> dict[str, str]:
        store = self._indices.setdefault(index_name, {})
        merged = store.get(doc_id, {})
        merged.update(copy.deepcopy(body))
        store[doc_id] = merged
        return {"_id": doc_id, "result": "updated"}

    async def exists(self, index_name: str, doc_id: str) -> bool:
        return doc_id in self._indices.get(index_name, {})

    async def search(self, index_name: str, body: dict[str, Any]) -> dict[str, Any]:
        data = self._indices.get(index_name, {})
        docs = self._build_docs(data)
        docs = self._filter_docs(docs, body.get("query", {}))
        docs = self._sort_docs(docs, body.get("sort", []))

        # Apply _source filtering if specified
        source_fields = body.get("_source")
        if source_fields and isinstance(source_fields, list):
            docs = self._apply_source_filtering(docs, source_fields)

        return {"hits": {"hits": copy.deepcopy(docs[: body.get("size", 10)])}}

    async def delete(self, index_name: str, doc_id: str) -> dict[str, str]:
        store = self._indices.get(index_name, {})
        if doc_id not in store:
            return {"_id": doc_id, "result": "not_found"}
        del store[doc_id]
        return {"_id": doc_id, "result": "deleted"}

    async def close(self) -> bool:
        return True

    # ------------------------------------------------------------------
    # Extra helpers (same interface as LocalEs)
    # ------------------------------------------------------------------

    async def get_by_node_id(
        self, index_name: str, node_id: str
    ) -> Optional[dict[str, Any]]:
        data = self._indices.get(index_name, {})
        for doc_id, doc_content in data.items():
            if isinstance(doc_content, dict) and doc_content.get("node_id") == node_id:
                return {"_id": doc_id, "_source": copy.deepcopy(doc_content)}
        return None

    async def update_by_node_id(
        self, index_name: str, node_id: str, updates: dict[str, Any]
    ) -> dict[str, str]:
        data = self._indices.get(index_name, {})
        for doc_id, doc_content in data.items():
            if isinstance(doc_content, dict) and doc_content.get("node_id") == node_id:
                doc_content.update(copy.deepcopy(updates))
                return {"_id": doc_id, "result": "updated"}
        return {"_id": "", "result": "not_found"}
