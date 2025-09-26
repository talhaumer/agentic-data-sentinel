"""API endpoints for Data Sentinel."""

import structlog
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.enhanced_orchestration_agent import EnhancedDataSentinelOrchestrator, WorkflowStrategy
from app.api.schemas import (
    DatasetCreate,
    DatasetResponse,
    RunResponse,
    WorkflowRequest,
    WorkflowResponse
)
from app.core.database import get_db
from app.models import Anomaly, Dataset, Run
from app.utils.json_encoder import custom_jsonable_encoder

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "0.1.0"
    }


@router.post("/datasets", response_model=DatasetResponse)
async def create_dataset(
    dataset: DatasetCreate,
    db: Session = Depends(get_db)
):
    """Create a new dataset."""
    try:
        db_dataset = Dataset(
            name=dataset.name,
            description=dataset.description,
            source_type=dataset.source_type,
            source_config=dataset.source_config
        )
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        
        logger.info(
            "Dataset created", 
            dataset_id=db_dataset.id, 
            name=dataset.name
        )
        return db_dataset
        
    except Exception as e:
        logger.error("Failed to create dataset", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets", response_model=List[DatasetResponse])
async def get_datasets(db: Session = Depends(get_db)):
    """Get all datasets."""
    datasets = db.query(Dataset).filter(Dataset.is_active.is_(True)).all()
    return datasets


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Get a specific dataset."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.post("/workflow", response_model=WorkflowResponse)
async def trigger_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger data quality workflow for a dataset."""
    try:
        # Verify dataset exists
        dataset = db.query(Dataset).filter(
            Dataset.id == request.dataset_id
        ).first()
        if not dataset:
            raise HTTPException(
                status_code=404, 
                detail="Dataset not found"
            )
        
        # Create workflow state
        workflow_state = {
            "dataset_id": request.dataset_id,
            "dataset_name": dataset.name,
            "warehouse_type": dataset.source_type,
            "user_id": "api_user",
            "session_id": f"session_{request.dataset_id}",
            "metadata": {
                "include_llm_explanation": request.include_llm_explanation
            }
        }
        
        # Run enhanced orchestrated workflow
        orchestrator = EnhancedDataSentinelOrchestrator()
        result = await orchestrator.run_workflow(
            dataset_id=request.dataset_id,
            dataset_name=dataset.name,
            strategy=WorkflowStrategy.INTELLIGENT,
            include_llm_explanation=request.include_llm_explanation
        )
        
        logger.info(
            "Workflow completed",
            workflow_id=result.get("workflow_id"),
            dataset_id=request.dataset_id,
            status=result.get("status")
        )
        
        # Extract explanations properly
        anomaly_data = result.get("results", {}).get("anomaly_detection", {}).get("data", {})
        explanations = []
        
        # If anomaly_data is a dict, try to extract explanations
        if isinstance(anomaly_data, dict):
            if "anomalies" in anomaly_data:
                explanations = anomaly_data["anomalies"]
            elif "intelligent_analysis" in anomaly_data:
                explanations = [anomaly_data["intelligent_analysis"]]
            else:
                explanations = [anomaly_data] if anomaly_data else []
        elif isinstance(anomaly_data, list):
            explanations = anomaly_data
        
        # Use custom encoder to handle NumPy types for all results
        validation_result = result.get("results", {}).get("validation", {}).get("data")
        if validation_result is not None:
            validation_result = custom_jsonable_encoder(validation_result)
        
        if explanations:
            explanations = custom_jsonable_encoder(explanations)
        
        # Extract all agent results
        data_loading_result = result.get("results", {}).get("data_loading")
        if data_loading_result:
            data_loading_result = custom_jsonable_encoder(data_loading_result)
        
        remediation_result = result.get("results", {}).get("remediation")
        if remediation_result:
            remediation_result = custom_jsonable_encoder(remediation_result)
        
        notification_result = result.get("results", {}).get("notification")
        if notification_result:
            notification_result = custom_jsonable_encoder(notification_result)
        
        learning_result = result.get("results", {}).get("learning")
        if learning_result:
            learning_result = custom_jsonable_encoder(learning_result)
        
        # Extract performance metrics
        performance_metrics = result.get("performance")
        if performance_metrics:
            performance_metrics = custom_jsonable_encoder(performance_metrics)
        
        # Extract agent status information
        agent_status = {}
        for agent_name, agent_result in result.get("results", {}).items():
            if isinstance(agent_result, dict):
                agent_status[agent_name] = {
                    "status": agent_result.get("status", "unknown"),
                    "confidence": agent_result.get("confidence", 0.0),
                    "execution_time": performance_metrics.get(agent_name, 0.0) if performance_metrics else 0.0
                }
        
        return WorkflowResponse(
            status=result["status"],
            run_id=result.get("workflow_id"),
            message=(
                "Workflow completed successfully" 
                if result["status"] == "completed" 
                else "Workflow failed"
            ),
            validation_result=validation_result,
            explanations=explanations,
            data_loading_result=data_loading_result,
            remediation_result=remediation_result,
            notification_result=notification_result,
            learning_result=learning_result,
            performance_metrics=performance_metrics,
            agent_status=agent_status
        )
        
    except Exception as e:
        logger.error("Workflow failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs", response_model=List[RunResponse])
async def get_runs(db: Session = Depends(get_db)):
    """Get all runs."""
    runs = db.query(Run).order_by(
        Run.started_at.desc()
    ).limit(100).all()
    return runs


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: int, db: Session = Depends(get_db)):
    """Get a specific run."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/anomalies", response_model=List[dict])
async def get_anomalies(db: Session = Depends(get_db)):
    """Get all anomalies."""
    anomalies = db.query(Anomaly).order_by(
        Anomaly.detected_at.desc()
    ).limit(100).all()
    return [
        {
            "id": anomaly.id,
            "run_id": anomaly.run_id,
            "anomaly_type": anomaly.anomaly_type,
            "severity": anomaly.severity,
            "description": anomaly.description,
            "confidence": anomaly.confidence,
            "detected_at": anomaly.detected_at,
            "details": anomaly.details
        }
        for anomaly in anomalies
    ]


@router.get("/agents/status")
async def get_agents_status():
    """Get status of all agents."""
    try:
        orchestrator = EnhancedDataSentinelOrchestrator()
        agent_status = {}
        
        for agent_name, agent in orchestrator.agents.items():
            agent_status[agent_name] = agent.get_stats()
        
        return {
            "agents": agent_status,
            "total_agents": len(agent_status),
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error("Failed to get agent status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows")
async def get_workflows():
    """Get all active workflows."""
    try:
        orchestrator = EnhancedDataSentinelOrchestrator()
        workflows = await orchestrator.get_all_workflows()
        return workflows
    except Exception as e:
        logger.error("Failed to get workflows", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get status of a specific workflow."""
    try:
        orchestrator = EnhancedDataSentinelOrchestrator()
        workflow = await orchestrator.get_workflow_status(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow
    except Exception as e:
        logger.error("Failed to get workflow status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: str):
    """Cancel a running workflow."""
    try:
        orchestrator = EnhancedDataSentinelOrchestrator()
        success = await orchestrator.cancel_workflow(workflow_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return {"message": "Workflow cancelled successfully"}
    except Exception as e:
        logger.error("Failed to cancel workflow", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
