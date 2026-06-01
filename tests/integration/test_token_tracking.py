"""Integration tests for token usage tracking and aggregation.

Tests cover:
- aggregate_token_usage() accumulates totals in shared_data["_metrics"]
- Per-model breakdown in by_model
- Multiple LLM calls accumulate token counts
- Token tracking disabled via Config skips aggregation
- TokenUsage schema computed fields

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
"""

from oxygent.schemas import OxyRequest
from oxygent.schemas.usage import EstimationMethod, TokenUsage
from oxygent.utils.token_utils import aggregate_token_usage

# ============================================================================
# Tests
# ============================================================================


class TestTokenUsageSchema:
    """Test TokenUsage Pydantic model."""

    def test_total_tokens_computed(self):
        usage = TokenUsage(input_tokens=100, output_tokens=50, model_name="gpt-4")
        assert usage.total_tokens == 150

    def test_default_values(self):
        usage = TokenUsage()
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0
        assert usage.cached_input_tokens == 0
        assert usage.cache_creation_input_tokens == 0
        assert usage.reasoning_tokens == 0
        assert usage.total_tokens == 0
        assert usage.model_name == ""
        assert usage.estimation_method == EstimationMethod.EXACT

    def test_all_fields_populated(self):
        usage = TokenUsage(
            input_tokens=200,
            output_tokens=100,
            cached_input_tokens=50,
            cache_creation_input_tokens=10,
            reasoning_tokens=30,
            model_name="claude-3",
            estimation_method=EstimationMethod.TIKTOKEN,
        )
        assert usage.total_tokens == 300
        assert usage.cached_input_tokens == 50
        assert usage.cache_creation_input_tokens == 10
        assert usage.reasoning_tokens == 30


class TestAggregateTokenUsage:
    """Test aggregate_token_usage function."""

    def test_single_aggregation(self):
        """A single call should initialize and populate _metrics.token_usage."""
        req = OxyRequest(arguments={"query": "test"}, shared_data={})
        usage = TokenUsage(input_tokens=100, output_tokens=50, model_name="gpt-4")

        aggregate_token_usage(req, usage)

        metrics = req.shared_data["_metrics"]["token_usage"]
        assert metrics["total_tokens"] == 150
        assert metrics["input_tokens"] == 100
        assert metrics["output_tokens"] == 50
        assert metrics["request_count"] == 1

    def test_multiple_aggregations(self):
        """Multiple calls should accumulate totals."""
        req = OxyRequest(arguments={"query": "test"}, shared_data={})

        aggregate_token_usage(
            req, TokenUsage(input_tokens=100, output_tokens=50, model_name="gpt-4")
        )
        aggregate_token_usage(
            req, TokenUsage(input_tokens=200, output_tokens=80, model_name="gpt-4")
        )
        aggregate_token_usage(
            req, TokenUsage(input_tokens=50, output_tokens=30, model_name="claude-3")
        )

        metrics = req.shared_data["_metrics"]["token_usage"]
        assert metrics["total_tokens"] == 510
        assert metrics["input_tokens"] == 350
        assert metrics["output_tokens"] == 160
        assert metrics["request_count"] == 3

    def test_per_model_breakdown(self):
        """Token usage should be tracked per model."""
        req = OxyRequest(arguments={"query": "test"}, shared_data={})

        aggregate_token_usage(
            req, TokenUsage(input_tokens=100, output_tokens=50, model_name="gpt-4")
        )
        aggregate_token_usage(
            req, TokenUsage(input_tokens=80, output_tokens=40, model_name="claude-3")
        )
        aggregate_token_usage(
            req, TokenUsage(input_tokens=60, output_tokens=20, model_name="gpt-4")
        )

        by_model = req.shared_data["_metrics"]["token_usage"]["by_model"]

        assert "gpt-4" in by_model
        assert by_model["gpt-4"]["total_tokens"] == 230
        assert by_model["gpt-4"]["request_count"] == 2

        assert "claude-3" in by_model
        assert by_model["claude-3"]["total_tokens"] == 120
        assert by_model["claude-3"]["request_count"] == 1

    def test_cached_and_reasoning_tokens(self):
        """cached_input_tokens, cache_creation_input_tokens, and reasoning_tokens should be tracked."""
        req = OxyRequest(arguments={"query": "test"}, shared_data={})

        aggregate_token_usage(
            req,
            TokenUsage(
                input_tokens=100,
                output_tokens=50,
                cached_input_tokens=30,
                cache_creation_input_tokens=10,
                reasoning_tokens=20,
                model_name="o1",
            ),
        )

        metrics = req.shared_data["_metrics"]["token_usage"]
        assert metrics["cached_input_tokens"] == 30
        assert metrics["cache_creation_input_tokens"] == 10
        assert metrics["reasoning_tokens"] == 20

    def test_empty_model_name_uses_unknown(self):
        """When model_name is empty, it should be tracked as 'unknown'."""
        req = OxyRequest(arguments={"query": "test"}, shared_data={})

        aggregate_token_usage(
            req, TokenUsage(input_tokens=10, output_tokens=5, model_name="")
        )

        by_model = req.shared_data["_metrics"]["token_usage"]["by_model"]
        assert "unknown" in by_model
        assert by_model["unknown"]["total_tokens"] == 15

    def test_disabled_tracking_skips_aggregation(self, monkeypatch):
        """When token tracking is disabled, aggregation should be skipped."""
        monkeypatch.setattr(
            "oxygent.utils.token_utils.Config.get_token_tracking_enabled",
            lambda: False,
        )

        req = OxyRequest(arguments={"query": "test"}, shared_data={})
        aggregate_token_usage(
            req, TokenUsage(input_tokens=100, output_tokens=50, model_name="gpt-4")
        )

        assert (
            "_metrics" not in req.shared_data
            or "token_usage" not in req.shared_data.get("_metrics", {})
        )

    def test_preserves_existing_metrics(self):
        """Aggregation should not overwrite existing _metrics entries."""
        req = OxyRequest(
            arguments={"query": "test"},
            shared_data={"_metrics": {"custom_key": "value"}},
        )

        aggregate_token_usage(
            req, TokenUsage(input_tokens=50, output_tokens=25, model_name="test")
        )

        assert req.shared_data["_metrics"]["custom_key"] == "value"
        assert "token_usage" in req.shared_data["_metrics"]
