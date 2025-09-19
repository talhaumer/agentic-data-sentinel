"""
Data Sentinel v1 - Vercel API Entry Point
Simplified entry point for Vercel serverless functions
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the simplified FastAPI app for Vercel
from app.main_vercel_simple import app

# Export the app for Vercel
handler = app
