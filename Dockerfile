# Data Sentinel - Multi-Agent Data Quality Monitoring System
# Multi-stage Docker build for production deployment

# Stage 1: Base Python environment
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements files
COPY server/requirements.txt ./server/
COPY client/requirements.txt ./client/

# Install server dependencies
RUN pip install --no-cache-dir -r server/requirements.txt

# Install client dependencies
RUN pip install --no-cache-dir -r client/requirements.txt

# Stage 3: Development
FROM dependencies as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    black \
    flake8 \
    mypy

# Copy source code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose ports
EXPOSE 8000 8501

# Development command
CMD ["bash", "-c", "cd server && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload & cd client && streamlit run app.py --server.port 8501 --server.address 0.0.0.0"]

# Stage 4: Production
FROM dependencies as production

# Create non-root user
RUN groupadd -r sentinel && useradd -r -g sentinel sentinel

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs && \
    chown -R sentinel:sentinel /app

# Switch to non-root user
USER sentinel

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Production command
CMD ["bash", "-c", "cd server && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 & cd client && streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"]

