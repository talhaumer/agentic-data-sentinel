"""Agent workflow endpoints."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Dataset, Run
from app.schemas import (
    AgentWorkflowRequest,
    AgentWorkflowResponse,
    LLMExplanationRequest,
    LLMExplanationResponse,
)
from app.services.agent_service_simple import SimpleAgentService
from app.services.llm_service import LLMService

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/workflow", response_model=AgentWorkflowResponse)
async def trigger_workflow(
    request: AgentWorkflowRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Trigger agent workflow for a dataset."""
    try:
        # Verify dataset exists
        dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # Create a new run
        run = Run(dataset_id=request.dataset_id, status="pending")
        db.add(run)
        db.commit()
        db.refresh(run)

        # Run agent workflow synchronously
        agent_service = SimpleAgentService()
        try:
            result = await agent_service.run_workflow(
                run.id, request.include_llm_explanation
            )
            run.status = "completed"
            run.summary = result.get("summary", {})
            db.commit()
        except Exception as e:
            run.status = "failed"
            run.summary = {"error": str(e)}
            db.commit()
            raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")

        logger.info(
            "Agent workflow triggered", run_id=run.id, dataset_id=request.dataset_id
        )

        return AgentWorkflowResponse(
            run_id=run.id,
            status="completed",
            message="Workflow completed successfully",
            estimated_duration=0,  # Completed immediately
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to trigger workflow", error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to trigger workflow")


@router.post("/explain", response_model=LLMExplanationResponse)
async def explain_anomaly(
    request: LLMExplanationRequest, db: Session = Depends(get_db)
):
    """Get LLM explanation for an anomaly."""
    try:
        # Get anomaly details
        from app.models import Anomaly

        anomaly = db.query(Anomaly).filter(Anomaly.id == request.anomaly_id).first()
        if not anomaly:
            raise HTTPException(status_code=404, detail="Anomaly not found")

        # Get LLM explanation
        llm_service = LLMService()
        explanation = await llm_service.explain_anomaly(anomaly, request.context)

        # Update anomaly with explanation
        anomaly.llm_explanation = explanation.explanation
        anomaly.suggested_sql = explanation.suggested_sql
        db.commit()

        logger.info("LLM explanation generated", anomaly_id=request.anomaly_id)
        return explanation

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate explanation", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate explanation")


@router.get("/workflow/{run_id}/status")
async def get_workflow_status(run_id: int, db: Session = Depends(get_db)):
    """Get the status of a running workflow."""
    try:
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")

        return {
            "run_id": run.id,
            "status": run.status,
            "duration_seconds": run.duration_seconds,
            "summary": run.summary,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get workflow status", run_id=run_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get workflow status")
