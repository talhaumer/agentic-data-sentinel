"""
Data Sentinel v1 - Vercel Serverless Entry Point
Optimized for Vercel's serverless environment
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import our main application directly
from app.main import app


# Vercel serverless handler
def handler(request):
    """Vercel serverless handler."""
    return app(request.scope, request.receive, request.send)


# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
