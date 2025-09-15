#!/usr/bin/env python3
"""Simple test script for Data Sentinel v1."""

import os
import sys
import asyncio
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")

    try:
        import fastapi

        print("✅ FastAPI imported")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

    try:
        import streamlit

        print("✅ Streamlit imported")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False

    try:
        import sqlalchemy

        print("✅ SQLAlchemy imported")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False

    try:
        import duckdb

        print("✅ DuckDB imported")
    except ImportError as e:
        print(f"❌ DuckDB import failed: {e}")
        return False

    try:
        import openai

        print("✅ OpenAI imported")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False

    try:
        import groq

        print("✅ Groq imported")
    except ImportError as e:
        print(f"❌ Groq import failed: {e}")
        return False

    try:
        import langchain

        print("✅ LangChain imported")
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False

    return True


def test_config():
    """Test configuration loading."""
    print("\n🔧 Testing configuration...")

    try:
        from app.config import get_settings

        settings = get_settings()
        print(f"✅ Config loaded - LLM Provider: {settings.llm_provider}")
        print(f"✅ Database URL: {settings.database_url}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_database():
    """Test database connection."""
    print("\n🗄️  Testing database...")

    try:
        from app.database import engine, Base
        from app.models import Dataset

        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_llm_service():
    """Test LLM service initialization."""
    print("\n🤖 Testing LLM service...")

    try:
        from app.services.llm_service import LLMService

        service = LLMService()
        print(f"✅ LLM service initialized with {service.settings.llm_provider}")
        return True
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        return False


def test_validation_service():
    """Test validation service."""
    print("\n🔍 Testing validation service...")

    try:
        from app.services.validation_service import ValidationService

        service = ValidationService()
        print("✅ Validation service initialized")
        return True
    except Exception as e:
        print(f"❌ Validation service test failed: {e}")
        return False


def test_agent_service():
    """Test agent service."""
    print("\n🤖 Testing agent service...")

    try:
        from app.services.agent_service_simple import SimpleAgentService

        service = SimpleAgentService()
        print("✅ Agent service initialized")
        return True
    except Exception as e:
        print(f"❌ Agent service test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🛡️  Data Sentinel v1 - Simple Test")
    print("=" * 50)

    tests = [
        test_imports,
        test_config,
        test_database,
        test_llm_service,
        test_validation_service,
        test_agent_service,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! Data Sentinel v1 is ready to run.")
        print("\n🚀 Next steps:")
        print("1. Edit .env file with your API key")
        print("2. Run: python run_simple.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
