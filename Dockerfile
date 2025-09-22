# Data Sentinel - Agentic AI Data Quality Platform
# Updated with LangGraph agents, external integrations, and observability

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./data/sentinel.db
ENV DW_CONN_STRING=sqlite:///./data/dw.db
ENV STREAMLIT_PORT=8501
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs

# Generate sample data
RUN python scripts/generate_sample_data.py

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🛡️ Data Sentinel v1 - Docker Container"\n\
echo "=================================================="\n\
echo "✅ All required packages are installed"\n\
echo "📁 Created necessary directories"\n\
echo "✅ Sample data generated"\n\
echo "🚀 Starting services..."\n\
echo ""\n\
echo "🚀 Starting FastAPI server on port 8000..."\n\
python -c "import uvicorn; from app.main import app; uvicorn.run(app, host=\"0.0.0.0\", port=8000)" &\n\
FASTAPI_PID=$!\n\
echo "✅ FastAPI server started (PID: $FASTAPI_PID)"\n\
echo ""\n\
echo "📊 Starting Streamlit dashboard on port 8501..."\n\
streamlit run app/frontend/streamlit_main.py --server.port=8501 --server.address=0.0.0.0 &\n\
STREAMLIT_PID=$!\n\
echo "✅ Streamlit dashboard started (PID: $STREAMLIT_PID)"\n\
echo ""\n\
echo "🎉 Data Sentinel v1 is running!"\n\
echo "=================================================="\n\
echo "📱 Access points:"\n\
echo "   API:          http://localhost:8000"\n\
echo "   Dashboard:    http://localhost:8501"\n\
echo "   API Docs:     http://localhost:8000/docs"\n\
echo "   Health Check: http://localhost:8000/health"\n\
echo "   LangGraph Viz: http://localhost:8501 → Agent Workflows → LangGraph Visualization"\n\
echo "=================================================="\n\
echo "🔧 To stop: Press Ctrl+C"\n\
echo "=================================================="\n\
\n\
# Wait for both processes\n\
wait $FASTAPI_PID $STREAMLIT_PID' > start.sh && chmod +x start.sh

# Default command
CMD ["./start.sh"]