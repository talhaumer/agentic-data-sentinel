# 🛡️ Data Sentinel v1 - Simple Setup

A simplified version of Data Sentinel that runs without Docker, Celery, Redis, Nginx, or Grafana. Perfect for getting started quickly!

## 🚀 Quick Start (3 steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp env.simple .env
# Edit .env and add your OpenAI API key
```

### 3. Run the Application
```bash
python run_simple.py
```

That's it! 🎉

## 📱 Access Points

- **API**: http://localhost:8000
- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 What's Included

### ✅ Core Features
- **FastAPI Backend**: RESTful API with all endpoints
- **Streamlit Dashboard**: Interactive web interface
- **Data Validation**: Comprehensive quality checks
- **Agent Workflows**: LangGraph-powered automation
- **LLM Integration**: OpenAI GPT-4 explanations
- **SQLite Database**: No external database needed
- **DuckDB Data Warehouse**: Local data storage

### ❌ What's Removed (for simplicity)
- Docker containers
- Celery background tasks
- Redis caching
- Nginx load balancing
- Grafana monitoring
- Prometheus metrics
- Production deployment configs

## 🎯 How to Use

### 1. Add a Dataset
```bash
curl -X POST "http://localhost:8000/api/v1/datasets/" \
  -H "Content-Type: application/json" \
  -d '{"name": "my_events", "owner": "data_team", "source": "api"}'
```

### 2. Run Agent Workflow
```bash
curl -X POST "http://localhost:8000/api/v1/agent/workflow" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 1, "include_llm_explanation": true}'
```

### 3. View Results
Open http://localhost:8501 in your browser to see the dashboard.

## 🔧 Configuration

Edit `.env` file:

```bash
# Required - Choose OpenAI or Groq
LLM_API_KEY=sk-your-openai-api-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4

# OR for Groq (faster & cheaper):
# LLM_API_KEY=gsk_your-groq-api-key-here
# LLM_PROVIDER=groq
# LLM_MODEL=llama-3.1-70b-versatile

SECRET_KEY=your-secret-key-here

# Optional
DEBUG=true
LOG_LEVEL=INFO
```

### 🤖 LLM Provider Options

**OpenAI** (Default):
- Models: `gpt-4`, `gpt-3.5-turbo`
- Get API key: https://platform.openai.com/api-keys

**Groq** (Recommended - Faster & Cheaper):
- Models: `llama-3.1-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`
- Get API key: https://console.groq.com/keys

## 📊 Sample Data

The application automatically generates sample data with quality issues:
- **Events**: 10,000 records with null values and outliers
- **Users**: 5,000 records with missing emails
- **Transactions**: 15,000 records with duplicates and anomalies

## 🚨 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **"LLM API key not found"**
   - Edit `.env` file and add your API key
   - OpenAI: https://platform.openai.com/api-keys
   - Groq: https://console.groq.com/keys

3. **"Port already in use"**
   - Kill existing processes: `pkill -f uvicorn` or `pkill -f streamlit`
   - Or change ports in the code

4. **"Database error"**
   - Delete `data/sentinel.db` and restart
   - The app will recreate the database

### Manual Start (if run_simple.py doesn't work)

```bash
# Terminal 1 - API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Dashboard
streamlit run app/frontend/streamlit_main.py --server.port 8501
```

## 🔄 Upgrading to Full Version

When you're ready for production features:

1. **Add Redis**: For caching and background tasks
2. **Add Celery**: For async processing
3. **Add Docker**: For containerization
4. **Add Monitoring**: Prometheus + Grafana
5. **Add Load Balancer**: Nginx configuration

See the main `README.md` for full deployment instructions.

## 🎉 What You Get

- **Autonomous Data Quality Monitoring**
- **AI-Powered Anomaly Detection**
- **LLM Explanations and Recommendations**
- **Interactive Dashboard**
- **RESTful API**
- **Sample Data for Testing**

Perfect for learning, prototyping, and small-scale deployments!

---

**Happy Data Quality Monitoring! 🚀**
