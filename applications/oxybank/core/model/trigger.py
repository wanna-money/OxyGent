"""Trigger system data models for knowledge base automation.

This module defines Pydantic models for the bank trigger system, which enables
automatic HTTP callbacks when knowledge base data meets specified conditions.
"""
from datetime import datetime
from typing import Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class TriggerCondition(BaseModel):
    """Trigger condition for matching knowledge base data.

    Conditions use AND logic - all conditions must be satisfied for trigger to fire.
    """

    field_name: str = Field(..., description="Field name to match (e.g., 'sys_status')")
    field_value: str = Field(..., description="Expected field value")
    operator: Literal["eq", "ne", "contains", "startswith", "endswith"] = Field(
        default="eq",
        description="Comparison operator: eq=equals, ne=not equals, contains=contains substring"
    )


class TriggerHTTPMethod(BaseModel):
    """HTTP method configuration for trigger callback."""

    method: Literal["POST", "PUT", "PATCH"] = Field(
        default="POST",
        description="HTTP method for callback"
    )
    headers: dict[str, str] = Field(
        default_factory=dict,
        description="HTTP headers for authentication (e.g., Authorization, X-API-Key)"
    )


class TriggerConfig(BaseModel):
    """Trigger configuration for knowledge base automation.

    Defines when and how to trigger HTTP callbacks based on knowledge base data changes.
    """

    trigger_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique trigger identifier (auto-generated on create)"
    )
    trigger_name: str = Field(..., description="Human-readable trigger name")
    url: str = Field(..., description="Callback URL endpoint")
    conditions: list[TriggerCondition] = Field(
        ...,
        min_length=1,
        description="List of conditions (AND logic - all must match)"
    )
    http_method: Literal["POST", "PUT", "PATCH"] = Field(
        default="POST",
        description="HTTP method for callback"
    )
    http_headers: dict[str, str] = Field(
        default_factory=dict,
        description="HTTP headers for authentication"
    )
    batch_mode: bool = Field(
        default=False,
        description="If true, pack multiple records into one request"
    )
    batch_size: Optional[int] = Field(
        default=50,
        ge=1,
        le=1000,
        description="Batch size when batch_mode=true (default: 50)"
    )
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="HTTP request timeout in seconds"
    )
    retry_times: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of retry attempts on failure"
    )
    retry_interval: int = Field(
        default=5,
        ge=1,
        le=60,
        description="Seconds between retry attempts"
    )
    enabled: bool = Field(
        default=True,
        description="Whether trigger is active"
    )
    update_data_enabled: bool = Field(
        default=True,
        description="Whether to update original ES data with HTTP response"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("conditions")
    @classmethod
    def validate_conditions(cls, v: list[TriggerCondition]) -> list[TriggerCondition]:
        """Validate conditions list is not empty."""
        if not v:
            raise ValueError("At least one condition is required")
        return v

    @model_validator(mode="after")
    def validate_batch_config(self):
        """Validate batch configuration consistency."""
        if self.batch_mode and not self.batch_size:
            self.batch_size = 50
        return self


class TriggerConfigWrapper(BaseModel):
    """Wrapper for trigger configurations stored in knowledge_base_info.

    This structure is stored in the kb_triggers field of knowledge_base_info index.
    """

    triggers: list[TriggerConfig] = Field(
        default_factory=list,
        description="List of trigger configurations for this knowledge base"
    )


# ==================== Request/Response Models ====================

class TriggerCreateRequest(BaseModel):
    """Request model for creating a new trigger."""

    trigger_name: str = Field(..., description="Human-readable trigger name")
    url: str = Field(..., description="Callback URL endpoint")
    conditions: list[TriggerCondition] = Field(
        ...,
        min_length=1,
        description="List of conditions (AND logic)"
    )
    http_method: Literal["POST", "PUT", "PATCH"] = Field(default="POST")
    http_headers: dict[str, str] = Field(default_factory=dict)
    batch_mode: bool = Field(default=False)
    batch_size: Optional[int] = Field(default=50, ge=1, le=1000)
    timeout: int = Field(default=30, ge=1, le=300)
    retry_times: int = Field(default=3, ge=0, le=10)
    retry_interval: int = Field(default=5, ge=1, le=60)
    enabled: bool = Field(default=True)
    update_data_enabled: bool = Field(default=True)


class TriggerUpdateRequest(BaseModel):
    """Request model for updating an existing trigger.

    All fields are optional - only provided fields will be updated.
    """

    trigger_name: Optional[str] = None
    url: Optional[str] = None
    conditions: Optional[list[TriggerCondition]] = None
    http_method: Optional[Literal["POST", "PUT", "PATCH"]] = None
    http_headers: Optional[dict[str, str]] = None
    batch_mode: Optional[bool] = None
    batch_size: Optional[int] = Field(None, ge=1, le=1000)
    timeout: Optional[int] = Field(None, ge=1, le=300)
    retry_times: Optional[int] = Field(None, ge=0, le=10)
    retry_interval: Optional[int] = Field(None, ge=1, le=60)
    enabled: Optional[bool] = None
    update_data_enabled: Optional[bool] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format if provided."""
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class TriggerResponse(BaseModel):
    """Response model for trigger operations."""

    trigger_id: str
    trigger_name: str
    url: str
    conditions: list[TriggerCondition]
    http_method: Literal["POST", "PUT", "PATCH"]
    http_headers: dict[str, str]
    batch_mode: bool
    batch_size: Optional[int]
    timeout: int
    retry_times: int
    retry_interval: int
    enabled: bool
    update_data_enabled: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ManualTriggerRequest(BaseModel):
    """Request model for manual trigger execution."""

    sample_ids: list[str] = Field(
        ...,
        min_length=1,
        description="List of sample IDs to trigger"
    )
    dry_run: bool = Field(
        default=False,
        description="If true, validate without executing HTTP callback"
    )


# ==================== History Models ====================

class TriggerExecutionStatus(BaseModel):
    """Execution status for trigger history."""

    execution_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique execution identifier"
    )
    kb_id: str = Field(..., description="Knowledge base ID")
    kb_name: str = Field(..., description="Knowledge base name")
    trigger_id: str = Field(..., description="Trigger ID that was executed")
    trigger_name: str = Field(..., description="Trigger name for reference")
    sample_ids: list[str] = Field(
        default_factory=list,
        description="Sample IDs affected by this execution"
    )
    status: Literal["pending", "success", "failed"] = Field(
        default="pending",
        description="Execution status"
    )
    http_status_code: Optional[int] = Field(
        default=None,
        description="HTTP status code from callback"
    )
    response_body: Optional[str] = Field(
        default=None,
        description="Response body from callback (truncated if large)"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if execution failed"
    )
    retry_count: int = Field(
        default=0,
        description="Number of retry attempts made"
    )
    updated_count: int = Field(
        default=0,
        description="Number of records successfully updated from response"
    )
    updated_records: list[dict] = Field(
        default_factory=list,
        description="Updated records from HTTP response (for ES write-back)"
    )
    executed_at: datetime = Field(
        default_factory=datetime.now,
        description="Execution timestamp"
    )


class TriggerHistoryQuery(BaseModel):
    """Query parameters for trigger history."""

    kb_name: Optional[str] = None
    trigger_id: Optional[str] = None
    status: Optional[Literal["pending", "success", "failed"]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class TriggerHistoryResponse(BaseModel):
    """Response model for trigger history query."""

    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Records per page")
    records: list[TriggerExecutionStatus] = Field(..., description="Execution records")
