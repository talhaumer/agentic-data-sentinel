"""
Main FastAPI application optimized for Vercel serverless deployment.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.api import api_router
# Removed unused import

# Vercel - specific database import
try:
    from app.database_vercel import init_db
except ImportError:
    def init_db():
        return True

from app.middleware.logging import LoggingMiddleware

# Configure logging for Vercel
logging.basicConfig(level = logging.INFO)
logger = structlog.get_logger(__name__)

# Vercel environment detection
IS_VERCEL = os.getenv("VERCEL") == "1"
VERCEL_ENV = os.getenv("VERCEL_ENV", "development")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for Vercel."""
    # Startup
    logger.info("Starting Data Sentinel v1", platform="Vercel", env = VERCEL_ENV)

    # Initialize database
    if init_db():
        logger.info("Database initialized successfully")
    else:
        logger.warning("Database initialization failed")

    yield

    # Shutdown
    logger.info("Shutting down Data Sentinel v1")

# Create FastAPI app with Vercel optimizations
app = FastAPI(
    title="Data Sentinel v1",
    description="AI - powered data quality monitoring and anomaly detection",
    version="1.0.0",
    docs_url="/docs" if not IS_VERCEL else None,  # Disable docs in production
    redoc_url="/redoc" if not IS_VERCEL else None,
    lifespan = lifespan,
)

# CORS middleware for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        ["*"] if IS_VERCEL else ["http://localhost:3000", "http://localhost:8501"]
    ),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware for Vercel
if IS_VERCEL:
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["*.vercel.app", "vercel.app"]
    )

# Logging middleware
app.add_middleware(LoggingMiddleware)

# Include API router
app.include_router(api_router, prefix="/api / v1")

# Health check endpoint for Vercel
@app.get("/health")
async def health_check():
    """Health check endpoint optimized for Vercel."""
    return {
        "status": "healthy",
        "service": "Data Sentinel v1",
        "platform": "Vercel",
        "environment": VERCEL_ENV,
        "version": "1.0.0",
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "Data Sentinel v1 - AI - powered data quality monitoring",
        "platform": "Vercel",
        "environment": VERCEL_ENV,
        "docs": "/docs" if not IS_VERCEL else "Documentation disabled in production",
        "health": "/health",
        "api": "/api / v1",
    }

# Vercel serverless handler
def handler(request):
    """Vercel serverless handler."""
    return app(request.scope, request.receive, request.send)

# For local development
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port = 8000)
