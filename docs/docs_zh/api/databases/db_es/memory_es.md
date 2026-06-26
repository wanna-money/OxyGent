# MemoryEs

---
类在继承体系中的位置：

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

## 简介

`MemoryEs` 是一个纯内存的 Elasticsearch 模拟层，使用单例模式。它使用 Python 字典模拟部分 ES API，完全不涉及磁盘 I/O -- 进程退出时数据将丢失。在读写边界处对文档进行深拷贝以确保隔离性。适用于单元测试和短生命周期进程。

## 参数

| 参数   | 类型 / 允许值 | 默认值 | 描述                                            |
| ----------- | -------------------- | ------- | ------------------------------------------------------ |
| `_indices`  | `dict`               | `{}`    | 将 `index_name` 映射到 `{doc_id: doc_body}`。             |
| `_mappings` | `dict`               | `{}`    | 将 `index_name` 映射到 mapping 定义。                     |

## 方法

| 方法                                    | 协程 (async) | 返回值         | 用途                                                        |
| ----------------------------------------- | ----------------- | -------------------- | ------------------------------------------------------------------------ |
| `create_index(index_name, body)`          | 是               | `dict`               | 创建带有 mapping 的索引；返回 `{"acknowledged": True}`。          |
| `index(index_name, doc_id, body)`         | 是               | `dict`               | 存储文档（深拷贝）；返回 `{"_id": doc_id, "result": "created"}`。 |
| `update(index_name, doc_id, body)`        | 是               | `dict`               | 将更新合并到已有文档中。                                    |
| `upsert(index_name, doc_id, body)` | 是 | `dict` | 更新或创建文档（合并语义）。 |
| `exists(index_name, doc_id)`              | 是               | `bool`               | 检查索引中是否存在某文档。                            |
| `search(index_name, body)`               | 是               | `dict`               | 过滤、排序，应用 `_source` 过滤；返回 ES 格式的命中结果。         |
| `delete(index_name, doc_id)`              | 是               | `dict`               | 删除文档；返回 `"deleted"` 或 `"not_found"`。                 |
| `close()`                                 | 是               | `bool`               | 空操作；返回 `True`。                                                   |
| `get_by_node_id(index_name, node_id)`     | 是               | `Optional[dict]`     | 扫描所有文档以查找匹配 `node_id` 的文档。                                |
| `update_by_node_id(index_name, node_id, updates)` | 是      | `dict`               | 通过 `node_id` 查找文档并合并更新。                          |

## 继承

请参阅 [BaseES](./base_es.md) 类以了解继承的参数和方法。
