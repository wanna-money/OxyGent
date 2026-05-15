# DBFactory
---
类所在位置:

```
oxygent/db_factory.py
```

---

## 简介

`DBFactory` 是一个用于数据库实例管理的单例工厂类。它确保在整个应用生命周期中，每种数据库类型只能创建和维护一个实例。该工厂使用单例模式提供对数据库实例的全局访问，同时防止同一数据库类型被创建多个实例。

## 参数

| 参数 | 类型 / 允许值 | 默认值 | 描述 |
| --------- | -------------------- | ------- | ----------- |
| `_instance` | `object` | `None` | 工厂维护的唯一数据库实例 |
| `_created_class` | `class` | `None` | 已创建实例的类类型 |
| `_factory_instance` | `DBFactory` | `None` | 单例工厂实例 |

## 方法

| 方法 | 协程 (async) | 返回值 | 用途 |
| ------ | ----------------- | ------------ | ------- |
| `__new__()` | 否 | `DBFactory` | 创建或返回 DBFactory 的单例实例 |
| `get_instance()` | 否 | `object` | 获取指定类类型的实例，若不存在则创建 |

## 用法

```python
from oxygent.db_factory import DBFactory
from oxygent.databases import LocalEs

factory = DBFactory()
es_client = factory.get_instance(LocalEs)

# 后续调用返回同一实例
es_client2 = factory.get_instance(LocalEs)
assert es_client is es_client2
```
