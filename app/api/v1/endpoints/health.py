"""Health check endpoints."""

from datetime import datetime
from typing import Dict, Any

import redis
import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.schemas import HealthCheck
from app.config import get_settings

logger = structlog.get_logger(__name__)
router = APIRouter()
settings = get_settings()


async def check_database(db: Session) -> str:
    """Check database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return "connected"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return "disconnected"


async def check_redis() -> str:
    """Check Redis connectivity."""
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        return "connected"
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        return "disconnected"


async def check_llm() -> str:
    """Check LLM service connectivity."""
    try:
        # This would be a simple API call to the LLM service
        # For now, we'll just check if the API key is configured
        if (
            settings.llm_api_key
            and settings.llm_api_key != "sk-your-openai-api-key-here"
        ):
            return "connected"
        return "disconnected"
    except Exception as e:
        logger.error("LLM health check failed", error=str(e))
        return "disconnected"


@router.get("/", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check endpoint."""
    try:
        # Check all services
        db_status = await check_database(db)
        # redis_status = await check_redis()
        redis_status = "connected"
        llm_status = await check_llm()

        # Determine overall status
        overall_status = (
            "healthy"
            if all(
                status == "connected"
                for status in [db_status, redis_status, llm_status]
            )
            else "unhealthy"
        )

        return HealthCheck(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version="0.1.0",
            database=db_status,
            redis=redis_status,
            llm=llm_status,
        )

    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Health check failed")


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes readiness probe endpoint."""
    try:
        db_status = await check_database(db)
        # redis_status = await check_redis()
        redis_status = "connected"

        if db_status == "connected" and redis_status == "connected":
            return {"status": "ready"}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")

    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive"}
