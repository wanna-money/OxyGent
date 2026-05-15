# DBFactory
---
The position of the class is:

```
oxygent/db_factory.py
```

---

## Introduction

`DBFactory` is a singleton factory class for database instance management. It ensures only one database instance of a specific class type can be created and maintained throughout the application lifecycle. The factory uses the singleton pattern to provide global access to database instances while preventing multiple instances of the same database type from being created.

## Parameters

| Parameter | Type / Allowed value | Default | Description |
| --------- | -------------------- | ------- | ----------- |
| `_instance` | `object` | `None` | The single database instance maintained by the factory |
| `_created_class` | `class` | `None` | The class type of the created instance |
| `_factory_instance` | `DBFactory` | `None` | The singleton factory instance |

## Methods

| Method | Coroutine (async) | Return Value | Purpose |
| ------ | ----------------- | ------------ | ------- |
| `__new__()` | No | `DBFactory` | Create or return the singleton instance of DBFactory |
| `get_instance()` | No | `object` | Get instance of specified class type, create if not exists |

## Usage

```python
from oxygent.db_factory import DBFactory
from oxygent.databases import LocalEs

factory = DBFactory()
es_client = factory.get_instance(LocalEs)

# Subsequent calls return the same instance
es_client2 = factory.get_instance(LocalEs)
assert es_client is es_client2
```
