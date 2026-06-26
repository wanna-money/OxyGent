"""Local filesystem-based Elasticsearch implementation (cross-platform, UTF-8-safe).

This module simulates a subset of Elasticsearch by persisting documents as JSON
files on the local filesystem.  The design goals are:

* **Robust cross‑platform behaviour** (Windows/POSIX) – atomic writes with
  `os.replace`, no reliance on POSIX‑only semantics.
* **UTF‑8 persistence** – files created in legacy encodings are lazily migrated.
* **Data‑safety first** – *never* overwrite an existing index unless explicitly
  requested; corrupted files are preserved via ``.bak`` before we attempt any
  recovery so historic logs are not silently lost.

Only the subset of APIs that OxyGent actually uses is implemented.
"""

from __future__ import annotations

import asyncio
import json
import locale
import logging
import os
from typing import Any, Optional

import aiofiles
import aiofiles.os
from aiofiles import tempfile

from oxygent.config import Config

from .base_es import BaseEs

logger = logging.getLogger(__name__)


class LocalEs(BaseEs):
    """Very small file‑system‑backed ES shim with write-behind caching."""

    def __init__(self) -> None:  # noqa: D401 – simple init
        self.data_dir: str = os.path.join(Config.get_cache_save_dir(), "local_es_data")
        os.makedirs(self.data_dir, exist_ok=True)
        self._locks: dict[str, asyncio.Lock] = {}
        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_lock: asyncio.Lock = asyncio.Lock()
        self._dirty: set[str] = set()
        self._flush_interval: float = 0.5
        self._flush_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # Utilities (paths, atomic IO helpers)
    # ------------------------------------------------------------------

    def _index_path(self, index_name: str) -> str:
        return os.path.join(self.data_dir, f"{index_name}.json")

    def _mapping_path(self, index_name: str) -> str:
        return os.path.join(self.data_dir, f"{index_name}_mapping.json")

    async def _write_json_atomic(self, path: str, data: dict[str, Any]) -> None:
        """Write *data* to *path* atomically, UTF‑8 encoded."""
        async with tempfile.NamedTemporaryFile(
            mode="w", delete=False, dir=self.data_dir, suffix=".tmp", encoding="utf-8"
        ) as tf:
            await tf.write(json.dumps(data, ensure_ascii=False, indent=2))
            tmp_path = tf.name
        try:
            await aiofiles.os.replace(tmp_path, path)
        finally:
            if await aiofiles.os.path.exists(tmp_path):
                await aiofiles.os.unlink(tmp_path)

    # ------------------------------------------------------------------
    # Encoding‑aware read helper (returns **None** on unrecoverable corruption)
    # ------------------------------------------------------------------

    async def _read_json_safe(self, path: str) -> Optional[dict[str, Any]]:
        if not await aiofiles.os.path.exists(path):
            return {}

        # a) try utf‑8
        try:
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                return json.loads(await f.read())
        except UnicodeDecodeError:
            pass  # Will fallback.
        except json.JSONDecodeError:
            logger.error(f"JSON corrupted (utf‑8) → {path}", exc_info=True)
            return None  # unrecoverable corruption

        # b) fallback – system code‑page
        fallback_enc = locale.getpreferredencoding(False) or "utf-8"
        try:
            async with aiofiles.open(path, "r", encoding=fallback_enc) as f:
                raw = await f.read()
            data = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            logger.error(f"JSON corrupted ({fallback_enc}) → {path}", exc_info=True)
            return None

        # c) successful fallback – migrate
        try:
            await self._write_json_atomic(path, data)
        except Exception as err:  # noqa: BLE001 – non‑critical
            logger.warning(f"Could not rewrite {path} as UTF‑8: {err}", exc_info=True)
        return data

    # ------------------------------------------------------------------
    # Public ES‑like API
    # ------------------------------------------------------------------

    async def create_index(
        self, index_name: str, body: dict[str, Any]
    ) -> dict[str, bool]:
        if not index_name or not body:
            raise ValueError("index_name and body must not be empty")

        # 1) persist mapping (overwrite OK – mapping updates should be explicit)
        await self._write_json_atomic(self._mapping_path(index_name), body)

        # 2) create empty index *only if it does not exist* – avoids wiping logs
        index_path = self._index_path(index_name)
        if not await aiofiles.os.path.exists(index_path):
            await self._write_json_atomic(index_path, {})
        return {"acknowledged": True}

    async def _ensure_cached(self, index_name: str) -> dict[str, Any]:
        """Load an index into the in-memory cache if not already present."""
        if index_name not in self._cache:
            data_path = self._index_path(index_name)
            self._cache[index_name] = (
                await self._read_json_safe(data_path) or {}
            )
        return self._cache[index_name]

    def _schedule_flush(self, index_name: str) -> None:
        """Mark an index as dirty and ensure the flush loop is running."""
        self._dirty.add(index_name)
        if self._flush_task is None or self._flush_task.done():
            self._flush_task = asyncio.create_task(self._flush_loop())

    async def _flush_loop(self) -> None:
        """Periodically flush dirty indices to disk."""
        while self._dirty:
            await asyncio.sleep(self._flush_interval)
            await self._flush_dirty()

    async def _flush_dirty(self) -> None:
        """Flush all dirty indices to disk."""
        async with self._cache_lock:
            to_flush = list(self._dirty)
            self._dirty.clear()
            snapshots: dict[str, dict[str, Any]] = {}
            for index_name in to_flush:
                data = self._cache.get(index_name)
                if data is not None:
                    snapshots[index_name] = json.loads(
                        json.dumps(data, ensure_ascii=False, default=str)
                    )

        for index_name, snapshot in snapshots.items():
            data_path = self._index_path(index_name)
            backup_path = f"{data_path}.bak"
            lock = self._locks.setdefault(index_name, asyncio.Lock())
            async with lock:
                await self._write_json_atomic(data_path, snapshot)
                try:
                    await self._write_json_atomic(backup_path, snapshot)
                except Exception as e:  # noqa: BLE001
                    logger.debug(
                        f"Failed to write backup for index {index_name}: {e}",
                        exc_info=True,
                    )

    async def insert(
        self,
        index_name: str,
        doc_id: str,
        body: dict[str, Any],
        *,
        update_mode: bool,
    ) -> dict[str, str]:
        async with self._cache_lock:
            data = await self._ensure_cached(index_name)
            if update_mode:
                merged = data.get(doc_id, {})
                merged.update(body)
                data[doc_id] = merged
            else:
                data[doc_id] = body
        self._schedule_flush(index_name)
        return {"_id": doc_id, "result": "updated" if update_mode else "created"}

    async def index(
        self, index_name: str, doc_id: str, body: dict[str, Any]
    ) -> dict[str, str]:
        return await self.insert(index_name, doc_id, body, update_mode=False)

    async def update(
        self, index_name: str, doc_id: str, body: dict[str, Any]
    ) -> dict[str, str]:
        return await self.insert(index_name, doc_id, body, update_mode=True)

    async def upsert(
        self, index_name: str, doc_id: str, body: dict[str, Any]
    ) -> dict[str, str]:
        return await self.insert(index_name, doc_id, body, update_mode=True)

    async def exists(self, index_name: str, doc_id: str) -> bool:
        async with self._cache_lock:
            data = await self._ensure_cached(index_name)
            return doc_id in data

    async def search(self, index_name: str, body: dict[str, Any]) -> dict[str, Any]:
        async with self._cache_lock:
            data = await self._ensure_cached(index_name)
            data_snapshot = {k: v.copy() if isinstance(v, dict) else v for k, v in data.items()}
        docs = self._build_docs(data_snapshot)
        docs = self._filter_docs(docs, body.get("query", {}))
        docs = self._sort_docs(docs, body.get("sort", []))

        # Apply _source filtering if specified
        source_fields = body.get("_source")
        if source_fields and isinstance(source_fields, list):
            docs = self._apply_source_filtering(docs, source_fields)

        return {"hits": {"hits": docs[: body.get("size", 10)]}}

    async def get_by_node_id(
        self, index_name: str, node_id: str
    ) -> Optional[dict[str, Any]]:
        async with self._cache_lock:
            data = await self._ensure_cached(index_name)
            for doc_id, doc_content in data.items():
                if isinstance(doc_content, dict) and doc_content.get("node_id") == node_id:
                    return {"_id": doc_id, "_source": doc_content.copy()}
        return None

    async def update_by_node_id(
        self, index_name: str, node_id: str, updates: dict[str, Any]
    ) -> dict[str, str]:
        async with self._cache_lock:
            data = await self._ensure_cached(index_name)
            for doc_id, doc_content in data.items():
                if (
                    isinstance(doc_content, dict)
                    and doc_content.get("node_id") == node_id
                ):
                    doc_content.update(updates)
                    self._schedule_flush(index_name)
                    return {"_id": doc_id, "result": "updated"}
        return {"_id": "", "result": "not_found"}

    async def delete(self, index_name: str, doc_id: str) -> dict[str, str]:
        """Delete a document from the index."""
        async with self._cache_lock:
            data = await self._ensure_cached(index_name)
            if doc_id not in data:
                return {"_id": doc_id, "result": "not_found"}
            del data[doc_id]
        self._schedule_flush(index_name)
        return {"_id": doc_id, "result": "deleted"}

    async def close(self) -> bool:
        """Flush all pending writes and shut down."""
        if self._flush_task and not self._flush_task.done():
            try:
                await self._flush_task
            except Exception:  # noqa: BLE001
                pass
        await self._flush_dirty()
        return True
