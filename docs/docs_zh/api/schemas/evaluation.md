# Evaluation Schemas

---
类所在位置：

```
oxygent/schemas/evaluation.py
```

---

## 简介

本模块定义了对话质量评价系统的数据模型：评分、统计信息以及 API 请求/响应类型。这些模型由 `EvaluationManager` 和 Web 服务评价接口使用。

## RatingType (str, Enum)

| 成员      | 值          |
| --------- | ----------- |
| `LIKE`    | `"like"`    |
| `DISLIKE` | `"dislike"` |

## ConversationRating (BaseModel)

| 参数          | 类型             | 默认值     | 描述                              |
| ------------- | ---------------- | ---------- | --------------------------------- |
| `rating_id`   | `str`            | （必填）   | 唯一的评分记录 ID。              |
| `trace_id`    | `str`            | （必填）   | 对话 trace ID。                  |
| `rating_type` | `RatingType`     | （必填）   | 点赞或点踩。                     |
| `user_id`     | `Optional[str]`  | `None`     | 用户 ID。                        |
| `user_ip`     | `Optional[str]`  | `None`     | 用户 IP 地址。                   |
| `comment`     | `Optional[str]`  | `None`     | 反馈评论（最多 500 字符）。      |
| `erp`         | `Optional[str]`  | `None`     | ERP 系统标识符。                 |
| `create_time` | `str`            | （必填）   | 评分创建时间。                   |
| `update_time` | `Optional[str]`  | `None`     | 评分更新时间。                   |

## RatingRequest (BaseModel)

| 参数          | 类型            | 默认值     | 描述                              |
| ------------- | --------------- | ---------- | --------------------------------- |
| `trace_id`    | `str`           | （必填）   | 对话 trace ID。                  |
| `rating_type` | `RatingType`    | （必填）   | 评分类型。                       |
| `comment`     | `Optional[str]` | `None`     | 评分评论（最多 500 字符）。      |
| `erp`         | `Optional[str]` | `None`     | ERP 系统标识符。                 |

## RatingStats (BaseModel)

| 参数                | 类型    | 默认值     | 描述                     |
| ------------------- | ------- | ---------- | ------------------------ |
| `trace_id`          | `str`   | （必填）   | 对话 trace ID。          |
| `like_count`        | `int`   | `0`        | 点赞数量。               |
| `dislike_count`     | `int`   | `0`        | 点踩数量。               |
| `total_ratings`     | `int`   | `0`        | 评分总数。               |
| `satisfaction_rate`  | `float` | `0.0`      | 点赞率。                 |
| `last_updated`      | `str`   | （必填）   | 最后更新时间。           |

## ConversationWithRating (BaseModel)

| 参数             | 类型                                  | 默认值     | 描述                                 |
| ---------------- | ------------------------------------- | ---------- | ------------------------------------ |
| `trace_id`       | `str`                                 | （必填）   | 对话 trace ID。                      |
| `input`          | `str`                                 | （必填）   | 用户输入。                           |
| `callee`         | `str`                                 | （必填）   | 被调用的 Agent。                     |
| `output`         | `str`                                 | （必填）   | 输出结果。                           |
| `create_time`    | `str`                                 | （必填）   | 创建时间。                           |
| `from_trace_id`  | `Optional[str]`                       | `None`     | 来源对话 ID。                        |
| `rating_stats`   | `Optional[RatingStats]`               | `None`     | 聚合后的评分统计。                   |
| `rating_history`  | `Optional[list[ConversationRating]]` | `None`     | 完整的评分历史记录。                 |

## RatingResponse (BaseModel)

| 参数            | 类型                    | 默认值     | 描述                           |
| --------------- | ----------------------- | ---------- | ------------------------------ |
| `success`       | `bool`                  | （必填）   | 操作是否成功。                 |
| `rating_id`     | `Optional[str]`         | `None`     | 评分记录 ID。                  |
| `current_stats` | `Optional[RatingStats]` | `None`     | 当前评分统计。                 |
| `message`       | `str`                   | `""`       | 响应消息。                     |
