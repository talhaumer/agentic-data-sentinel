# 🚀 Deploy to Vercel - Step by Step

## Quick Deployment (No CLI Required)

### Step 1: Prepare Your Repository
```bash
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

### Step 2: Deploy via Vercel Dashboard

1. **Go to Vercel**: https://vercel.com
2. **Sign up/Login** with your GitHub account
3. **Click "New Project"**
4. **Import from GitHub**:
   - Select your repository: `agentic-data-sentinel`
   - Click "Import"

### Step 3: Configure Project

1. **Project Name**: `data-sentinel-v1` (or your preferred name)
2. **Framework Preset**: Vercel will auto-detect Python
3. **Root Directory**: Leave as `.` (root)
4. **Build Command**: Leave empty (auto-detected)
5. **Output Directory**: Leave empty (auto-detected)

### Step 4: Set Environment Variables

In the Vercel dashboard, go to **Settings → Environment Variables** and add:

```
DATABASE_URL = sqlite:///./data/sentinel.db
LLM_API_KEY = your-openai-api-key-here
LLM_PROVIDER = openai
LLM_MODEL = gpt-3.5-turbo
SECRET_KEY = your-random-secret-key-here
DEBUG = false
VERCEL = 1
VERCEL_ENV = production
```

### Step 5: Deploy

1. **Click "Deploy"**
2. **Wait for build** (2-3 minutes)
3. **Get your URL** (e.g., `https://data-sentinel-v1.vercel.app`)

## Test Your Deployment

Visit these URLs to test:

- **Main App**: `https://your-app.vercel.app/`
- **Health Check**: `https://your-app.vercel.app/health`
- **API Docs**: `https://your-app.vercel.app/docs`

## What Happens During Deployment

1. **Vercel detects** your `vercel.json` configuration
2. **Installs Python** dependencies from `requirements-vercel.txt`
3. **Builds** your FastAPI application
4. **Creates** serverless functions from `api/index.py`
5. **Deploys** to global CDN

## Troubleshooting

### If Build Fails:
- Check the **Build Logs** in Vercel dashboard
- Ensure all dependencies are in `requirements-vercel.txt`
- Verify environment variables are set

### If App Doesn't Work:
- Check **Function Logs** in Vercel dashboard
- Verify your API endpoints are working
- Test locally first with `python api/index.py`

## Success! 🎉

Your Data Sentinel v1 is now live on Vercel!

**Next Steps:**
- Set up a custom domain
- Add monitoring and analytics
- Scale up with more features
- Connect to external databases
