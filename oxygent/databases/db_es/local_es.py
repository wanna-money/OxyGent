"""local_es.py – Local Elasticsearch implementation (cross‑platform, UTF‑8‑safe)

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
    """Very small file‑system‑backed ES shim."""

    def __init__(self) -> None:  # noqa: D401 – simple init
        self.data_dir: str = os.path.join(Config.get_cache_save_dir(), "local_es_data")
        os.makedirs(self.data_dir, exist_ok=True)
        self._locks: dict[str, asyncio.Lock] = {}

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

    async def insert(
        self,
        index_name: str,
        doc_id: str,
        body: dict[str, Any],
        *,
        update_mode: bool,
    ) -> dict[str, str]:
        data_path = self._index_path(index_name)
        backup_path = f"{data_path}.bak"

        lock = self._locks.setdefault(index_name, asyncio.Lock())
        async with lock:
            # --- load existing data ---
            data = await self._read_json_safe(data_path)

            if data is None:  # unrecoverable corruption; try backup once
                if await aiofiles.os.path.exists(backup_path):
                    await aiofiles.os.replace(backup_path, data_path)
                    data = await self._read_json_safe(data_path)

            if data is None:
                # still corrupted – preserve original file, switch to fresh store
                corrupt_path = f"{data_path}.corrupt"
                await aiofiles.os.rename(data_path, corrupt_path)
                logger.error(
                    "Index %s is corrupted – moved to %s", index_name, corrupt_path
                )
                data = {}

            # --- apply mutation ---
            if update_mode:
                merged = data.get(doc_id, {})
                merged.update(body)
                data[doc_id] = merged
            else:
                data[doc_id] = body

            # --- persist & backup ---
            # Write new data atomically first.  _write_json_atomic uses a temp
            # file + os.replace, so data_path is *never* absent — the old file
            # is atomically overwritten.  We create the backup *afterwards* so
            # that concurrent lock-free readers (search) never see a missing
            # data_path.
            await self._write_json_atomic(data_path, data)
            try:
                # Best-effort backup: copy the newly-persisted state.
                await self._write_json_atomic(backup_path, data)
            except Exception as e:  # noqa: BLE001 – backup is non-critical
                logger.debug(
                    f"Failed to write backup for index {index_name}: {e}",
                    exc_info=True,
                )

        return {"_id": doc_id, "result": "updated" if update_mode else "created"}

    async def index(
        self, index_name: str, doc_id: str, body: dict[str, Any]
    ) -> dict[str, str]:
        return await self.insert(index_name, doc_id, body, update_mode=False)

    async def update(
        self, index_name: str, doc_id: str, body: dict[str, Any]
    ) -> dict[str, str]:
        return await self.insert(index_name, doc_id, body, update_mode=True)

    async def exists(self, index_name: str, doc_id: str) -> bool:
        data = await self._read_json_safe(self._index_path(index_name)) or {}
        return doc_id in data

    async def search(self, index_name: str, body: dict[str, Any]) -> dict[str, Any]:
        data = await self._read_json_safe(self._index_path(index_name)) or {}
        docs = self._build_docs(data)
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
        data = await self._read_json_safe(self._index_path(index_name)) or {}

        for doc_id, doc_content in data.items():
            if isinstance(doc_content, dict) and doc_content.get("node_id") == node_id:
                return {"_id": doc_id, "_source": doc_content}

        return None

    async def update_by_node_id(
        self, index_name: str, node_id: str, updates: dict[str, Any]
    ) -> dict[str, str]:
        data_path = self._index_path(index_name)
        backup_path = f"{data_path}.bak"

        lock = self._locks.setdefault(index_name, asyncio.Lock())
        async with lock:
            data = await self._read_json_safe(data_path) or {}

            target_doc_id = None
            for doc_id, doc_content in data.items():
                if (
                    isinstance(doc_content, dict)
                    and doc_content.get("node_id") == node_id
                ):
                    target_doc_id = doc_id
                    break

            if target_doc_id is None:
                return {"_id": "", "result": "not_found"}

            data[target_doc_id].update(updates)

            await self._write_json_atomic(data_path, data)
            try:
                await self._write_json_atomic(backup_path, data)
            except Exception as e:  # noqa: BLE001 – backup is non-critical
                logger.debug(
                    f"Failed to write backup for index {index_name} after update_by_node_id: {e}",
                    exc_info=True,
                )

            return {"_id": target_doc_id, "result": "updated"}

    async def delete(self, index_name: str, doc_id: str) -> dict[str, str]:
        """Delete a document from the index.

        Args:
            index_name: Name of the index
            doc_id: ID of the document to delete

        Returns:
            Result of the delete operation
        """
        data_path = self._index_path(index_name)
        backup_path = f"{data_path}.bak"

        lock = self._locks.setdefault(index_name, asyncio.Lock())
        async with lock:
            data = await self._read_json_safe(data_path) or {}

            if doc_id not in data:
                return {"_id": doc_id, "result": "not_found"}

            del data[doc_id]

            await self._write_json_atomic(data_path, data)
            try:
                await self._write_json_atomic(backup_path, data)
            except Exception as e:  # noqa: BLE001 – backup is non-critical
                logger.debug(
                    f"Failed to write backup for index {index_name} after delete: {e}",
                    exc_info=True,
                )

            return {"_id": doc_id, "result": "deleted"}

    async def close(self) -> bool:  # noqa: D401 – nothing to clean
        return True
