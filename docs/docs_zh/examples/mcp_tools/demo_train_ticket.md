# 火车票查询示例

**源文件:** `examples/mcp_tools/demo_train_ticket.py`

## 概述

本示例展示了一个火车票查询智能体，通过中国铁路 12306 API 实时查询列车时刻表和余票信息。智能体使用自定义 `FunctionHub` 工具集封装 12306 API，允许用户用自然语言提问关于中国城市间火车票的问题。智能体自动处理日期解析（如"明天"）、车站代码查询和车票数据解析。

## 前置条件

- 环境变量：`DEFAULT_LLM_API_KEY`、`DEFAULT_LLM_BASE_URL`、`DEFAULT_LLM_MODEL_NAME`
- Python 3.10+
- 已安装 OxyGent 包（`pip install -r requirements.txt`）
- `requests` 库（包含在标准依赖中）
- 能够访问 `https://kyfw.12306.cn` 和 `https://www.12306.cn`（12306 API）的网络
- `function_hubs/train_ticket_tools.py` 模块可导入

## 运行方式

```bash
python -m examples.mcp_tools.demo_train_ticket
```

示例启动 Web 服务，初始查询为："请帮我查询明天从西安到北京的火车票"，并显示中英双语欢迎消息。

## 代码详解

### 组件（`oxy_space`）

| 组件 | 类型 | 角色 |
|---|---|---|
| `default_llm` | `HttpLLM` | 语言模型，温度 0.01，信号量 4 |
| `train_ticket_tools` | `FunctionHub` | 封装 12306 火车票 API 的自定义工具集 |
| `train_ticket_agent` | `ReActAgent` | 使用火车票工具的智能体；`trust_mode=False` |

### FunctionHub 工具

`train_ticket_tools` FunctionHub（定义在 `function_hubs/train_ticket_tools.py` 中）提供三个工具：

1. **`get_stations_of_city(city_names)`**：通过解析 12306 车站数据库查找中文城市名对应的车站代码。接受管道符分隔的城市名（如 `"北京|西安"`）。

2. **`get_tickets(train_date, from_station_code, to_station_code, purpose_codes)`**：查询 12306 API 获取指定日期两个车站之间的可用车票。返回 `Ticket` 对象列表，包含车次、出发/到达时间、耗时、可购买状态，以及所有座位等级的余票/价格信息（商务座、一等座、二等座、软卧/硬卧、软座/硬座、无座）。

3. **`get_current_date()`**：返回上海时区（UTC+8）的当前日期，格式为 `yyyy-MM-dd`。用于解析"明天"、"下周一"等相对日期。

### 智能体配置

```python
oxy.ReActAgent(
    name="train_ticket_agent",
    tools=["train_ticket_tools"],
    trust_mode=False,
    llm_name="default_llm",
)
```

- **`trust_mode=False`**：智能体在执行工具调用前会进行验证和推理，而非盲目执行。
- 智能体未标记 `is_master=True`，作为唯一的智能体会成为默认入口。

### 入口

```python
async def main():
    async with MAS(oxy_space=oxy_space) as mas:
        await mas.start_web_service(
            first_query="...",
            welcome_message="...",
        )
```

`welcome_message` 提供中英双语的使用示例。

## 核心概念

- **FunctionHub**：基于装饰器的系统，将 Python 函数包装为工具。每个用 `@fh.tool()` 装饰的函数成为带有 Pydantic 验证参数的可调用工具。`train_ticket_tools` 模块展示了一个包含数据模型（`StationData`、`Ticket`）的真实 FunctionHub。
- **外部 API 集成**：工具向 12306 API 发起 HTTP 请求，解析复杂的管道符分隔响应格式，并返回结构化的 Pydantic 模型。这展示了 OxyGent 智能体如何与真实 API 交互。
- **相对日期解析**：当用户提到相对日期时，智能体需要先调用 `get_current_date()` 获取当前日期，然后计算目标日期再查询车票。
- **车站代码查询**：智能体必须调用 `get_stations_of_city()` 将城市名解析为车站代码后才能查询车票，因为 12306 API 需要车站代码。
- **`trust_mode=False`**：指示智能体在执行工具调用前进行额外推理，这在工具与外部 API 交互时很有用。

## 预期行为

1. Web 界面打开，显示中英双语欢迎消息和示例查询。
2. 用户询问火车票信息（如"明天从西安到北京的火车票"）。
3. 智能体调用 `get_current_date()` 将"明天"解析为具体日期。
4. 智能体调用 `get_stations_of_city("西安|北京")` 获取车站代码。
5. 智能体使用解析后的日期和车站代码调用 `get_tickets()`。
6. 12306 API 返回原始车票数据，被解析为结构化的 `Ticket` 对象。
7. 智能体将结果格式化为易读的响应，显示可用列车、时间、耗时和余票信息。
