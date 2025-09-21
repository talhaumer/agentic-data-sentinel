"""Dataset management endpoints."""

from typing import List

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Dataset
from app.schemas import (
    Dataset as DatasetSchema,
    DatasetCreate,
    DatasetUpdate,
    DatasetWithStats,
)

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=List[DatasetWithStats])
async def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List all datasets with statistics."""
    try:
        datasets = db.query(Dataset).offset(skip).limit(limit).all()

        # Add statistics for each dataset
        result = []
        for dataset in datasets:
            stats = {
                "total_runs": len(dataset.runs),
                "total_anomalies": len(dataset.anomalies),
                "last_run_status": dataset.runs[-1].status if dataset.runs else None,
                "last_anomaly_at": (
                    max(
                        (anomaly.detected_at for anomaly in dataset.anomalies),
                        default=None,
                    )
                    if dataset.anomalies
                    else None
                ),
            }

            dataset_dict = {**dataset.__dict__, **stats}
            result.append(DatasetWithStats(**dataset_dict))

        return result

    except Exception as e:
        logger.error("Failed to list datasets", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list datasets")


@router.get("/{dataset_id}", response_model=DatasetWithStats)
async def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Get a specific dataset by ID."""
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # Add statistics
        stats = {
            "total_runs": len(dataset.runs),
            "total_anomalies": len(dataset.anomalies),
            "last_run_status": dataset.runs[-1].status if dataset.runs else None,
            "last_anomaly_at": (
                max(
                    (anomaly.detected_at for anomaly in dataset.anomalies), default=None
                )
                if dataset.anomalies
                else None
            ),
        }

        dataset_dict = {**dataset.__dict__, **stats}
        return DatasetWithStats(**dataset_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get dataset", dataset_id=dataset_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get dataset")


@router.post("/", response_model=DatasetSchema)
async def create_dataset(dataset: DatasetCreate, db: Session = Depends(get_db)):
    """Create a new dataset."""
    try:
        # Check if dataset with same name already exists
        existing = db.query(Dataset).filter(Dataset.name == dataset.name).first()
        if existing:
            raise HTTPException(
                status_code=400, detail="Dataset with this name already exists"
            )

        # Create new dataset
        db_dataset = Dataset(**dataset.dict())
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)

        logger.info("Dataset created", dataset_id=db_dataset.id, name=dataset.name)
        return db_dataset

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create dataset", error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create dataset")


@router.put("/{dataset_id}", response_model=DatasetSchema)
async def update_dataset(
    dataset_id: int, dataset: DatasetUpdate, db: Session = Depends(get_db)
):
    """Update an existing dataset."""
    try:
        db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not db_dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # Update fields
        update_data = dataset.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_dataset, field, value)

        db.commit()
        db.refresh(db_dataset)

        logger.info("Dataset updated", dataset_id=dataset_id)
        return db_dataset

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update dataset", dataset_id=dataset_id, error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update dataset")


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Delete a dataset."""
    try:
        db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not db_dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        db.delete(db_dataset)
        db.commit()

        logger.info("Dataset deleted", dataset_id=dataset_id)
        return {"message": "Dataset deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete dataset", dataset_id=dataset_id, error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete dataset")
