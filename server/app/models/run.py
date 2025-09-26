"""Run model."""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Run(Base):
    """Run model."""
    
    __tablename__ = "runs"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(
        Integer, 
        ForeignKey("datasets.id"), 
        nullable=False
    )
    status = Column(String(50), nullable=False)  # running, completed, failed
    started_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    results = Column(Text)  # JSON results
    
    # Relationships
    dataset = relationship("Dataset", back_populates="runs")
    anomalies = relationship("Anomaly", back_populates="run")


class Anomaly(Base):
    """Anomaly model."""
    
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(
        Integer, 
        ForeignKey("runs.id"), 
        nullable=False
    )
    anomaly_type = Column(String(100), nullable=False)
    severity = Column(Integer, nullable=False)  # 1-5
    description = Column(Text)
    confidence = Column(Integer)  # 0-100
    detected_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    details = Column(Text)  # JSON details
    
    # Relationships
    run = relationship("Run", back_populates="anomalies")
