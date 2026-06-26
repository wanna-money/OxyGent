# LocalEs
---
The position of the class is:

```markdown
[BaseDB](../base_db.md)
├── [BaseES](../db_es/base_es.md)
│   ├── [JesES](../db_es/jes_es.md)
│   ├── [LocalES](../db_es/local_es.md)
│   └── [MemoryEs](../db_es/memory_es.md)
├── [BaseRedis](../db_redis/base_redis.md)
│   ├── [LocalRedis](../db_redis/local_redis.md)
│   └── [JimdbApRedis](../db_redis/jimdb_ap_redis.md)
└── [BaseVectorDB](../db_vector/base_vector_db.md)
    └── [VearchDB](../db_vector/vearch_db.md)
```

---

## Introduction

`LocalEs` is a filesystem-based Elasticsearch implementation that simulates a subset of Elasticsearch functionality by persisting documents as JSON files on the local filesystem. It uses an in-memory write-behind cache for high-performance concurrent writes — mutations are applied to memory instantly and flushed to disk asynchronously. It provides robust cross-platform behavior with UTF-8 persistence, atomic file operations, and data safety features. This implementation is designed for development and testing scenarios where a full Elasticsearch instance is not available.

## Parameters

| Parameter | Type / Allowed value | Default | Description |
| --------- | -------------------- | ------- | ----------- |
| `data_dir` | `str` | `local_es_data` | Directory path for storing JSON files |
| `_cache` | `dict[str, dict]` | `{}` | In-memory cache mapping index names to their document data |
| `_cache_lock` | `asyncio.Lock` | - | Lock protecting cache reads and writes |
| `_flush_interval` | `float` | `0.5` | Interval in seconds between background disk flushes |

## Methods

| Method | Coroutine (async) | Return Value | Purpose |
| ------ | ----------------- | ------------ | ------- |
| `create_index()` | Yes | `dict[str, bool]` | Create a new index with specified configuration |
| `index()` | Yes | `dict[str, str]` | Index a document in the filesystem |
| `update()` | Yes | `dict[str, str]` | Update an existing document |
| `upsert()` | Yes | `dict[str, str]` | Update or create a document (merge semantics) |
| `search()` | Yes | `dict` | Execute a search query with basic filtering and sorting |
| `exists()` | Yes | `bool` | Check if a document exists in the specified index |
| `close()` | Yes | `bool` | Flush all pending writes to disk and shut down |
| `insert()` | Yes | `dict[str, str]` | Internal method to insert or update documents with atomic operations |
| `get_by_node_id()` | Yes | `Optional[dict]` | Get a document by node_id |
| `update_by_node_id()` | Yes | `dict[str, str]` | Update a document by node_id |
| `_index_path()` | No | `str` | Get the file path for an index |
| `_mapping_path()` | No | `str` | Get the file path for index mapping |
| `_write_json_atomic()` | Yes | `None` | Write JSON data to file atomically with UTF-8 encoding |
| `_read_json_safe()` | Yes | `Optional[dict]` | Read JSON file safely with encoding fallback |
| `_build_docs()` | No | `list[dict]` | Static method to build document list from data dictionary |
| `_filter_docs()` | No | `list[dict]` | Filter documents based on query conditions |
| `_sort_docs()` | No | `list[dict]` | Static method to sort documents based on sort specifications |
| `_match_single_condition()` | No | `bool` | Check if a document matches a single query condition |
| `_ensure_cached()` | Yes | `dict` | Load an index into memory cache on first access |
| `_schedule_flush()` | No | `None` | Mark index as dirty and ensure flush loop is running |
| `_flush_dirty()` | Yes | `None` | Flush all dirty indices to disk |


## Inherited

Please refer to the [BaseEs](./base_es.md) class for inherited abstract method definitions and the [BaseDB](../base_db.md) class for retry functionality and error handling.

 
