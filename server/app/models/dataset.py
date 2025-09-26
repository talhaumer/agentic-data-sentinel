"""Dataset model."""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Dataset(Base):
    """Dataset model."""
    
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    source_type = Column(String(50), nullable=False)  # file, database, api
    source_config = Column(Text)  # JSON config
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now()
    )
    
    # Relationships
    runs = relationship("Run", back_populates="dataset")
