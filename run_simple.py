#!/usr/bin/env python3
"""Simple runner for Data Sentinel v1 without Docker/Celery/Redis."""

import os
import sys
import subprocess
import time
from pathlib import Path


def check_requirements():
    """Check if required packages are installed."""
    try:
        import fastapi
        import streamlit
        import sqlalchemy
        import duckdb
        import openai

        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False


def setup_environment():
    """Set up environment variables."""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        with open("env.simple", "r") as f:
            content = f.read()
        with open(".env", "w") as f:
            f.write(content)
        print(
            "⚠️  Please edit .env file with your configuration (especially LLM_API_KEY)"
        )
        print("   Choose between OpenAI or Groq (Groq is faster & cheaper)")
        return False
    return True


def create_directories():
    """Create necessary directories."""
    directories = ["data", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("📁 Created necessary directories")


def generate_sample_data():
    """Generate sample data if it doesn't exist."""
    data_file = Path("data/dw.db")
    if not data_file.exists():
        print("📊 Generating sample data...")
        try:
            subprocess.run(
                [sys.executable, "scripts/generate_sample_data.py"], check=True
            )
            print("✅ Sample data generated")
        except subprocess.CalledProcessError:
            print("❌ Failed to generate sample data")
            raise
    else:
        print("✅ Sample data already exists")
    return True


def start_api():
    """Start the FastAPI server."""
    print("🚀 Starting FastAPI server...")
    try:
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
            ]
        )
        print("✅ FastAPI server started at http://localhost:8000")
        return True
    except Exception as e:
        print(f"❌ Failed to start FastAPI: {e}")
        return False


def start_dashboard():
    """Start the Streamlit dashboard."""
    print("📊 Starting Streamlit dashboard...")
    try:
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app/frontend/streamlit_main.py",
                "--server.port",
                "8501",
                "--server.address",
                "0.0.0.0",
            ]
        )
        print("✅ Streamlit dashboard started at http://localhost:8501")
        return True
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")
        return False


def main():
    """Main function to start Data Sentinel v1."""
    print("🛡️  Data Sentinel v1 - Simple Setup")
    print("=" * 50)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Setup environment
    if not setup_environment():
        sys.exit(1)

    # Create directories
    create_directories()

    # Generate sample data
    if not generate_sample_data():
        sys.exit(1)

    # Start services
    print("\n🚀 Starting services...")

    if not start_api():
        sys.exit(1)

    # Wait a moment for API to start
    time.sleep(2)

    if not start_dashboard():
        sys.exit(1)

    print("\n🎉 Data Sentinel v1 is running!")
    print("=" * 50)
    print("📱 Access points:")
    print("   API:          http://localhost:8000")
    print("   Dashboard:    http://localhost:8501")
    print("   API Docs:     http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    print("\n🔧 To stop: Press Ctrl+C")
    print("=" * 50)

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Data Sentinel...")
        sys.exit(0)


if __name__ == "__main__":
    main()
