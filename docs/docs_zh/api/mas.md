# MAS
---
类所在位置:

```
oxygent/mas.py
```

---

## 简介

`MAS`（Multi-Agent System，多智能体系统）是 OxyGent 多智能体系统的主类。它提供了一个全面的框架，用于管理多个 Agent、工具、LLM 及其他组件。MAS 负责组件注册、数据库连接、Agent 组织结构管理，并提供 CLI 和 Web 服务两种交互接口。

## 参数

| 参数 | 类型 / 允许值 | 默认值 | 描述 |
| --------- | -------------------- | ------- | ----------- |
| `name` | `str` | `""` | MAS 实例的标识符 |
| `default_oxy_space` | `list` | `[]` | 内置的核心组件，始终存在 |
| `oxy_space` | `list` | `[]` | 待注册的 Oxy 对象初始列表 |
| `oxy_name_to_oxy` | `dict[str, Oxy]` | `{}` | Oxy 名称到 Oxy 实例的映射字典 |
| `master_agent_name` | `str` | `""` | 主 Agent 的名称 |
| `first_query` | `str` | `""` | 前端显示的首条查询 |
| `agent_organization` | `dict` | `[]` | Agent 的组织结构 |
| `vearch_client` | `Optional[VearchDB]` | `None` | 向量数据库客户端 |
| `es_client` | `Optional[AsyncElasticsearch]` | `None` | Elasticsearch 客户端 |
| `redis_client` | `Optional[JimdbApRedis]` | `None` | Redis 客户端 |
| `lock` | `bool` | `False` | 控制任务执行流程 |
| `active_tasks` | `dict` | `{}` | 管理活跃任务的字典 |
| `background_tasks` | `dict` | `{}` | 后台任务字典 |
| `event_dict` | `dict` | `{}` | 事件管理字典 |
| `message_prefix` | `str` | `"oxygent"` | 消息前缀 |
| `global_data` | `dict` | `{}` | 系统级全局数据存储 |

## 方法

| 方法 | 协程 (async) | 返回值 | 用途 |
| ------ | ----------------- | ------------ | ------- |
| `create()` | 是 | `MAS` | 类方法，创建并初始化 MAS 实例 |
| `init()` | 是 | `None` | 使用所有组件和连接初始化 MAS |
| `init_db()` | 是 | `None` | 初始化数据库连接（Elasticsearch、Redis） |
| `init_all_oxy()` | 是 | `None` | 初始化所有已注册的 Oxy 对象 |
| `batch_init_oxy()` | 是 | `None` | 批量初始化指定类型的 Oxy 对象 |
| `create_vearch_table()` | 是 | `None` | 为工具创建 Vearch 表 |
| `cleanup_all()` | 是 | `None` | 优雅地释放所有已注册 Oxy 组件持有的资源 |
| `add_oxy()` | 否 | `None` | 注册单个 Oxy 对象 |
| `add_oxy_list()` | 否 | `None` | 注册一组 Oxy 对象 |
| `call()` | 是 | `Any` | 直接调用一个 Oxy 组件并返回其输出 |
| `chat_with_agent()` | 是 | `OxyResponse` | 将聊天查询转发到 MAS |
| `send_message()` | 是 | `None` | 将消息推送到 Redis 列表以供 SSE 使用 |
| `start_cli_mode()` | 是 | `None` | 启动交互式 CLI 模式 |
| `start_web_service()` | 是 | `None` | 启动 FastAPI + SSE Web 服务 |
| `start_batch_processing()` | 是 | `list` | 并发执行一批查询 |
| `wait_next()` | 是 | `None` | 阻塞执行直到 lock 变为 False |
| `set_oxy_attr()` | 否 | `bool` | 在运行时动态修改组件属性 |
| `show_banner()` | 否 | `None` | 显示 OxyGent 启动横幅 |
| `show_mas_info()` | 否 | `None` | 显示 MAS 初始化信息 |
| `show_org()` | 否 | `None` | 显示组织结构 |
| `init_global_data()` | 否 | `None` | 初始化内存中的全局数据存储 |
| `is_agent()` | 否 | `bool` | 检查某个 Oxy 名称是否为 Agent |
| `init_master_agent_name()` | 否 | `None` | 初始化主 Agent 名称 |
| `init_agent_organization()` | 否 | `None` | 构建 Agent 组织结构 |

## 用法

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="Hello!" 
        )

async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_cli_mode(
            first_query="Hello!" 
        )
```
