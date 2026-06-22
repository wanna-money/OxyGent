# MemoryEs

---
The position of the class is:

```markdown
[BaseDB](../base_db.md)
├── [BaseES](./base_es.md)
│   ├── [JesES](./jes_es.md)
│   ├── [LocalES](./local_es.md)
│   └── [MemoryEs](./memory_es.md)
├── [BaseRedis](../db_redis/base_redis.md)
│   ├── [LocalRedis](../db_redis/local_redis.md)
│   └── [JimdbApRedis](../db_redis/jimdb_ap_redis.md)
└── [BaseVectorDB](../db_vector/base_vector_db.md)
    └── [VearchDB](../db_vector/vearch_db.md)
```

---

## Introduction

`MemoryEs` is a pure in-memory Elasticsearch shim that uses the singleton pattern. It simulates a subset of ES APIs using Python dicts with zero disk I/O — data is lost when the process exits. It deep-copies documents on read/write boundaries for isolation. Ideal for unit tests and short-lived processes.

## Parameters

| Parameter   | Type / Allowed value | Default | Description                                            |
| ----------- | -------------------- | ------- | ------------------------------------------------------ |
| `_indices`  | `dict`               | `{}`    | Maps `index_name` to `{doc_id: doc_body}`.             |
| `_mappings` | `dict`               | `{}`    | Maps `index_name` to mapping body.                     |

## Methods

| Method                                    | Coroutine (async) | Return Value         | Purpose (concise)                                                        |
| ----------------------------------------- | ----------------- | -------------------- | ------------------------------------------------------------------------ |
| `create_index(index_name, body)`          | Yes               | `dict`               | Create an index with mapping; returns `{"acknowledged": True}`.          |
| `index(index_name, doc_id, body)`         | Yes               | `dict`               | Store a document (deep-copied); returns `{"_id": doc_id, "result": "created"}`. |
| `update(index_name, doc_id, body)`        | Yes               | `dict`               | Merge updates into existing document.                                    |
| `exists(index_name, doc_id)`              | Yes               | `bool`               | Check whether a document exists in the index.                            |
| `search(index_name, body)`               | Yes               | `dict`               | Filter, sort, apply `_source` filtering; returns ES-format hits.         |
| `delete(index_name, doc_id)`              | Yes               | `dict`               | Delete a document; returns `"deleted"` or `"not_found"`.                 |
| `close()`                                 | Yes               | `bool`               | No-op; returns `True`.                                                   |
| `get_by_node_id(index_name, node_id)`     | Yes               | `Optional[dict]`     | Scan all docs for one matching `node_id`.                                |
| `update_by_node_id(index_name, node_id, updates)` | Yes      | `dict`               | Find a document by `node_id` and merge updates.                          |

## Inherited

Please refer to the [BaseES](./base_es.md) class for inherited parameters and methods.
