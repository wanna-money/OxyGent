# JesEs
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

`JesEs` 是 BaseEs 抽象类的具体实现，用于 Elasticsearch 数据库操作。它使用支持身份认证的 AsyncElasticsearch 客户端提供完整的 Elasticsearch 功能。该类实现了 BaseEs 中所有必需的抽象方法，并包含用于索引管理和文档操作的额外辅助方法。

## 参数

| 参数 | 类型 / 允许值 | 默认值 | 描述 |
| --------- | -------------------- | ------- | ----------- |
| `hosts` | `str or list` | 必填 | 要连接的 Elasticsearch 主机地址 |
| `user` | `str` | 必填 | 用于身份认证的用户名 |
| `password` | `str` | 必填 | 用于身份认证的密码 |
| `maxsize` | `int` | `200` | 连接池中的最大连接数 |
| `timeout` | `int` | `20` | 请求超时时间（秒） |
| `client` | `AsyncElasticsearch` | `None` | 内部 Elasticsearch 客户端实例 |

## 方法

| 方法 | 协程 (async) | 返回值 | 用途 |
| ------ | ----------------- | ------------ | ------- |
| `create_index()` | 是 | `dict or None` | 使用指定配置创建新索引 |
| `index()` | 是 | `dict` | 在 Elasticsearch 中索引文档 |
| `update()` | 是 | `dict` | 更新已有文档 |
| `search()` | 是 | `dict` | 对索引执行搜索查询 |
| `exists()` | 是 | `bool` | 检查指定索引中是否存在某文档 |
| `close()` | 是 | `None` | 关闭 Elasticsearch 客户端连接 |
| `_index_exists()` | 是 | `bool` | 内部方法，检查索引是否存在 |
| `_create_new_index()` | 是 | `dict` | 内部方法，创建新索引 |

## 继承

请参阅 [BaseEs](./base_es.md) 类以了解继承的抽象方法定义，以及 [BaseDB](../base_db.md) 类以了解重试功能和错误处理。
