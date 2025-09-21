"""
Vercel serverless function entry point for Data Sentinel API.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for Vercel
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/sentinel.db")
os.environ.setdefault("LLM_PROVIDER", "groq")
os.environ.setdefault("GROQ_API_KEY", "")
os.environ.setdefault("SECRET_KEY", "")

try:
    from app.main_vercel_simple import app
    # Export the FastAPI app for Vercel
    handler = app
except ImportError:
    try:
        from app.main import app
        handler = app
    except Exception as e:
        # Fallback minimal app if imports fail
        from fastapi import FastAPI
        app = FastAPI(title="Data Sentinel API", version="1.0.0")
        
        @app.get("/")
        async def root():
            return {"message": "Data Sentinel API", "status": "running"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "error": str(e)}
        
        handler = app