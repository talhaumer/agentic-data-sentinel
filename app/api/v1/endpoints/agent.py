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

        # Run agent workflow synchronously (service will create its own run record)
        agent_service = SimpleAgentService()
        result = await agent_service.run_workflow(
            request.dataset_id, request.include_llm_explanation
        )

        logger.info(
            "Agent workflow triggered",
            run_id=result.get("run_id"),
            dataset_id=request.dataset_id,
        )

        # Return appropriate response based on result
        if result.get("status") == "completed":
            return AgentWorkflowResponse(
                run_id=result.get("run_id"),
                status="completed",
                message="Workflow completed successfully",
                estimated_duration=result.get("duration_seconds", 0),
            )
        else:
            # Handle failed workflow
            error_msg = result.get("summary", {}).get("error", "Unknown error")
            raise HTTPException(status_code=500, detail=f"Workflow failed: {error_msg}")

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


@router.post("/approve/{anomaly_id}")
async def approve_anomaly_action(
    anomaly_id: int, 
    approved: bool,
    approved_by: str = "human",
    db: Session = Depends(get_db)
):
    """Approve or reject a pending anomaly action."""
    try:
        agent_service = SimpleAgentService()
        result = await agent_service.approve_action(anomaly_id, approved, approved_by)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Approval failed"))
            
    except Exception as e:
        logger.error("Failed to process approval", anomaly_id=anomaly_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process approval")


@router.get("/pending-approvals")
async def get_pending_approvals(db: Session = Depends(get_db)):
    """Get all anomalies pending human approval."""
    try:
        from app.models import Anomaly
        
        pending_anomalies = db.query(Anomaly).filter(
            Anomaly.status == "pending_approval"
        ).all()
        
        approvals = []
        for anomaly in pending_anomalies:
            # Determine suggested action based on severity
            if anomaly.severity >= 4:
                suggested_action = "create_issue"
                priority = "high"
            elif anomaly.severity >= 3:
                suggested_action = "notify_owner"
                priority = "medium"
            elif anomaly.severity >= 2:
                suggested_action = "auto_fix"
                priority = "low"
            else:
                suggested_action = "no_action"
                priority = "low"
            
            approvals.append({
                "anomaly_id": anomaly.id,
                "dataset_id": anomaly.dataset_id,
                "table_name": anomaly.table_name,
                "column_name": anomaly.column_name,
                "issue_type": anomaly.issue_type,
                "severity": anomaly.severity,
                "description": anomaly.description,
                "suggested_action": suggested_action,
                "priority": priority,
                "detected_at": anomaly.detected_at,
                "llm_explanation": anomaly.llm_explanation,
                "suggested_sql": anomaly.suggested_sql
            })
        
        return {
            "pending_approvals": approvals,
            "count": len(approvals)
        }
        
    except Exception as e:
        logger.error("Failed to get pending approvals", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get pending approvals")
