# Environment Setup

## Required Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./data/sentinel.db
DW_CONN_STRING=sqlite:///./data/dw.db

# LLM Configuration
LLM_API_KEY=your-llm-api-key-here
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-70b-versatile

# Authentication
SECRET_KEY=your-secret-key-here

# External API Integrations (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@domain.com
JIRA_API_TOKEN=your-jira-api-token
GITHUB_TOKEN=ghp_your-github-token
GITHUB_OWNER=your-github-username
GITHUB_REPO=your-repo-name
SENDGRID_API_KEY=SG.your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com

# LangChain Tracing (Optional)
LANGCHAIN_API_KEY=your-langchain-api-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=data-sentinel
ENVIRONMENT=development

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
MAX_WORKERS=4
BATCH_SIZE=1000
DW_SAMPLE_SIZE=10000
ANOMALY_THRESHOLD=0.7
HEALTH_SCORE_THRESHOLD=0.8
```

## Quick Start

1. Copy the environment variables above to a `.env` file
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python run_simple.py`
4. Access the API at `http://localhost:8000`
5. Access the dashboard at `http://localhost:8501`
