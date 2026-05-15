# VearchDB

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

`VearchDB` 实现了 Vearch 向量数据库操作的完整接口，提供向量存储、相似性搜索和工具检索功能，支持 embedding 和高级过滤能力。

## 参数

| 参数      | 类型 / 允许值 | 默认值             | 描述                                                                                              |
| -------------- | -------------------- | ------------------- | -------------------------------------------------------------------------------------------------------- |
| `config`       | `VearchConfig`       | 必须赋值    | 从输入 `config` 字典创建的封装配置对象（例如 URL、空间名称、模型 URL）。  |
| `vearch_tools` | `VectorToolAsync`    | `VectorToolAsync()` | 用于 Vearch 底层 HTTP 调用的辅助工具（创建/删除空间、插入、搜索）。                           |
| `emb_func`     | `Callable \| None`   | `None`              | 异步 embedding 函数；当配置中存在 `embedding_model_url` 时设置。                               |

## 方法

| 方法                                                                                                  | 协程 (async) | 返回值     | 用途                                                                                                       |
| ------------------------------------------------------------------------------------------------------- | ----------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `__init__(self, config)`                                                                                | 否                | `None`           | 存储配置、创建 `vearch_tools`，并在提供 embedding URL 时设置 `emb_func`。                                |
| `create_space(self, space_config)`                                                                      | 是               | `Dict[str, Any]` | 通过 master 节点 API 使用指定 schema 创建空间。                                                              |
| `create_tool_df_space(self, tool_space_name)`                                                        | 是               | `Dict[str, Any]` | 创建预定义的"工具数据帧"空间（属性包括 `app_name`、`agent_name`、`tool_name`、`vector` 等）。  |
| `drop_space(self, space_name)`                                                                          | 是               | `str`            | 使用底层辅助工具删除空间；底层 API 返回文本。                                                       |
| `query_search(self, space_name, query, retrieval_nums, fields=[], threshold=None)`                      | 是               | `pd.DataFrame`   | 对文本查询进行 embedding 并执行向量搜索；可选按分数阈值过滤。                                       |
| `query_search_batch(self, space_name, query_list, retrieval_nums, fields=[])`                           | 是               | `pd.DataFrame`   | 语义搜索的批量版本，将所有查询的结果拼接在一起。                                                |
| `check_space_exist(self, space_name)`                                                                   | 是               | `bool`           | 通过获取空间信息并评估响应来检查空间是否存在。                                          |
| `create_vearch_table_by_tool_list(self, tool_list)`                                                     | 是               | `None`           | 系统初始化：对工具描述进行 embedding、确保单一应用、清除旧记录并批量插入新记录。                      |
| `upload_by_df(self, df)`                                                                                | 是               | `str`            | 从 DataFrame 批量插入工具（NDJSON `_bulk`）。                                                    |
| `delete_by_appname(self, app_name)`                                                                     | 是               | `None`           | 通过召回 ID 然后逐个删除来删除某应用的所有文档。                                                     |
| `recall_by_appname(self, app_name)`                                                                     | 是               | `list[str]`      | 返回匹配指定应用名称的所有文档 ID。                                                    |
| `tool_retrieval(self, query, app_name=None, agent_name=None, top_k=5, threshold=0.01, *args, **kwargs)` | 是               | `list[str]`      | 通过混合搜索（向量 + 元数据）并结合分数阈值检索工具名称。                                        |
| `single_mode_insert_by_text(self, body, vector_col, sapce_name)`                                        | 是               | `str`            | 为 `body[vector_col]` 生成 embedding，附加为 `vector`，并插入单条记录。                                |
| `emb_search(self, emb, retrieval_nums, fields)`                                                         | 是               | `pd.DataFrame`   | 使用提供的 embedding 进行直接向量搜索（辅助路径）。                                                          |
| `filter_and_emb_search(self, emb, retrieval_nums, fields, filter={})`                                   | 是               | `pd.DataFrame`   | 向量搜索结合条件过滤；返回 DataFrame 或空 DataFrame。                                       |
| `search_by_filter(self, space_name, filter)`                                                            | 是               | `pd.DataFrame`   | 仅过滤搜索（无向量项）并将结果转换为 DataFrame。                                                |

## 继承

请参阅 [BaseVectorDB](./base_vector_db.md) 类以了解继承的参数和方法，包括重试功能和错误处理。
