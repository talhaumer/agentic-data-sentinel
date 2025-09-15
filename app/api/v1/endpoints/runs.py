"""Validation run management endpoints."""

from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Run, Dataset
from app.schemas import Run as RunSchema, RunCreate, RunUpdate
from fastapi import BackgroundTasks
from app.services.agent_service_simple import SimpleAgentService
import asyncio


logger = structlog.get_logger(__name__)
router = APIRouter()


async def run_agent_sync_wrapper(dataset_id: int):
    """Async wrapper for the agent workflow."""
    agent_service = SimpleAgentService()
    await agent_service.run_workflow(dataset_id)


@router.get("/", response_model=List[RunSchema])
async def list_runs(
    dataset_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List validation runs."""
    try:
        query = db.query(Run)

        if dataset_id:
            query = query.filter(Run.dataset_id == dataset_id)

        runs = query.order_by(Run.run_time.desc()).offset(skip).limit(limit).all()
        return runs

    except Exception as e:
        logger.error("Failed to list runs", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list runs")


@router.get("/{run_id}", response_model=RunSchema)
async def get_run(run_id: int, db: Session = Depends(get_db)):
    """Get a specific run by ID."""
    try:
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")

        return run

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get run", run_id=run_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get run")


@router.post("/", response_model=RunSchema)
async def create_run(
    run: RunCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """Create a new validation run."""
    try:

        # Verify dataset exists
        dataset = db.query(Dataset).filter(Dataset.id == run.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # Create new run
        db_run = Run(**run.dict())
        db.add(db_run)
        db.commit()
        db.refresh(db_run)

        logger.info("Run created", run_id=db_run.id, dataset_id=run.dataset_id)
        # background_tasks.add_task(run_agent_sync_wrapper, db_run.dataset_id)
        agent_service = SimpleAgentService()
        await agent_service.run_workflow(db_run.dataset_id)

        # Refresh to get updated run data
        db.refresh(db_run)
        return db_run

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create run", error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create run")


@router.put("/{run_id}", response_model=RunSchema)
async def update_run(run_id: int, run: RunUpdate, db: Session = Depends(get_db)):
    """Update an existing run."""
    try:
        db_run = db.query(Run).filter(Run.id == run_id).first()
        if not db_run:
            raise HTTPException(status_code=404, detail="Run not found")

        # Update fields
        update_data = run.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_run, field, value)

        db.commit()
        db.refresh(db_run)

        logger.info("Run updated", run_id=run_id)
        return db_run

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update run", run_id=run_id, error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update run")


@router.delete("/{run_id}")
async def delete_run(run_id: int, db: Session = Depends(get_db)):
    """Delete a run."""
    try:
        db_run = db.query(Run).filter(Run.id == run_id).first()
        if not db_run:
            raise HTTPException(status_code=404, detail="Run not found")

        db.delete(db_run)
        db.commit()

        logger.info("Run deleted", run_id=run_id)
        return {"message": "Run deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete run", run_id=run_id, error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete run")
