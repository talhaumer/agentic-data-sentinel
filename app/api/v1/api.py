"""Main API router for v1 endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import datasets, runs, anomalies, health, agent, external

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(runs.router, prefix="/runs", tags=["runs"])
api_router.include_router(anomalies.router, prefix="/anomalies", tags=["anomalies"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(external.router, prefix="/external", tags=["external"])
