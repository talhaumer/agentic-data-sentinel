"""Database models for the Data Sentinel application."""

from datetime import datetime
# Removed unused import

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from app.database import Base

class Dataset(Base):
    """Dataset metadata and health tracking."""


    id = Column(Integer, primary_key = True, index = True)
    name = Column(String(255), nullable = False, unique = True, index = True)

    # Relationships
    runs = relationship("Run", back_populates="dataset", cascade="all, delete - orphan")
    anomalies = relationship(
        "Anomaly", back_populates="dataset", cascade="all, delete - orphan"
    )

class Run(Base):
    """Validation run history and results."""


    id = Column(Integer, primary_key = True, index = True)

    # Relationships
    dataset = relationship("Dataset", back_populates="runs")

class Anomaly(Base):
    """Detected data quality issues and anomalies."""


    id = Column(Integer, primary_key = True, index = True)
        String(100), nullable = False
    )  # null_rate, drift, uniqueness, etc.
        String(100), nullable = True
    )  # auto_fix, notify, create_issue, none
        String(50), default="open"
    )  # open, investigating, resolved, ignored

    # Relationships
    dataset = relationship("Dataset", back_populates="anomalies")

class ValidationRule(Base):
    """Data quality validation rules and thresholds."""


    id = Column(Integer, primary_key = True, index = True)
        String(100), nullable = False
    )  # null_rate, uniqueness, range, etc.

    # Relationships
    dataset = relationship("Dataset")

class ActionLog(Base):
    """Audit log for all actions taken by the system."""


    id = Column(Integer, primary_key = True, index = True)

    # Relationships
    anomaly = relationship("Anomaly")
