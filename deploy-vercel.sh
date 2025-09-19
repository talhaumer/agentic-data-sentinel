#!/bin/bash

# Data Sentinel v1 - Vercel Deployment Script
echo "🚀 Deploying Data Sentinel v1 to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please log in to Vercel:"
    vercel login
fi

# Create .vercelignore file
cat > .vercelignore << EOF
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
deploy-*.sh
run_*.py
test_*.py
EOF

# Deploy to Vercel
echo "📦 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo "🔗 Your Data Sentinel v1 is now live on Vercel!"
echo "📊 Check your Vercel dashboard for the deployment URL"
