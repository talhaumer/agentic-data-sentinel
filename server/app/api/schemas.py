"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DatasetCreate(BaseModel):
    """Schema for creating a dataset."""
    name: str
    description: Optional[str] = None
    source_type: str
    source_config: str


class DatasetResponse(BaseModel):
    """Schema for dataset response."""
    id: int
    name: str
    description: Optional[str]
    source_type: str
    source_config: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnomalyResponse(BaseModel):
    """Schema for anomaly response."""
    id: int
    anomaly_type: str
    severity: int
    description: str
    confidence: Optional[int]
    detected_at: datetime
    details: Optional[str]
    
    class Config:
        from_attributes = True


class RunResponse(BaseModel):
    """Schema for run response."""
    id: int
    dataset_id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    results: Optional[str]
    anomalies: List[AnomalyResponse] = []
    
    class Config:
        from_attributes = True


class WorkflowRequest(BaseModel):
    """Schema for workflow request."""
    dataset_id: int
    include_llm_explanation: bool = True


class WorkflowResponse(BaseModel):
    """Schema for workflow response."""
    status: str
    run_id: Optional[str] = None
    message: str
    validation_result: Optional[Dict[str, Any]] = None
    explanations: Optional[List[Dict[str, Any]]] = None
    # All agent results
    data_loading_result: Optional[Dict[str, Any]] = None
    remediation_result: Optional[Dict[str, Any]] = None
    notification_result: Optional[Dict[str, Any]] = None
    learning_result: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    agent_status: Optional[Dict[str, Any]] = None
