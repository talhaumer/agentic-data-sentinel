# 🛡️ Data Sentinel - Agentic AI Data Quality Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)](https://langchain-ai.github.io/langgraph/)

**Data Sentinel** is a production-ready AI-powered data quality platform that autonomously monitors, detects anomalies, and provides intelligent remediation across modern data warehouses. Built with LangGraph for orchestration, LLMs for explanations, and a comprehensive dashboard for monitoring.

## ✨ Key Features

### 🎯 **Core Capabilities**
- **🤖 AI-Powered Anomaly Detection**: Intelligent data quality monitoring with LLM explanations
- **📊 Multi-Format Support**: Parquet, CSV, JSON, Excel, and SQL databases
- **🔄 Human-in-the-Loop**: Approval queue for high-severity issues
- **🚨 Automated Actions**: GitHub issue creation, email notifications, auto-fix capabilities
- **📈 Real-time Dashboard**: Interactive Streamlit interface for monitoring and management
- **🔍 Comprehensive Validation**: 15+ data quality checks including uniqueness, completeness, and consistency

### 🛠️ **Technical Stack**
- **Backend**: FastAPI with SQLite database
- **Frontend**: Streamlit dashboard
- **AI/ML**: LangGraph agents with OpenAI/Groq LLM integration
- **Data Processing**: Pandas, DuckDB data warehouse
- **Integrations**: GitHub, Email (SendGrid/Gmail), MCP protocol
- **Observability**: LangChain tracing and structured logging

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- LLM API key (OpenAI or Groq)

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/your-org/agentic-data-sentinel.git
cd agentic-data-sentinel

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
nano .env
```

**Required Configuration:**
```bash
# Choose one LLM provider
LLM_API_KEY=your-api-key-here
LLM_PROVIDER=openai  # or groq
LLM_MODEL=gpt-4      # or llama-3.1-70b-versatile

# Optional: GitHub integration
GITHUB_TOKEN=your-github-token
GITHUB_OWNER=your-username
GITHUB_REPO=your-repo

# Optional: Email integration
GMAIL_EMAIL=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
```

### 3. Run the Application
```bash
# Start the platform
python run.py
```

### 4. Access the Platform
- **🌐 Dashboard**: http://localhost:8501
- **🔌 API**: http://localhost:8000
- **📚 API Docs**: http://localhost:8000/docs
- **❤️ Health Check**: http://localhost:8000/health

## 📊 Supported Data Sources

| Format | Status | Example Usage | Features |
|--------|--------|---------------|----------|
| **Parquet** | ✅ Full Support | `file:///path/data.parquet` | High performance, columnar storage |
| **CSV** | ✅ Full Support | `file:///path/data.csv?format=csv` | Comma-separated values |
| **JSON** | ✅ Full Support | `file:///path/data.json?format=json` | JSON arrays and JSON Lines |
| **Excel** | ✅ Full Support | `file:///path/data.xlsx?format=xlsx` | .xlsx and .xls formats |
| **SQL Tables** | ✅ Full Support | `db://connection?table=name` | Any SQLAlchemy-compatible database |

## 🎯 How to Use

### 1. Add Your Dataset
```bash
# Via API
curl -X POST "http://localhost:8000/api/v1/datasets/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sales_data",
    "owner": "data_team",
    "source": "file:///path/to/your/data.parquet"
  }'

# Or use the dashboard at http://localhost:8501
```

### 2. Run Data Quality Analysis
```bash
# Trigger agent workflow
curl -X POST "http://localhost:8000/api/v1/agent/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "include_llm_explanation": true
  }'
```

### 3. Review Results
- **Dashboard**: View health scores, anomalies, and trends
- **Approval Queue**: Review and approve high-severity issues
- **GitHub Issues**: Automatically created for critical problems

## 🔍 Data Quality Checks

### **Completeness Checks**
- Null value percentage per column
- Missing value patterns
- Data completeness trends

### **Uniqueness Checks**
- Duplicate detection
- Primary key violations
- Cardinality analysis

### **Consistency Checks**
- Data type validation
- Format consistency
- Value range validation

### **Accuracy Checks**
- Statistical outlier detection
- Distribution analysis
- Cross-column validation

### **Timeliness Checks**
- Data freshness validation
- Ingestion delay detection
- Update frequency analysis

## 🤖 AI-Powered Features

### **Intelligent Anomaly Explanation**
- Root cause analysis using LLM
- Confidence scoring
- Suggested remediation steps
- SQL queries for investigation

### **Automated Action Planning**
- Severity-based action routing
- Human approval for critical issues
- Auto-fix for low-risk problems
- Integration with external tools

### **Smart Recommendations**
- Data quality improvement suggestions
- Preventive measures
- Best practice recommendations

## 🚨 Human-in-the-Loop Approval

### **Approval Queue**
- High-severity anomalies require human review
- Detailed context and AI analysis
- One-click approval/rejection
- Audit trail for all decisions

### **Action Types**
- **Auto-Fix**: Low-severity issues (severity 1-2)
- **Notify Owner**: Medium-severity issues (severity 3)
- **Create Issue**: High-severity issues (severity 4-5)
- **No Action**: Very low-severity issues

## 🔧 What's Included

### ✅ Core Features
- **FastAPI Backend**: RESTful API with all endpoints
- **Streamlit Dashboard**: Interactive web interface
- **LangGraph Agents**: StateGraph workflow automation
- **Data Validation**: Comprehensive quality checks
- **Anomaly Detection**: AI-powered data quality monitoring
- **External Integrations**: Slack, Jira, GitHub, SendGrid
- **LLM Integration**: AI explanations and recommendations
- **Observability**: LangChain tracing and metrics
- **SQLite Database**: No external database needed
- **DuckDB Data Warehouse**: Local data storage

### 🎯 Production Ready
- Clean, organized codebase
- Comprehensive error handling
- Structured logging
- API documentation
- Health monitoring
- Environment configuration
- LangChain observability
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

## 🔧 Configuration Options

### **LLM Providers**

**OpenAI (Default)**
```bash
LLM_API_KEY=sk-your-openai-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
```

**Groq (Recommended - Faster & Cheaper)**
```bash
LLM_API_KEY=gsk-your-groq-key
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-70b-versatile
```

### **External Integrations**

**GitHub Integration**
```bash
GITHUB_TOKEN=ghp_your-token
GITHUB_OWNER=your-username
GITHUB_REPO=your-repo
```

**Email Integration**
```bash
# Option 1: Gmail
GMAIL_EMAIL=your-email@gmail.com
GMAIL_PASSWORD=your-app-password

# Option 2: SendGrid
SENDGRID_API_KEY=your-sendgrid-key
FROM_EMAIL=your-email@domain.com
```

### **Application Settings**
```bash
SECRET_KEY=your-secret-key-here
DEBUG=true
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./sentinel.db
```

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

## 📚 API Reference

### **Core Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `GET` | `/api/v1/datasets/` | List all datasets |
| `POST` | `/api/v1/datasets/` | Create new dataset |
| `POST` | `/api/v1/agent/workflow` | Run data quality analysis |
| `GET` | `/api/v1/anomalies/` | List anomalies |
| `POST` | `/api/v1/agent/approve/{id}` | Approve/reject anomaly action |
| `GET` | `/api/v1/agent/pending-approvals` | Get approval queue |

### **Interactive API Documentation**
Visit http://localhost:8000/docs for complete API documentation with interactive testing.

## 🏗️ Architecture

### **System Components**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI       │    │   LangGraph     │
│   Dashboard     │◄──►│   Backend       │◄──►│   Agents        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   SQLite DB     │    │   LLM Service   │
                       │   (Metadata)    │    │   (OpenAI/Groq) │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Data Sources  │
                       │   (Files/DB)    │
                       └─────────────────┘
```

### **Agent Workflow**

1. **📥 Fetch Data**: Load dataset from source
2. **🔍 Validate**: Run quality checks
3. **🤖 Detect Anomalies**: AI-powered anomaly detection
4. **💡 Explain**: LLM generates explanations
5. **📋 Plan Actions**: Determine remediation steps
6. **✅ Execute**: Auto-fix or queue for approval
7. **📊 Report**: Update health scores and metrics

## 📚 Documentation

- **[Architecture Details](docs/ARCHITECTURE.md)**: Complete technical documentation
- **[API Reference](http://localhost:8000/docs)**: Interactive API documentation
- **[Sample Data](scripts/generate_sample_data.py)**: Data generation scripts

## 🛠️ Development

### **Project Structure**
```
agentic-data-sentinel/
├── app/
│   ├── agents/           # LangGraph agents
│   ├── api/             # FastAPI endpoints
│   ├── frontend/        # Streamlit dashboard
│   ├── services/        # Business logic
│   └── models.py        # Database models
├── data/                # Sample data files
├── docs/                # Documentation
├── scripts/             # Utility scripts
└── tests/               # Test suite
```

### **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_services.py
```

### **Code Quality**
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** for the agent framework
- **FastAPI** for the web framework
- **Streamlit** for the dashboard
- **Pandas** for data processing
- **OpenAI/Groq** for LLM capabilities

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/agentic-data-sentinel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/agentic-data-sentinel/discussions)

---

**Made with ❤️ for the data community. Keep your data quality high and your insights reliable!**
