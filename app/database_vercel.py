"""
Database configuration optimized for Vercel serverless environment.
Uses in - memory SQLite for development and external database for production.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Vercel environment detection
IS_VERCEL = os.getenv("VERCEL") == "1"
VERCEL_ENV = os.getenv("VERCEL_ENV", "development")

# Database URL configuration for Vercel
if IS_VERCEL:
    # Production Vercel environment
    if VERCEL_ENV == "production":
        # Use external database (PostgreSQL, PlanetScale, etc.)
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/sentinel.db")
    else:
        # Preview / development - use in - memory database
        DATABASE_URL = "sqlite:///:memory:"
else:
    # Local development
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/sentinel.db")

# Create engine with Vercel optimizations
if IS_VERCEL and VERCEL_ENV != "production":
    # In - memory database for Vercel preview
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    # Production or local database
    engine = create_engine(
        DATABASE_URL, echo = False, pool_pre_ping = True, pool_recycle = 300
    )

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()

def get_db():
    """Get database session for Vercel."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables for Vercel."""
    try:
        # Import models to ensure they're registered
        from app.models import Dataset, Run, Anomaly, ValidationRule, ActionLog  # noqa: F401

        # Create tables
        Base.metadata.create_all(bind = engine)
        return True
    except Exception as e:
        print("Database initialization failed: {e}")
        return False

# Initialize database on import for Vercel
if IS_VERCEL:
    init_db()
