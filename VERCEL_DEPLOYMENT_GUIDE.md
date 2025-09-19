# 🚀 Vercel Deployment Guide for Data Sentinel v1

## Prerequisites

1. **Node.js and npm** (for Vercel CLI)
   - Download from: https://nodejs.org/
   - Or install via package manager

2. **Vercel Account**
   - Sign up at: https://vercel.com
   - Connect your GitHub account

## Deployment Methods

### Method 1: Vercel Dashboard (Easiest)

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/dashboard
   - Click "New Project"

2. **Import from GitHub**
   - Select your repository: `agentic-data-sentinel`
   - Vercel will auto-detect the configuration

3. **Configure Environment Variables**
   ```
   DATABASE_URL=sqlite:///./data/sentinel.db
   LLM_API_KEY=your-api-key-here
   SECRET_KEY=your-secret-key-here
   DEBUG=false
   VERCEL=1
   VERCEL_ENV=production
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete

### Method 2: Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

### Method 3: GitHub Integration

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Vercel deployment"
   git push origin main
   ```

2. **Connect in Vercel**
   - Go to Vercel Dashboard
   - Import from GitHub
   - Select your repository

## Project Structure for Vercel

```
agentic-data-sentinel/
├── api/
│   └── index.py              # Vercel serverless function
├── app/
│   ├── main_vercel_simple.py # Simplified FastAPI app
│   └── ...
├── vercel.json               # Vercel configuration
├── requirements-vercel.txt   # Python dependencies
├── package.json             # Node.js configuration
└── README.md
```

## Environment Variables

Set these in Vercel Dashboard → Project → Settings → Environment Variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `sqlite:///./data/sentinel.db` | Database connection |
| `LLM_API_KEY` | `your-openai-key` | OpenAI API key |
| `LLM_PROVIDER` | `openai` | LLM provider |
| `LLM_MODEL` | `gpt-3.5-turbo` | LLM model |
| `SECRET_KEY` | `random-secret-key` | App secret |
| `DEBUG` | `false` | Debug mode |
| `VERCEL` | `1` | Vercel environment flag |
| `VERCEL_ENV` | `production` | Environment name |

## Testing Deployment

After deployment, test these endpoints:

- `https://your-app.vercel.app/` - Root endpoint
- `https://your-app.vercel.app/health` - Health check
- `https://your-app.vercel.app/docs` - API documentation

## Troubleshooting

### Common Issues:

1. **Build Failures**
   - Check `requirements-vercel.txt` for missing dependencies
   - Ensure Python version compatibility

2. **Runtime Errors**
   - Check environment variables are set correctly
   - Review Vercel function logs

3. **Import Errors**
   - Verify `PYTHONPATH` is set to "."
   - Check file paths in `api/index.py`

### Debug Commands:

```bash
# Check Vercel CLI
vercel --version

# Test locally
vercel dev

# Check deployment status
vercel ls

# View logs
vercel logs
```

## Next Steps

1. **Set up monitoring** - Add error tracking
2. **Configure domain** - Add custom domain
3. **Set up CI/CD** - Automatic deployments
4. **Add database** - Connect external database
5. **Scale up** - Add more features

## Support

- Vercel Docs: https://vercel.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com/
- Project Issues: Create GitHub issue
