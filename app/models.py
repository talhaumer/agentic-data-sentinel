"""Database models for the Data Sentinel application."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Dataset(Base):
    """Dataset metadata and health tracking."""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    owner = Column(String(255), nullable=True)
    source = Column(String(500), nullable=True)
    last_ingest = Column(DateTime, nullable=True)
    health_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    runs = relationship("Run", back_populates="dataset", cascade="all, delete-orphan")
    anomalies = relationship(
        "Anomaly", back_populates="dataset", cascade="all, delete-orphan"
    )


class Run(Base):
    """Validation run history and results."""

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    run_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), nullable=False)  # pending, running, completed, failed
    summary = Column(JSON, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="runs")


class Anomaly(Base):
    """Detected data quality issues and anomalies."""

    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    table_name = Column(String(255), nullable=True)
    column_name = Column(String(255), nullable=True)
    issue_type = Column(
        String(100), nullable=False
    )  # null_rate, drift, uniqueness, etc.
    severity = Column(Integer, nullable=False)  # 1-5 scale
    detected_at = Column(DateTime, default=datetime.utcnow)
    description = Column(Text, nullable=True)
    suggested_sql = Column(Text, nullable=True)
    llm_explanation = Column(Text, nullable=True)
    action_taken = Column(
        String(100), nullable=True
    )  # auto_fix, notify, create_issue, none
    status = Column(
        String(50), default="open"
    )  # open, investigating, resolved, ignored
    extra = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="anomalies")


class ValidationRule(Base):
    """Data quality validation rules and thresholds."""

    __tablename__ = "validation_rules"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    rule_name = Column(String(255), nullable=False)
    rule_type = Column(
        String(100), nullable=False
    )  # null_rate, uniqueness, range, etc.
    threshold_value = Column(Float, nullable=True)
    is_active = Column(String(10), default="true")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset")


class ActionLog(Base):
    """Audit log for all actions taken by the system."""

    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    anomaly_id = Column(Integer, ForeignKey("anomalies.id"), nullable=True)
    action_type = Column(String(100), nullable=False)  # auto_fix, notify, create_issue
    action_details = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False)  # success, failed, pending
    executed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    anomaly = relationship("Anomaly")
