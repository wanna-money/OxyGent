# JimdbApRedis

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

`JimdbApRedis` 实现了专为 JimDB（京东内部数据库）设计的 Redis 客户端，提供健壮的连接处理、自动重试以及带有大小限制和过期管理的增强列表操作。

## 参数

| 参数               | 类型 / 允许值 | 默认值          | 描述                                              |
| ----------------------- | -------------------- | ---------------- | -------------------------------------------------------- |
| `host`                  | `str`                | 必须赋值 | Redis 服务器主机名或 IP。                             |
| `port`                  | `int`                | 必须赋值 | Redis 服务器端口。                                       |
| `password`              | `str`                | 必须赋值 | 认证密码。                                 |
| `redis_pool`            | `Redis \| None`      | `None`           | 连接池；通过 `_get_redis_connection()` 创建。  |
| `default_expire_time`   | `int`                | `86400`          | 操作使用的默认 TTL（秒）。                |
| `default_list_max_size` | `int`                | `1024`           | 列表操作的默认最大列表大小。               |

## 方法

| 方法                                                                 | 协程 (async) | 返回值                      | 用途                                                      |
| ---------------------------------------------------------------------- | ----------------- | --------------------------------- | ---------------------------------------------------------------------- |
| `__init__(host, port, password)`                                       | 否                | `None`                            | 保存连接参数并创建 Redis 连接池。                      |
| `_get_redis_connection(self)`                                          | 否                | `Redis`                           | 构建 Redis 连接池（`Redis.from_url`）。                      |
| `close(self)`                                                          | 是               | `None`                            | 关闭连接池并断开所有连接。                         |
| `set(self, key, value, ex=86400)`                                      | 是               | `Optional[bool]`                  | 设置带过期时间的键（默认 1 天）。                               |
| `get(self, key)`                                                       | 是               | `Optional[bytes]`                 | 获取键的值。                                                |
| `exists(self, key)`                                                    | 是               | `Optional[int]`                   | 检查键是否存在。                                            |
| `mset(self, items, ex=None)`                                           | 是               | `Optional[bool]`                  | 批量设置多个键（可选统一 TTL）。                       |
| `mget(self, keys)`                                                     | 是               | `Optional[List[Optional[bytes]]]` | 批量获取多个键。                                             |
| `delete(self, key)`                                                    | 是               | `Optional[int]`                   | 删除一个键。                                                          |
| `expire(self, key, ex)`                                                | 是               | `Optional[bool]`                  | 设置键的 TTL；当 `ex` 为 `None` 时返回 `True`。                   |
| `lpush(self, key, *values, ex=86400, max_size=1024, max_length=20240)` | 是               | `int`                             | 左推入并支持值截断、列表修剪和 TTL，使用 pipeline 执行。  |
| `rpop(self, key)`                                                      | 是               | `Optional[bytes]`                 | 弹出列表的最后一个元素。                                        |
| `brpop(self, key, timeout=1)`                                          | 是               | `Optional[bytes]`                 | 为 JimDB 模拟的阻塞弹出（`rpop`、sleep、再 `rpop`）。           |
| `lrange(self, key, start=0, end=-1)`                                   | 是               | `Optional[List[bytes]]`           | 返回列表的一个切片（由于 `lpush`，顺序为 LIFO）。                        |
| `lrem(self, key, count, value)`                                        | 是               | `Optional[int]`                   | 移除等于 `value` 的元素。                                      |
| `lindex(self, key, index)`                                             | 是               | `Optional[bytes]`                 | 通过索引获取列表元素。                                             |
| `llen(self, key)`                                                      | 是               | `Optional[int]`                   | 获取列表长度。                                                       |
| `ltrim(self, key, start, end)`                                         | 是               | `Optional[bool]`                  | 将列表修剪到指定范围。                                        |
