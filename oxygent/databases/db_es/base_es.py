"""base_es.py Base Elasticsearch Database Class Module.

This file defines the abstract base class for Elasticsearch database services,
inheriting from BaseDB and providing the interface contract for ES operations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from oxygent.databases.base_db import BaseDB

logger = logging.getLogger(__name__)


class BaseEs(BaseDB, ABC):
    """Abstract base class for Elasticsearch database services.

    This class inherits from BaseDB to get retry functionality and error handling, while
    defining the essential interface that all Elasticsearch implementations must
    provide. All methods are abstract and must be implemented by subclasses.

    Shared query-execution helpers (_build_docs, _filter_docs, _match_single_condition,
    _sort_docs, _apply_source_filtering) and the higher-level find_node_safe are
    implemented here so that in-memory and file-backed subclasses share a single copy.
    """

    @abstractmethod
    async def create_index(self, index_name, body):
        """Create a new index in Elasticsearch with the specified configuration.

        Args:
            index_name: Name of the index to create
            body: Index configuration including mappings, settings, etc.

        Returns:
            Result of the index creation operation

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        pass

    @abstractmethod
    async def index(self, index_name, doc_id, body):
        """Index a document in Elasticsearch.

        This method adds or updates a document in the specified index with the given ID.

        Args:
            index_name: Name of the index to store the document
            doc_id: Unique identifier for the document
            body: Document content to be indexed

        Returns:
            Result of the indexing operation

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        pass

    @abstractmethod
    async def update(self, index_name, doc_id, body):
        """Update a document by ID. Subclasses must implement this."""
        pass

    @abstractmethod
    async def search(self, index_name, body):
        """Execute a search query against an Elasticsearch index.

        Args:
            index_name: Name of the index to search
            body: Search query body containing filters, aggregations, etc.

        Returns:
            Search results matching the query criteria

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        pass

    @abstractmethod
    async def exists(self, index_name, doc_id):
        """Check if a document exists in the specified index.

        Args:
            index_name: Name of the index to check
            doc_id: Document ID to verify existence

        Returns:
            Boolean indicating whether the document exists

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        pass

    @abstractmethod
    async def close(self):
        """Close the Elasticsearch client connection and clean up resources.

        This method should be called when the ES client is no longer needed
        to properly release connections and resources.

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        pass

    # ------------------------------------------------------------------
    # Shared query-execution helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_docs(data: dict[str, Any]) -> list[dict[str, Any]]:
        return [{"_id": k, "_source": v} for k, v in data.items()]

    @staticmethod
    def _apply_source_filtering(
        docs: list[dict[str, Any]], source_fields: list[str]
    ) -> list[dict[str, Any]]:
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

    def _filter_docs(
        self, docs: list[dict[str, Any]], query: dict[str, Any]
    ) -> list[dict[str, Any]]:
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
    def _sort_docs(
        docs: list[dict[str, Any]], spec: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
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

    # ------------------------------------------------------------------
    # Higher-level helpers (polymorphic via search / get_by_node_id)
    # ------------------------------------------------------------------

    async def find_node_safe(
        self, index_name: str, trace_id: str, node_id: str
    ) -> Optional[dict[str, Any]]:
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
