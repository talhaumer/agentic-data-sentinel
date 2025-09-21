"""External API integration endpoints."""

import structlog
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.external_apis import ExternalAPIManager
from app.schemas import NotificationRequest, IssueRequest

logger = structlog.get_logger(__name__)
router = APIRouter()

# Initialize external API manager
api_manager = ExternalAPIManager()


@router.post("/notify")
async def send_notification(
    request: NotificationRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Send notification via external APIs."""
    try:
        result = await api_manager.send_notification(
            channel=request.channel,
            message=request.message,
            priority=request.priority,
            platform=request.platform
        )
        
        if result.get("success"):
            logger.info("Notification sent successfully", platform=request.platform)
            return {"status": "success", "result": result}
        else:
            logger.error("Failed to send notification", error=result.get("error"))
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except Exception as e:
        logger.error("Notification endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-issue")
async def create_issue(
    request: IssueRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create issue via external APIs."""
    try:
        result = await api_manager.create_issue(
            title=request.title,
            description=request.description,
            priority=request.priority,
            platform=request.platform
        )
        
        if result.get("success"):
            logger.info("Issue created successfully", platform=request.platform)
            return {"status": "success", "result": result}
        else:
            logger.error("Failed to create issue", error=result.get("error"))
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except Exception as e:
        logger.error("Issue creation endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/integrations/status")
async def get_integration_status() -> Dict[str, Any]:
    """Get status of external integrations."""
    try:
        status = {
            "slack": api_manager.slack is not None,
            "jira": api_manager.jira is not None,
            "github": api_manager.github is not None,
            "email": api_manager.email is not None
        }
        
        return {
            "status": "success",
            "integrations": status,
            "available_platforms": {
                "notifications": ["slack", "email"],
                "issues": ["jira", "github"]
            }
        }
        
    except Exception as e:
        logger.error("Failed to get integration status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
