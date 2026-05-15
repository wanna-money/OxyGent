## Rating Creation and Management

### 1. Create a Rating (with Comment)

Create or update a conversation rating, with support for attaching a comment.

**API Information**
- **Path**: `POST /rating`
- **Description**: Create a rating record for a specified conversation, which can include a like/dislike type and an optional text comment

**Request Parameters**

```json
{
  "trace_id": "string",        // Required, conversation trace ID
  "rating_type": "like|dislike", // Required, rating type: like or dislike
  "comment": "string",         // Optional, comment content
  "erp": "string"              // Optional, ERP system identifier
}
```

**Request Example**

```bash
curl -X POST "http://localhost:8000/rating" \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "abc123",
    "rating_type": "like",
    "comment": "The answer was very accurate and solved my problem!"
  }'
```

**Response Example**

```json
{
  "code": 200,
  "message": "Rating successful",
  "data": {
    "rating_id": "uuid-xxx-xxx",
    "stats": {
      "trace_id": "abc123",
      "like_count": 5,
      "dislike_count": 1,
      "total_ratings": 6,
      "satisfaction_rate": 83.33,
      "last_updated": "2025-12-29 10:30:45.123456"
    }
  }
}
```

**Field Descriptions**
- `rating_id`: The ID of the newly created rating record
- `stats`: Updated statistics
  - `like_count`: Total number of likes
  - `dislike_count`: Total number of dislikes
  - `total_ratings`: Total number of ratings
  - `satisfaction_rate`: Satisfaction rate (proportion of likes)
  - `last_updated`: Last updated time

---

### 2. Delete a Rating

Delete a specified rating record (admin function).

**API Information**
- **Path**: `DELETE /rating/{rating_id}`
- **Description**: Delete a rating record by rating_id and recalculate statistics

**Path Parameters**
- `rating_id`: Rating record ID

**Request Example**

```bash
curl -X DELETE "http://localhost:8000/rating/uuid-xxx-xxx"
```

**Response Example**

```json
{
  "code": 200,
  "message": "Rating deleted successfully",
  "data": {
    "deleted": true,
    "rating_id": "uuid-xxx-xxx"
  }
}
```

---

## Rating Queries

### 3. Get Rating Statistics

Get rating statistics for a specified conversation.

**API Information**
- **Path**: `GET /rating/{trace_id}`
- **Description**: Query the aggregated rating statistics for a conversation

**Path Parameters**
- `trace_id`: Conversation trace ID

**Request Example**

```bash
curl "http://localhost:8000/rating/abc123"
```

**Response Example**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "trace_id": "abc123",
    "like_count": 5,
    "dislike_count": 1,
    "total_ratings": 6,
    "satisfaction_rate": 83.33,
    "last_updated": "2025-12-29 10:30:45.123456"
  }
}
```

---

### 4. Get Current Rating

Get the most recent rating record for a conversation.

**API Information**
- **Path**: `GET /rating/{trace_id}/current`
- **Description**: Return the most recent rating record for a specified conversation (by creation time)

**Path Parameters**
- `trace_id`: Conversation trace ID

**Query Parameters**
- `erp`: (Optional) ERP system identifier, used to filter ratings for a specific ERP

**Request Example**

```bash
curl "http://localhost:8000/rating/abc123/current?erp=system1"
```

**Response Example**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "trace_id": "abc123",
    "current_rating": {
      "rating_id": "uuid-xxx-xxx",
      "trace_id": "abc123",
      "rating_type": "like",
      "user_id": null,
      "user_ip": "192.168.1.100",
      "comment": "The answer was very accurate and solved my problem!",
      "erp": "system1",
      "create_time": "2025-12-29 10:30:45.123456",
      "update_time": null
    }
  }
}
```
---

## Error Code Descriptions

| Error Code | Description |
|-----------|-------------|
| 200 | Success |
| 400 | Invalid request parameters or operation failure |
| 404 | Resource not found |
| 500 | Internal server error |

---

## Notes

1. **Comment length limit**: It is recommended that comment content does not exceed 1000 characters
2. **Multiple ratings**: The same conversation can be rated multiple times; the system retains all historical records
3. **Comment is optional**: The `comment` field is optional; you can rate without leaving a comment
4. **Real-time statistics**: Rating statistics are updated immediately after a rating is created or deleted
5. **Index refresh**: The system automatically refreshes indexes to ensure data is immediately queryable
6. **ERP integration**: Use the `erp` field to distinguish ratings from different users
