"""Anomaly management endpoints."""

from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Anomaly, Dataset
from app.schemas import Anomaly as AnomalySchema, AnomalyCreate, AnomalyUpdate

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.get("/", response_model = List[AnomalySchema])
async def list_anomalies(
    dataset_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    severity_min: Optional[int] = Query(None, ge = 1, le = 5),
    skip: int = Query(0, ge = 0),
    limit: int = Query(100, ge = 1, le = 1000),
    db: Session = Depends(get_db),
):
    """List anomalies with optional filtering."""
    try:
        query = db.query(Anomaly)

        if dataset_id:
            query = query.filter(Anomaly.dataset_id == dataset_id)

        if status:
            query = query.filter(Anomaly.status == status)

        if severity_min:
            query = query.filter(Anomaly.severity >= severity_min)

        anomalies = (
            query.order_by(Anomaly.detected_at.desc()).offset(skip).limit(limit).all()
        )
        return anomalies

    except Exception as e:
        logger.error("Failed to list anomalies", error = str(e))
        raise HTTPException(status_code = 500, detail="Failed to list anomalies")

@router.get("/{anomaly_id}", response_model = AnomalySchema)
async def get_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    """Get a specific anomaly by ID."""
    try:
        anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            raise HTTPException(status_code = 404, detail="Anomaly not found")

        return anomaly

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get anomaly", anomaly_id = anomaly_id, error = str(e))
        raise HTTPException(status_code = 500, detail="Failed to get anomaly")

@router.post("/", response_model = AnomalySchema)
async def create_anomaly(anomaly: AnomalyCreate, db: Session = Depends(get_db)):
    """Create a new anomaly."""
    try:
        # Verify dataset exists
        dataset = db.query(Dataset).filter(Dataset.id == anomaly.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code = 404, detail="Dataset not found")

        # Create new anomaly
        db_anomaly = Anomaly(**anomaly.dict())
        db.add(db_anomaly)
        db.commit()
        db.refresh(db_anomaly)

        logger.info(
            "Anomaly created", anomaly_id = db_anomaly.id, dataset_id = anomaly.dataset_id
        )
        return db_anomaly

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create anomaly", error = str(e))
        db.rollback()
        raise HTTPException(status_code = 500, detail="Failed to create anomaly")

@router.put("/{anomaly_id}", response_model = AnomalySchema)
async def update_anomaly(
    anomaly_id: int, anomaly: AnomalyUpdate, db: Session = Depends(get_db)
):
    """Update an existing anomaly."""
    try:
        db_anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not db_anomaly:
            raise HTTPException(status_code = 404, detail="Anomaly not found")

        # Update fields
        update_data = anomaly.dict(exclude_unset = True)
        for field, value in update_data.items():
            setattr(db_anomaly, field, value)

        db.commit()
        db.refresh(db_anomaly)

        logger.info("Anomaly updated", anomaly_id = anomaly_id)
        return db_anomaly

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update anomaly", anomaly_id = anomaly_id, error = str(e))
        db.rollback()
        raise HTTPException(status_code = 500, detail="Failed to update anomaly")

@router.delete("/{anomaly_id}")
async def delete_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    """Delete an anomaly."""
    try:
        db_anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not db_anomaly:
            raise HTTPException(status_code = 404, detail="Anomaly not found")

        db.delete(db_anomaly)
        db.commit()

        logger.info("Anomaly deleted", anomaly_id = anomaly_id)
        return {"message": "Anomaly deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete anomaly", anomaly_id = anomaly_id, error = str(e))
        db.rollback()
        raise HTTPException(status_code = 500, detail="Failed to delete anomaly")

@router.post("/{anomaly_id}/resolve")
async def resolve_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    """Mark an anomaly as resolved."""
    try:
        db_anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not db_anomaly:
            raise HTTPException(status_code = 404, detail="Anomaly not found")

        db_anomaly.status = "resolved"
        db.commit()

        logger.info("Anomaly resolved", anomaly_id = anomaly_id)
        return {"message": "Anomaly resolved successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to resolve anomaly", anomaly_id = anomaly_id, error = str(e))
        db.rollback()
        raise HTTPException(status_code = 500, detail="Failed to resolve anomaly")
