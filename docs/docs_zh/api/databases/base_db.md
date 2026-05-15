# BaseDB
---
类在继承体系中的位置：

```markdown
[BaseDB](./base_db.md)
├── [BaseES](./db_es/base_es.md)
│   ├── [JesES](./db_es/jes_es.md)
│   ├── [LocalES](./db_es/local_es.md)
│   └── [MemoryEs](./db_es/memory_es.md)
├── [BaseRedis](./db_redis/base_redis.md)
│   ├── [LocalRedis](./db_redis/local_redis.md)
│   └── [JimdbApRedis](./db_redis/jimdb_ap_redis.md)
└── [BaseVectorDB](./db_vector/base_vector_db.md)
    └── [VearchDB](./db_vector/vearch_db.md)
```

---

## 简介

`BaseDB` 是数据库服务的基类，提供通用的重试和错误处理功能。该类会自动为其子类的所有公共方法应用重试装饰器，通过可配置的重试策略确保数据库操作的健壮性。它为不同数据库类型实现可靠的数据库连接和操作提供了基础。

## 参数

| 参数 | 类型 / 允许值 | 默认值 | 描述 |
| --------- | -------------------- | ------- | ----------- |
| 无实例参数 | - | - | BaseDB 是一个没有实例参数的基类 |

## 方法

| 方法 | 协程 (async) | 返回值 | 用途 |
| ------ | ----------------- | ------------ | ------- |
| `try_decorator()` | 否 | `Callable` | 静态方法，为数据库操作创建重试装饰器 |
| `__init_subclass__()` | 否 | `None` | 类方法，在子类被创建时自动调用，自动应用重试装饰器 |

## 装饰器参数

| 参数 | 类型 / 允许值 | 默认值 | 描述 |
| --------- | -------------------- | ------- | ----------- |
| `max_retries` | `int` | `1` | 最大重试次数 |
| `delay_between_retries` | `float` | `0.1` | 重试之间的延迟时间（秒） |
