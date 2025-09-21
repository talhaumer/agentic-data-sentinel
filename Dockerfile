# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./data/sentinel.db

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data

# Create logs directory
RUN mkdir -p logs

# Expose ports
EXPOSE 8000 8501

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🛡️ Starting Data Sentinel v1"\n\
echo "=================================================="\n\
echo "🚀 Starting FastAPI server on port 8000..."\n\
python -c "import uvicorn; from app.main import app; uvicorn.run(app, host=\"0.0.0.0\", port=8000)" &\n\
echo "📊 Starting Streamlit dashboard on port 8501..."\n\
streamlit run app/frontend/streamlit_main.py --server.port=8501 --server.address=0.0.0.0 &\n\
echo "🎉 Data Sentinel v1 is running!"\n\
echo "=================================================="\n\
echo "📱 Access points:"\n\
echo "   API:          http://localhost:8000"\n\
echo "   Dashboard:    http://localhost:8501"\n\
echo "   API Docs:     http://localhost:8000/docs"\n\
echo "   Health Check: http://localhost:8000/health"\n\
echo "=================================================="\n\
wait' > start.sh && chmod +x start.sh

# Default command
CMD ["./start.sh"]
