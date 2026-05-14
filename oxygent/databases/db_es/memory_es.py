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
import logging
from typing import Any, Optional

from .base_es import BaseEs

logger = logging.getLogger(__name__)


class MemoryEs(BaseEs):
    """Pure in-memory ES shim – no persistence, no external dependencies.

    Implements its own singleton pattern so it can be used directly
    (``MemoryEs()``) without going through ``DBFactory``.
    """

    _singleton: "MemoryEs | None" = None

    def __new__(cls, *args, **kwargs):
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

    async def index(self, index_name: str, doc_id: str, body: dict[str, Any]):
        self._indices.setdefault(index_name, {})[doc_id] = copy.deepcopy(body)
        return {"_id": doc_id, "result": "created"}

    async def update(self, index_name: str, doc_id: str, body: dict[str, Any]):
        store = self._indices.setdefault(index_name, {})
        merged = store.get(doc_id, {})
        merged.update(copy.deepcopy(body))
        store[doc_id] = merged
        return {"_id": doc_id, "result": "updated"}

    async def exists(self, index_name: str, doc_id: str) -> bool:
        return doc_id in self._indices.get(index_name, {})

    async def search(self, index_name: str, body: dict[str, Any]):
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

    async def find_node_safe(self, index_name: str, trace_id: str, node_id: str):
        result = await self.get_by_node_id(index_name, node_id)
        if result:
            if result["_source"].get("trace_id") == trace_id:
                return result
            else:
                logger.warning(
                    f"Node {node_id} found but trace_id mismatch: "
                    f"expected {trace_id}, got {result['_source'].get('trace_id')}"
                )

        compound_query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"trace_id": trace_id}},
                        {"term": {"node_id": node_id}},
                    ]
                }
            },
            "size": 1,
        }
        search_result = await self.search(index_name, compound_query)
        hits = search_result.get("hits", {}).get("hits", [])
        return hits[0] if hits else None

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

    # ------------------------------------------------------------------
    # Helpers for naive query execution
    # ------------------------------------------------------------------

    @staticmethod
    def _build_docs(data: dict[str, Any]):
        return [{"_id": k, "_source": v} for k, v in data.items()]

    @staticmethod
    def _apply_source_filtering(docs: list[dict[str, Any]], source_fields: list[str]):
        """Filter _source fields to only include specified fields."""
        filtered_docs = []
        for doc in docs:
            filtered_doc = doc.copy()
            filtered_source = {}
            for field in source_fields:
                if field in doc["_source"]:
                    filtered_source[field] = doc["_source"][field]
            filtered_doc["_source"] = filtered_source
            filtered_docs.append(filtered_doc)
        return filtered_docs

    def _filter_docs(self, docs: list[dict[str, Any]], query: dict[str, Any]):
        if not query:
            return docs

        if "match_all" in query:
            return docs

        if "term" in query:
            k, v = next(iter(query["term"].items()))
            if k == "_id":
                return [d for d in docs if d["_id"] == v]
            return [d for d in docs if d["_source"].get(k) == v]

        if "terms" in query:
            k, vlist = next(iter(query["terms"].items()))
            return [d for d in docs if d["_source"].get(k) in vlist]

        if "match" in query:
            k, v = next(iter(query["match"].items()))
            v_lower = str(v).lower()
            if k == "_id":
                return [d for d in docs if v_lower in str(d["_id"]).lower()]
            return [d for d in docs if v_lower in str(d["_source"].get(k, "")).lower()]

        if "range" in query:
            k, bounds = next(iter(query["range"].items()))
            filtered = []
            for d in docs:
                val = d["_source"].get(k)
                if val is None:
                    continue
                if "gte" in bounds and val < bounds["gte"]:
                    continue
                if "gt" in bounds and val <= bounds["gt"]:
                    continue
                if "lte" in bounds and val > bounds["lte"]:
                    continue
                if "lt" in bounds and val >= bounds["lt"]:
                    continue
                filtered.append(d)
            return filtered

        if "bool" in query:
            bool_query = query["bool"]
            filtered_docs = docs

            for condition in bool_query.get("must", []):
                filtered_docs = self._filter_docs(filtered_docs, condition)

            for condition in bool_query.get("filter", []):
                filtered_docs = self._filter_docs(filtered_docs, condition)

            for cond in bool_query.get("must_not", []):
                filtered_docs = [
                    d
                    for d in filtered_docs
                    if not self._match_single_condition(d, cond)
                ]

            should_conditions = bool_query.get("should", [])
            if should_conditions:
                has_required = bool_query.get("must") or bool_query.get("filter")
                if not has_required:
                    filtered_docs = [
                        d
                        for d in filtered_docs
                        if any(
                            self._match_single_condition(d, cond)
                            for cond in should_conditions
                        )
                    ]

            return filtered_docs

        return docs

    def _match_single_condition(
        self, doc: dict[str, Any], condition: dict[str, Any]
    ) -> bool:
        if "term" in condition:
            k, v = next(iter(condition["term"].items()))
            if k == "_id":
                return doc["_id"] == v
            return doc["_source"].get(k) == v

        if "terms" in condition:
            k, vlist = next(iter(condition["terms"].items()))
            return doc["_source"].get(k) in vlist

        if "match" in condition:
            k, v = next(iter(condition["match"].items()))
            if k == "_id":
                field_value = str(doc["_id"])
            else:
                field_value = str(doc["_source"].get(k, ""))
            return str(v).lower() in field_value.lower()

        if "range" in condition:
            k, bounds = next(iter(condition["range"].items()))
            val = doc["_source"].get(k)
            if val is None:
                return False
            if "gte" in bounds and val < bounds["gte"]:
                return False
            if "gt" in bounds and val <= bounds["gt"]:
                return False
            if "lte" in bounds and val > bounds["lte"]:
                return False
            if "lt" in bounds and val >= bounds["lt"]:
                return False
            return True

        return False

    @staticmethod
    def _sort_docs(docs: list[dict[str, Any]], spec: list[dict[str, Any]]):
        for s in reversed(spec):
            for field, order in s.items():
                reverse = order.get("order", "asc") == "desc"
                docs.sort(
                    key=lambda d, f=field: (
                        d["_source"].get(f) is None,
                        d["_source"].get(f),
                    ),
                    reverse=reverse,
                )
        return docs
