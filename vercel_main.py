"""
Data Sentinel v1 - Vercel Serverless Entry Point
Optimized for Vercel's serverless environment
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import our application
from app.main import app as data_sentinel_app

# Create Vercel-optimized FastAPI app
app = FastAPI(
    title="Data Sentinel v1",
    description="AI-powered data quality monitoring and anomaly detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the main application
app.mount("/api", data_sentinel_app)

# Health check endpoint for Vercel
@app.get("/health")
async def health_check():
    """Health check endpoint for Vercel."""
    return {
        "status": "healthy",
        "service": "Data Sentinel v1",
        "platform": "Vercel",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "Data Sentinel v1 - AI-powered data quality monitoring",
        "docs": "/docs",
        "health": "/health",
        "api": "/api"
    }

# Vercel serverless handler
def handler(request):
    """Vercel serverless handler."""
    return app(request.scope, request.receive, request.send)

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
