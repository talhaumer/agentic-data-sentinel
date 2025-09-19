# Data Sentinel v1 - Vercel Deployment Script (PowerShell)
Write-Host "🚀 Deploying Data Sentinel v1 to Vercel..." -ForegroundColor Green

# Check if Vercel CLI is installed
try {
    $vercelVersion = vercel --version
    Write-Host "✅ Vercel CLI found: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Red
    npm install -g vercel
}

# Check if user is logged in
try {
    $user = vercel whoami
    Write-Host "✅ Logged in as: $user" -ForegroundColor Green
} catch {
    Write-Host "🔐 Please log in to Vercel:" -ForegroundColor Yellow
    vercel login
}

# Create .vercelignore file
$vercelIgnore = @"
# Data Sentinel v1 - Vercel Ignore
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# Data files
data/
logs/
*.db
*.sqlite
*.sqlite3

# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Documentation
docs/
*.md
!README.md

# Tests
tests/
test_*.py
*_test.py

# Scripts
scripts/
deploy-*.ps1
deploy-*.sh
run_*.py
test_*.py
"@

$vercelIgnore | Out-File -FilePath ".vercelignore" -Encoding UTF8
Write-Host "📝 Created .vercelignore file" -ForegroundColor Blue

# Deploy to Vercel
Write-Host "📦 Deploying to Vercel..." -ForegroundColor Blue
vercel --prod

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🔗 Your Data Sentinel v1 is now live on Vercel!" -ForegroundColor Green
Write-Host "📊 Check your Vercel dashboard for the deployment URL" -ForegroundColor Blue
