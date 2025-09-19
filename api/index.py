"""
Vercel serverless function entry point for Data Sentinel API.
"""

from app.main import app

# Export the FastAPI app for Vercel
handler = app
