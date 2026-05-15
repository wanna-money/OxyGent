# BaseVectorDB

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

`BaseVectorDB` 定义了向量数据库服务的抽象基类，继承自 BaseDB 并提供向量存储和相似性搜索操作的接口契约。

## 参数

| 参数       | 类型 / 允许值 | 默认值 | 描述                                                                     |
| --------------- | -------------------- | ------- | ------------------------------------------------------------------------------- |
| *无声明参数* | —                    | —       | `BaseVectorDB` 未新增字段；它是 `BaseDB` 之上的抽象接口。  |

## 方法

| 方法                                 | 协程 (async) | 返回值           | 用途 |
| -------------------------------------- | ----------------- | ---------------------- | ----------------- |
| `create_space(self, index_name, body)` | 是               | 由实现类定义 | 在子类中实现。   |
| `query_search(self, index_name, body)` | 是               | 由实现类定义 | 在子类中实现。   |

## 继承

请参阅 [BaseDB](../base_db.md) 类以了解继承的参数和方法，包括重试功能和错误处理。
