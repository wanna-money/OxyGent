# LocalEs
---
类在继承体系中的位置：

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

## 简介

`LocalEs` 是基于文件系统的 Elasticsearch 实现，通过将文档以 JSON 文件形式持久化到本地文件系统来模拟部分 Elasticsearch 功能。它提供了健壮的跨平台行为，支持 UTF-8 持久化、原子文件操作和数据安全特性。该实现适用于无法使用完整 Elasticsearch 实例的开发和测试场景。

## 参数

| 参数 | 类型 / 允许值 | 默认值 | 描述 |
| --------- | -------------------- | ------- | ----------- |
| `data_dir` | `str` | `local_es_data` | 存储 JSON 文件的目录路径 |
| `_locks` | `dict[str, asyncio.Lock]` | `{}` | 用于线程安全索引操作的锁字典 |

## 方法

| 方法 | 协程 (async) | 返回值 | 用途 |
| ------ | ----------------- | ------------ | ------- |
| `create_index()` | 是 | `dict[str, bool]` | 使用指定配置创建新索引 |
| `index()` | 是 | `dict[str, str]` | 在文件系统中索引文档 |
| `update()` | 是 | `dict[str, str]` | 更新已有文档 |
| `search()` | 是 | `dict` | 执行带有基本过滤和排序功能的搜索查询 |
| `exists()` | 是 | `bool` | 检查指定索引中是否存在某文档 |
| `close()` | 是 | `bool` | 关闭本地 ES 客户端（空操作，返回 True） |
| `insert()` | 是 | `dict[str, str]` | 内部方法，通过原子操作插入或更新文档 |
| `find_node_safe()` | 是 | `Optional[dict]` | 通过 node_id 查找节点，并验证 trace_id |
| `get_by_node_id()` | 是 | `Optional[dict]` | 通过 node_id 获取文档 |
| `update_by_node_id()` | 是 | `dict[str, str]` | 通过 node_id 更新文档 |
| `_index_path()` | 否 | `str` | 获取索引的文件路径 |
| `_mapping_path()` | 否 | `str` | 获取索引映射的文件路径 |
| `_write_json_atomic()` | 是 | `None` | 以 UTF-8 编码原子写入 JSON 数据到文件 |
| `_read_json_safe()` | 是 | `Optional[dict]` | 安全读取 JSON 文件，支持编码回退 |
| `_build_docs()` | 否 | `list[dict]` | 静态方法，从数据字典构建文档列表 |
| `_filter_docs()` | 否 | `list[dict]` | 根据查询条件过滤文档 |
| `_sort_docs()` | 否 | `list[dict]` | 静态方法，根据排序规则对文档排序 |
| `_match_single_condition()` | 否 | `bool` | 检查文档是否匹配单个查询条件 |


## 继承

请参阅 [BaseEs](./base_es.md) 类以了解继承的抽象方法定义，以及 [BaseDB](../base_db.md) 类以了解重试功能和错误处理。
