# PowerShell script to build and run Data Sentinel Docker container

Write-Host "🐳 Data Sentinel Docker Setup" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# Build the Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker build -t data-sentinel:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker image built successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Starting Data Sentinel..." -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan
    
    # Run the container
    docker run --name data-sentinel -p 8000:8000 -p 8501:8501 `
        -v "${PWD}/data:/app/data" `
        -v "${PWD}/logs:/app/logs" `
        -e DATABASE_URL=sqlite:////app/data/sentinel.db `
        -e DW_CONN_STRING=sqlite:///./data/dw.db `
        -e LLM_PROVIDER=groq `
        -e LLM_API_KEY=REMOVED `
        -e SECRET_KEY=your-secret-key-change-this-in-production `
        -e DEBUG=True `
        data-sentinel:latest
} else {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}
