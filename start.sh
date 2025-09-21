#!/bin/bash

# Render main port
export PORT_INTERNAL=${PORT:-8000}

# Start FastAPI in background
echo "🚀 Starting FastAPI on port $PORT_INTERNAL..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT_INTERNAL &

# Start Streamlit in background (internal port)
echo "📊 Starting Streamlit on port 8501..."
streamlit run app/frontend/streamlit_main.py --server.port=8501 --server.address=0.0.0.0 &

# Start Nginx
echo "🖥️ Starting Nginx reverse proxy..."
nginx -g 'daemon off;'

# Wait for background processes
wait
