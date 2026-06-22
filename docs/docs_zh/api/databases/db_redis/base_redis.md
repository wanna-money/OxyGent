# BaseRedis

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

`BaseRedis` 定义了键值数据库服务的抽象基类，继承自 BaseDB 并提供 Redis 操作的接口契约。

## 参数

| 参数       | 类型 / 允许值 | 默认值 | 描述                                                                                 |
| --------------- | -------------------- | ------- | ------------------------------------------------------------------------------------------- |
| *无声明参数* | —                    | —       | `BaseRedis` 未新增字段；它在 `BaseDB` 之上定义了抽象的 Redis 接口。  |

## 方法

| 方法                                                  | 协程 (async) | 返回值           | 用途 |
| ------------------------------------------------------- | ----------------- | ---------------------- | ----------------- |
| `set(self, key: str, value: str, ex: int = None)`       | 是               | 由实现类定义 | 在子类中实现。   |
| `get(self, key: str)`                                   | 是               | 由实现类定义 | 在子类中实现。   |
| `exists(self, key: str)`                                | 是               | 由实现类定义 | 在子类中实现。   |
| `mset(self, items: dict, ex: int = None)`               | 是               | 由实现类定义 | 在子类中实现。   |
| `mget(self, keys: list)`                                | 是               | 由实现类定义 | 在子类中实现。   |
| `close(self)`                                           | 是               | 由实现类定义 | 在子类中实现。   |
| `delete(self, key: str)`                                | 是               | 由实现类定义 | 在子类中实现。   |
| `lpush(self, key: str, *values: list)`                  | 是               | 由实现类定义 | 在子类中实现。   |
| `brpop(self, key: str, timeout: int = 1)`               | 是               | 由实现类定义 | 在子类中实现。   |
| `lrange(self, key: str, start: int = 0, end: int = -1)` | 是               | 由实现类定义 | 在子类中实现。   |
| `expire(self, key: str, ex: int)`                       | 是               | 由实现类定义 | 在子类中实现。   |
| `llen(self, key: str)`                                  | 是               | 由实现类定义 | 在子类中实现。   |
| `ltrim(self, key: str, start: int, end: int)`           | 是               | 由实现类定义 | 在子类中实现。   |

## 继承
请参阅 [BaseDB](../base_db.md) 类以了解继承的参数和方法。
