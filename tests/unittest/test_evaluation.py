"""Unit tests for oxygent.schemas.evaluation (Pydantic models)."""

import pytest
from pydantic import ValidationError

from oxygent.schemas.evaluation import (
    ConversationRating,
    ConversationWithRating,
    RatingRequest,
    RatingResponse,
    RatingStats,
    RatingType,
)


# ──────────────────────────────────────────────────────────────────────────────
# RatingType enum
# ──────────────────────────────────────────────────────────────────────────────
def test_rating_type_values():
    assert RatingType.LIKE == "like"
    assert RatingType.DISLIKE == "dislike"


# ──────────────────────────────────────────────────────────────────────────────
# ConversationRating
# ──────────────────────────────────────────────────────────────────────────────
def test_conversation_rating_valid():
    r = ConversationRating(
        rating_id="r1",
        trace_id="t1",
        rating_type=RatingType.LIKE,
        create_time="2024-01-01",
    )
    assert r.rating_id == "r1"
    assert r.rating_type == "like"  # use_enum_values


def test_conversation_rating_missing_required():
    with pytest.raises(ValidationError):
        ConversationRating(rating_id="r1")


def test_conversation_rating_comment_max_length():
    r = ConversationRating(
        rating_id="r1",
        trace_id="t1",
        rating_type=RatingType.LIKE,
        create_time="2024-01-01",
        comment="x" * 500,
    )
    assert len(r.comment) == 500

    with pytest.raises(ValidationError):
        ConversationRating(
            rating_id="r1",
            trace_id="t1",
            rating_type=RatingType.LIKE,
            create_time="2024-01-01",
            comment="x" * 501,
        )


def test_conversation_rating_optional_fields():
    r = ConversationRating(
        rating_id="r1",
        trace_id="t1",
        rating_type=RatingType.DISLIKE,
        create_time="2024-01-01",
        user_id="u1",
        user_ip="1.2.3.4",
        erp="ERP001",
    )
    assert r.user_id == "u1"
    assert r.user_ip == "1.2.3.4"


# ──────────────────────────────────────────────────────────────────────────────
# RatingRequest
# ──────────────────────────────────────────────────────────────────────────────
def test_rating_request_valid():
    req = RatingRequest(
        trace_id="t1",
        rating_type=RatingType.LIKE,
    )
    assert req.trace_id == "t1"
    assert req.rating_type == "like"  # use_enum_values


def test_rating_request_missing_required():
    with pytest.raises(ValidationError):
        RatingRequest(trace_id="t1")


# ──────────────────────────────────────────────────────────────────────────────
# RatingStats
# ──────────────────────────────────────────────────────────────────────────────
def test_rating_stats_defaults():
    stats = RatingStats(trace_id="t1", last_updated="2024-01-01")
    assert stats.like_count == 0
    assert stats.dislike_count == 0
    assert stats.total_ratings == 0
    assert stats.satisfaction_rate == 0.0


# ──────────────────────────────────────────────────────────────────────────────
# ConversationWithRating
# ──────────────────────────────────────────────────────────────────────────────
def test_conversation_with_rating():
    c = ConversationWithRating(
        trace_id="t1",
        input="hello",
        callee="agent1",
        output="world",
        create_time="2024-01-01",
    )
    assert c.rating_stats is None
    assert c.rating_history is None


# ──────────────────────────────────────────────────────────────────────────────
# RatingResponse
# ──────────────────────────────────────────────────────────────────────────────
def test_rating_response():
    resp = RatingResponse(success=True, message="ok")
    assert resp.success is True
    assert resp.rating_id is None
    assert resp.current_stats is None


def test_rating_response_with_stats():
    stats = RatingStats(
        trace_id="t1",
        like_count=5,
        dislike_count=1,
        total_ratings=6,
        satisfaction_rate=0.83,
        last_updated="2024-01-01",
    )
    resp = RatingResponse(
        success=True, rating_id="r1", current_stats=stats, message="rated"
    )
    assert resp.current_stats.like_count == 5
