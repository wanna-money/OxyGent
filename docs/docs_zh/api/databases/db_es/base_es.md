# BaseEs
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

`BaseEs` 是 Elasticsearch 数据库服务的抽象基类。它继承自 BaseDB 以获得重试功能和错误处理能力，同时定义了所有 Elasticsearch 实现必须提供的基本接口。所有方法均为抽象方法，必须由子类实现以提供具体的 Elasticsearch 功能。

## 参数

| 参数 | 类型 / 允许值 | 默认值 | 描述 |
| --------- | -------------------- | ------- | ----------- |
| 无实例参数 | - | - | BaseEs 是一个没有实例参数的抽象基类 |

## 方法

| 方法 | 协程 (async) | 返回值 | 用途 |
| ------ | ----------------- | ------------ | ------- |
| `create_index()` | 是 | `Any` | 抽象方法，使用指定配置创建新索引 |
| `index()` | 是 | `Any` | 抽象方法，在 Elasticsearch 中索引文档 |
| `update()` | 是 | `Any` | 抽象方法，更新已有文档 |
| `search()` | 是 | `Any` | 抽象方法，对索引执行搜索查询 |
| `exists()` | 是 | `bool` | 抽象方法，检查指定索引中是否存在某文档 |
| `close()` | 是 | `None` | 抽象方法，关闭 Elasticsearch 客户端连接 |

## 继承

请参阅 [BaseDB](../base_db.md) 类以了解继承的参数和方法，包括重试功能和错误处理。

## 用法

```python
Config.set_es_config( 
    {
        "hosts": ["${PROD_ES_HOST_1}", "${PROD_ES_HOST_2}", "${PROD_ES_HOST_3}"],
        "user": "${PROD_ES_USER}",
        "password": "${PROD_ES_PASSWORD}",
    }
)
```
