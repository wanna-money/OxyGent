# Evaluation Schemas

---
The position of the classes is:

```
oxygent/schemas/evaluation.py
```

---

## Introduction

This module defines the data models for the conversation quality evaluation system: ratings, statistics, and API request/response types. These are used by the `EvaluationManager` and the web service evaluation endpoints.

## RatingType (str, Enum)

| Member    | Value       |
| --------- | ----------- |
| `LIKE`    | `"like"`    |
| `DISLIKE` | `"dislike"` |

## ConversationRating (BaseModel)

| Parameter     | Type             | Default    | Description                       |
| ------------- | ---------------- | ---------- | --------------------------------- |
| `rating_id`   | `str`            | (required) | Unique rating record ID.          |
| `trace_id`    | `str`            | (required) | Conversation trace ID.            |
| `rating_type` | `RatingType`     | (required) | Like or dislike.                  |
| `user_id`     | `Optional[str]`  | `None`     | User ID.                          |
| `user_ip`     | `Optional[str]`  | `None`     | User IP address.                  |
| `comment`     | `Optional[str]`  | `None`     | Feedback comment (max 500 chars). |
| `erp`         | `Optional[str]`  | `None`     | ERP system identifier.            |
| `create_time` | `str`            | (required) | Rating creation time.             |
| `update_time` | `Optional[str]`  | `None`     | Rating update time.               |

## RatingRequest (BaseModel)

| Parameter     | Type            | Default    | Description                       |
| ------------- | --------------- | ---------- | --------------------------------- |
| `trace_id`    | `str`           | (required) | Conversation trace ID.            |
| `rating_type` | `RatingType`    | (required) | Rating type.                      |
| `comment`     | `Optional[str]` | `None`     | Rating comment (max 500 chars).   |
| `erp`         | `Optional[str]` | `None`     | ERP system identifier.            |

## RatingStats (BaseModel)

| Parameter           | Type    | Default    | Description              |
| ------------------- | ------- | ---------- | ------------------------ |
| `trace_id`          | `str`   | (required) | Conversation trace ID.   |
| `like_count`        | `int`   | `0`        | Number of likes.         |
| `dislike_count`     | `int`   | `0`        | Number of dislikes.      |
| `total_ratings`     | `int`   | `0`        | Total number of ratings. |
| `satisfaction_rate`  | `float` | `0.0`      | Like percentage.         |
| `last_updated`      | `str`   | (required) | Last update time.        |

## ConversationWithRating (BaseModel)

| Parameter        | Type                              | Default    | Description                          |
| ---------------- | --------------------------------- | ---------- | ------------------------------------ |
| `trace_id`       | `str`                             | (required) | Conversation trace ID.               |
| `input`          | `str`                             | (required) | User input.                          |
| `callee`         | `str`                             | (required) | Called agent.                        |
| `output`         | `str`                             | (required) | Output result.                       |
| `create_time`    | `str`                             | (required) | Creation time.                       |
| `from_trace_id`  | `Optional[str]`                   | `None`     | Source conversation ID.              |
| `rating_stats`   | `Optional[RatingStats]`           | `None`     | Aggregated rating statistics.        |
| `rating_history`  | `Optional[list[ConversationRating]]` | `None` | Complete rating history records.     |

## RatingResponse (BaseModel)

| Parameter       | Type                    | Default    | Description                    |
| --------------- | ----------------------- | ---------- | ------------------------------ |
| `success`       | `bool`                  | (required) | Whether operation succeeded.   |
| `rating_id`     | `Optional[str]`         | `None`     | Rating record ID.              |
| `current_stats` | `Optional[RatingStats]` | `None`     | Current rating statistics.     |
| `message`       | `str`                   | `""`       | Response message.              |
