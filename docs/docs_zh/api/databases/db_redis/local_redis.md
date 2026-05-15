# LocalRedis

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

`LocalRedis` 实现了键值数据库的内存模拟，为开发和测试环境提供类似 Redis 的功能，无需实际的 Redis 服务器。

## 参数

| 参数               | 类型 / 允许值 | 默认值 | 描述                                          |
| ----------------------- | -------------------- | ------- | ---------------------------------------------------- |
| `data`                  | `Dict[str, deque]`   | `{}`    | 内存存储，将键映射到 deque 以支持列表操作。 |
| `expiry`                | `Dict[str, float]`   | `{}`    | 每个键的过期时间（epoch 秒数），用于自动过期。       |
| `default_expire_time`   | `int`                | `86400` | 默认过期时间（秒）。                      |
| `default_list_max_size` | `int`                | `10`    | 新建 deque 的默认最大列表长度。          |


## 方法

| 方法                                                                | 协程 (async) | 返回值                           | 用途                                                           |
| --------------------------------------------------------------------- | ----------------- | -------------------------------------- | --------------------------------------------------------------------------- |
| `__init__(self)`                                                      | 否                | `None`                                 | 初始化内存数据结构及默认 TTL/限制。                     |
| `lpush(self, key, *values, ex=None, max_size=None, max_length=20240)` | 是               | `int`                                  | 向头部推入值；强制执行 TTL、大小限制和类型/长度处理。 |
| `rpop(self, key)`                                                     | 是               | `str \| bytes \| int \| float \| None` | 检查过期后从尾部弹出元素。                                |
| `_check_expiry(self, key)`                                            | 否                | `None`                                 | 如果键的 TTL 已过期则移除该键。                                        |
| `close(self)`                                                         | 是               | `None`                                 | 在子类中实现                                                              |
