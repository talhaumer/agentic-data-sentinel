"""
Simplified FastAPI app for Vercel deployment
Minimal configuration to avoid serverless issues
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create a minimal FastAPI app
app = FastAPI(
    title="Data Sentinel v1",
    description="AI-powered data quality monitoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Data Sentinel v1",
        "platform": "Vercel",
        "version": "1.0.0",
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Data Sentinel v1 - AI-powered data quality monitoring",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1",
    }

# Basic API endpoints
@app.get("/api/v1/health")
async def api_health():
    """API health check."""
    return {"status": "healthy", "api": "v1"}

@app.get("/api/v1/status")
async def api_status():
    """API status."""
    return {"status": "running", "version": "1.0.0"}

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
