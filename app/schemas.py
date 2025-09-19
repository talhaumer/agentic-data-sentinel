"""Pydantic schemas for API request / response models."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    class Config:

# Dataset schemas
class DatasetBase(BaseSchema):
    """Base dataset schema."""

    name: str = Field(..., min_length = 1, max_length = 255)
    owner: Optional[str] = Field(None, max_length = 255)
    source: Optional[str] = Field(None, max_length = 500)

class DatasetCreate(DatasetBase):
    """Schema for creating a new dataset."""

    pass

class DatasetUpdate(BaseSchema):
    """Schema for updating a dataset."""

    name: Optional[str] = Field(None, min_length = 1, max_length = 255)
    owner: Optional[str] = Field(None, max_length = 255)
    source: Optional[str] = Field(None, max_length = 500)
    health_score: Optional[float] = Field(None, ge = 0.0, le = 1.0)

class Dataset(DatasetBase):
    """Schema for dataset response."""

    id: int
    last_ingest: Optional[datetime]
    health_score: float
    created_at: datetime
    updated_at: datetime

class DatasetWithStats(Dataset):
    """Dataset with additional statistics."""

    total_runs: int
    total_anomalies: int
    last_run_status: Optional[str]
    last_anomaly_at: Optional[datetime]

# Run schemas
class RunBase(BaseSchema):
    """Base run schema."""

    dataset_id: int
    status: str = Field(..., pattern="^(pending|running|completed|failed)$")

class RunCreate(RunBase):
    """Schema for creating a new run."""

    pass

class RunUpdate(BaseSchema):
    """Schema for updating a run."""

    status: Optional[str] = Field(None, pattern="^(pending|running|completed|failed)$")
    summary: Optional[Dict[str, Any]]
    duration_seconds: Optional[float]

class Run(RunBase):
    """Schema for run response."""

    id: int
    run_time: datetime
    summary: Optional[Dict[str, Any]]
    duration_seconds: Optional[float]
    created_at: datetime

# Anomaly schemas
class AnomalyBase(BaseSchema):
    """Base anomaly schema."""

    dataset_id: int
    table_name: Optional[str] = Field(None, max_length = 255)
    column_name: Optional[str] = Field(None, max_length = 255)
    issue_type: str = Field(..., max_length = 100)
    severity: int = Field(..., ge = 1, le = 5)
    description: Optional[str] = None
    suggested_sql: Optional[str] = None
    llm_explanation: Optional[str] = None
    action_taken: Optional[str] = Field(None, max_length = 100)
    status: str = Field(
        "open", pattern="^(open|investigating|resolved|ignored|pending_approval)$"
    )
    extra: Optional[Dict[str, Any]] = None

class AnomalyCreate(AnomalyBase):
    """Schema for creating a new anomaly."""

    pass

class AnomalyUpdate(BaseSchema):
    """Schema for updating an anomaly."""

    status: Optional[str] = Field(
        None, pattern="^(open|investigating|resolved|ignored|pending_approval)$"
    )
    action_taken: Optional[str] = Field(None, max_length = 100)
    llm_explanation: Optional[str] = None
    suggested_sql: Optional[str] = None

class Anomaly(AnomalyBase):
    """Schema for anomaly response."""

    id: int
    detected_at: datetime
    created_at: datetime
    updated_at: datetime

# Validation rule schemas
class ValidationRuleBase(BaseSchema):
    """Base validation rule schema."""

    dataset_id: int
    rule_name: str = Field(..., min_length = 1, max_length = 255)
    rule_type: str = Field(..., max_length = 100)
    threshold_value: Optional[float] = None
    is_active: str = Field("true", pattern="^(true|false)$")

class ValidationRuleCreate(ValidationRuleBase):
    """Schema for creating a new validation rule."""

    pass

class ValidationRuleUpdate(BaseSchema):
    """Schema for updating a validation rule."""

    rule_name: Optional[str] = Field(None, min_length = 1, max_length = 255)
    rule_type: Optional[str] = Field(None, max_length = 100)
    threshold_value: Optional[float] = None
    is_active: Optional[str] = Field(None, pattern="^(true|false)$")

class ValidationRule(ValidationRuleBase):
    """Schema for validation rule response."""

    id: int
    created_at: datetime
    updated_at: datetime

# Action log schemas
class ActionLogBase(BaseSchema):
    """Base action log schema."""

    anomaly_id: Optional[int] = None
    action_type: str = Field(..., max_length = 100)
    action_details: Optional[Dict[str, Any]] = None
    status: str = Field(..., pattern="^(success|failed|pending|approved|rejected)$")

class ActionLogCreate(ActionLogBase):
    """Schema for creating a new action log."""

    pass

class ActionLog(ActionLogBase):
    """Schema for action log response."""

    id: int
    executed_at: datetime
    created_at: datetime

# Health and metrics schemas
class HealthCheck(BaseSchema):
    """Health check response schema."""

    status: str
    timestamp: datetime
    version: str
    database: str
    redis: str
    llm: str

class MetricsSummary(BaseSchema):
    """Metrics summary schema."""

    total_datasets: int
    total_runs: int
    total_anomalies: int
    avg_health_score: float
    open_anomalies: int
    resolved_anomalies: int
    last_24h_runs: int
    last_24h_anomalies: int

# LLM and agent schemas
class LLMExplanationRequest(BaseSchema):
    """Request schema for LLM explanation."""

    anomaly_id: int
    context: Optional[Dict[str, Any]] = None

class LLMExplanationResponse(BaseSchema):
    """Response schema for LLM explanation."""

    explanation: str
    confidence: float = Field(..., ge = 0.0, le = 1.0)
    suggested_sql: Optional[str] = None
    action_type: str = Field(
        ..., pattern="^(auto_fix|notify_owner|create_issue|no_action)$"
    )

class AgentWorkflowRequest(BaseSchema):
    """Request schema for triggering agent workflow."""

    dataset_id: int
    force_run: bool = False
    include_llm_explanation: bool = True

class AgentWorkflowResponse(BaseSchema):
    """Response schema for agent workflow."""

    run_id: int
    status: str
    message: str
    estimated_duration: Optional[int] = None  # seconds
