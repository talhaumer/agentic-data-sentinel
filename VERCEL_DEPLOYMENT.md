# 🚀 Data Sentinel v1 - Vercel Deployment Guide

Deploy your AI-powered data quality monitoring system to Vercel's serverless platform.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Node.js**: Install Node.js (for Vercel CLI)
3. **Git Repository**: Your code should be in a Git repository
4. **External Database**: PostgreSQL or compatible database (Vercel Postgres recommended)

## 🛠️ Quick Deployment

### Option 1: One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/agentic-data-sentinel)

### Option 2: Manual Deployment

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   # Windows PowerShell
   .\deploy-vercel.ps1
   
   # Or manually
   vercel --prod
   ```

## 🔧 Configuration

### 1. Environment Variables

Set these in your Vercel dashboard or `.env.local`:

```bash
# Database (Required)
DATABASE_URL=postgresql://username:password@host:port/database

# LLM (Required)
LLM_API_KEY=your-openai-or-groq-api-key
LLM_PROVIDER=openai  # or groq
LLM_MODEL=gpt-4      # or llama-3.1-8b-instant

# Authentication (Required)
SECRET_KEY=your-secure-secret-key

# Optional
SLACK_WEBHOOK_URL=your-slack-webhook
JIRA_BASE_URL=your-jira-url
```

### 2. Database Setup

**Recommended: Vercel Postgres**
1. Go to your Vercel dashboard
2. Navigate to Storage → Create Database → Postgres
3. Copy the connection string to `DATABASE_URL`

**Alternative: External Database**
- Use any PostgreSQL-compatible database
- Ensure it's accessible from Vercel's IP ranges

### 3. LLM Configuration

**OpenAI**:
```bash
LLM_API_KEY=sk-your-openai-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
```

**Groq (Faster & Cheaper)**:
```bash
LLM_API_KEY=gsk_your-groq-key
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
```

## 📁 Project Structure

```
agentic-data-sentinel/
├── vercel.json              # Vercel configuration
├── vercel_main.py           # Vercel entry point
├── requirements-vercel.txt  # Vercel dependencies
├── deploy-vercel.ps1        # Windows deployment script
├── deploy-vercel.sh         # Unix deployment script
├── env.vercel.example       # Environment template
└── app/                     # Application code
    ├── main.py
    ├── database_vercel.py   # Vercel database config
    └── ...
```

## 🔄 Deployment Process

1. **Code Changes**: Push to your Git repository
2. **Automatic Deploy**: Vercel automatically deploys on push
3. **Manual Deploy**: Run `vercel --prod` for manual deployment
4. **Preview Deploy**: Run `vercel` for preview deployment

## 🌐 Accessing Your Application

After deployment, you'll get:
- **Production URL**: `https://your-app.vercel.app`
- **API Documentation**: `https://your-app.vercel.app/docs`
- **Health Check**: `https://your-app.vercel.app/health`

## 🔍 Monitoring & Logs

1. **Vercel Dashboard**: Monitor deployments and performance
2. **Function Logs**: View serverless function logs
3. **Analytics**: Track usage and performance metrics

## 🛡️ Security Considerations

1. **Environment Variables**: Never commit API keys to Git
2. **Database Security**: Use connection pooling and SSL
3. **API Keys**: Rotate keys regularly
4. **CORS**: Configure allowed origins for production

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Check `DATABASE_URL` format
   - Ensure database is accessible from Vercel
   - Verify SSL settings

2. **LLM API Errors**:
   - Verify API key is correct
   - Check API key permissions
   - Ensure sufficient credits

3. **Deployment Failed**:
   - Check build logs in Vercel dashboard
   - Verify all dependencies are in `requirements-vercel.txt`
   - Check for syntax errors

### Debug Mode

Enable debug mode for troubleshooting:
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📊 Performance Optimization

1. **Database**: Use connection pooling
2. **Caching**: Implement Redis for caching
3. **Cold Starts**: Optimize imports and initialization
4. **Memory**: Monitor memory usage in Vercel dashboard

## 🔄 Updates & Maintenance

1. **Code Updates**: Push to Git triggers automatic deployment
2. **Dependencies**: Update `requirements-vercel.txt`
3. **Environment**: Update variables in Vercel dashboard
4. **Database**: Run migrations as needed

## 📞 Support

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Issues**: Create an issue in your repository

## 🎉 Success!

Your Data Sentinel v1 is now running on Vercel! 

**Next Steps**:
1. Configure your data sources
2. Set up monitoring alerts
3. Customize the dashboard
4. Integrate with your data pipeline

Happy monitoring! 🛡️✨
