#!/bin/bash

echo "🐳 Data Sentinel Docker Setup"
echo "=============================="

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t data-sentinel:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "🚀 Starting Data Sentinel..."
    echo "=============================="
    
    # Run the container
    docker run -p 8000:8000 -p 8501:8501 \
        -v $(pwd)/data:/app/data \
        -v $(pwd)/logs:/app/logs \
        -e DATABASE_URL=sqlite:///./data/sentinel.db \
        -e DW_CONN_STRING=sqlite:///./data/dw.db \
        -e LLM_PROVIDER=groq \
        -e LLM_API_KEY=${LLM_API_KEY} \
        -e SECRET_KEY=${SECRET_KEY} \
        data-sentinel:latest
else
    echo "❌ Docker build failed!"
    exit 1
fi
