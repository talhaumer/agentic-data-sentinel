# 🛡️ Data Sentinel

<div align="center">

![Data Sentinel](https://img.shields.io/badge/Data%20Sentinel-v0.1.0-blue?style=for-the-badge&logo=shield)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-orange?style=for-the-badge&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)

**AI-Powered Data Quality Monitoring & Anomaly Detection Platform**

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-documentation) • [🐳 Docker](#-docker-deployment) • [🔧 Configuration](#-configuration) • [📊 Features](#-features)

</div>

---

## 🌟 Overview

Data Sentinel is a cutting-edge, AI-powered data quality monitoring platform that combines intelligent anomaly detection, real-time validation, and automated remediation. Built with modern microservices architecture, it provides comprehensive data quality insights with LLM-powered explanations and recommendations.

### ✨ Key Features

- 🤖 **AI-Powered Anomaly Detection** - Advanced ML algorithms with adaptive thresholds
- 🔍 **Intelligent Data Validation** - Dynamic rule generation based on data patterns
- 📊 **Real-Time Monitoring** - Live dashboard with interactive visualizations
- 🚀 **Automated Workflows** - Multi-agent orchestration for data quality checks
- 💡 **LLM Explanations** - AI-generated insights and remediation suggestions
- 🐳 **Docker Ready** - Complete containerization for easy deployment
- 🔧 **Extensible Architecture** - Plugin-based system for custom validators

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Streamlit Client]
        Dashboard[Interactive Dashboard]
        Analytics[Advanced Analytics]
    end
    
    subgraph "API Layer"
        API[FastAPI Server]
        Endpoints[REST Endpoints]
        Auth[Authentication]
    end
    
    subgraph "Agent Layer"
        Orchestrator[Enhanced Orchestrator]
        Validation[Intelligent Validation]
        Anomaly[Anomaly Detection]
        Remediation[Remediation Agent]
        Learning[Learning Agent]
    end
    
    subgraph "Data Layer"
        DB[(SQLite/PostgreSQL)]
        Files[File Storage]
        Cache[Redis Cache]
    end
    
    subgraph "External Services"
        LLM[OpenAI/Groq LLM]
        Storage[Cloud Storage]
        Monitoring[Monitoring Tools]
    end
    
    UI --> API
    Dashboard --> API
    Analytics --> API
    API --> Orchestrator
    Orchestrator --> Validation
    Orchestrator --> Anomaly
    Orchestrator --> Remediation
    Orchestrator --> Learning
    Validation --> DB
    Anomaly --> DB
    Remediation --> DB
    Learning --> DB
    Orchestrator --> LLM
    API --> Storage
    API --> Monitoring
```

### 📁 Project Structure

```
agentic-data-sentinel/
├── 🐳 docker-compose.yml          # Docker orchestration
├── 🐳 Dockerfile.server           # Server container
├── 🐳 Dockerfile.client           # Client container
├── 📋 requirements.txt            # Root dependencies
├── 🚀 run.py                      # One-command startup
├── 📊 create_sample_data.py       # Sample data generator
├── 📖 README.md                   # This file
├── 📖 DATASETS.md                 # Dataset documentation
├── 📖 LLM_SETUP.md                # LLM configuration guide
│
├── 🖥️ server/                     # Backend API server
│   ├── 🐳 Dockerfile              # Server container
│   ├── 📋 requirements.txt        # Server dependencies
│   ├── 🚀 main.py                 # FastAPI application
│   ├── 🚀 start.py                # Server startup
│   ├── ⚙️ env.example             # Environment template
│   │
│   └── 📦 app/                    # Application code
│       ├── 🤖 agents/             # AI agents
│       │   ├── base_agent.py
│       │   ├── data_loading_agent.py
│       │   ├── intelligent_validation_agent.py
│       │   ├── intelligent_anomaly_detection_agent.py
│       │   ├── enhanced_orchestration_agent.py
│       │   ├── remediation_agent.py
│       │   ├── notification_agent.py
│       │   └── learning_agent.py
│       │
│       ├── 🌐 api/                # API layer
│       │   ├── endpoints.py
│       │   └── schemas.py
│       │
│       ├── ⚙️ core/               # Core services
│       │   ├── config.py
│       │   └── database.py
│       │
│       ├── 📊 models/             # Data models
│       │   ├── dataset.py
│       │   └── run.py
│       │
│       ├── 🔧 services/           # Business logic
│       │   ├── llm_service.py
│       │   └── intelligent_llm_service.py
│       │
│       └── 🛠️ utils/              # Utilities
│           └── json_encoder.py
│
├── 🖥️ client/                     # Frontend client
│   ├── 🐳 Dockerfile              # Client container
│   ├── 📋 requirements.txt        # Client dependencies
│   ├── 🚀 app.py                  # Streamlit application
│   └── 🚀 start.py                # Client startup
│
└── 📊 data/                       # Data storage
    ├── 📈 sample_*.parquet        # Sample datasets
    ├── 📊 employees.csv
    ├── 📦 inventory.csv
    └── 🗄️ *.db                    # Database files
```

---

## 🚀 Quick Start

### Option 1: One-Command Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/agentic-data-sentinel.git
cd agentic-data-sentinel

# Run everything with one command
python run.py
```

### Option 2: Docker Deployment (Production Ready)

#### Prerequisites
- Docker Desktop installed and running
- Docker Compose v2.0+

#### Quick Start with Docker
```bash
# Clone the repository
git clone https://github.com/your-username/agentic-data-sentinel.git
cd agentic-data-sentinel

# Windows (PowerShell)
.\docker-run.ps1 build
.\docker-run.ps1 start prod

# Linux/macOS (Bash)
chmod +x docker-run.sh
./docker-run.sh build
./docker-run.sh start prod

# Access the application
# API: http://localhost:8000
# Client: http://localhost:8501
```

#### Docker Profiles
- **Production**: `.\docker-run.ps1 start prod` (ports 8000, 8501)
- **Development**: `.\docker-run.ps1 start dev` (ports 8001, 8502)
- **Full Stack**: `.\docker-run.ps1 start full` (includes database, cache, monitoring)

#### Manual Docker Commands
```bash
# Build the application
docker-compose build

# Start production environment
docker-compose up -d

# Start development environment
docker-compose --profile dev up -d

# Start full environment with monitoring
docker-compose --profile db --profile cache --profile proxy --profile monitoring up -d
```

### Option 3: Manual Python Installation

#### Prerequisites
- Python 3.11+
- pip

#### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/agentic-data-sentinel.git
cd agentic-data-sentinel

# Install server dependencies
cd server
pip install -r requirements.txt

# Install client dependencies
cd ../client
pip install -r requirements.txt

# Start the server
cd ../server
python start.py

# Start the client (in a new terminal)
cd client
streamlit run app.py
```

#### Access the application
- API: http://localhost:8000
- Client: http://localhost:8501

---

## 🐳 Docker Deployment

### Docker Files
- `Dockerfile` - Multi-stage Docker build configuration
- `docker-compose.yml` - Multi-service orchestration
- `.dockerignore` - Build context exclusions
- `docker-run.sh` - Linux/macOS deployment script
- `docker-run.ps1` - Windows PowerShell deployment script
- `nginx/nginx.conf` - Reverse proxy configuration
- `monitoring/prometheus.yml` - Metrics collection setup
- `scripts/init-db.sql` - Database initialization

### Docker Services
- **data-sentinel** - Main application (FastAPI + Streamlit)
- **postgres** - External database (optional)
- **redis** - Caching and session management (optional)
- **nginx** - Reverse proxy and load balancer (optional)
- **prometheus** - Metrics collection (optional)
- **grafana** - Monitoring dashboard (optional)

### Docker Commands
```bash
# Build and start production
docker-compose build
docker-compose up -d

# Development environment
docker-compose --profile dev up -d

# Full stack with monitoring
docker-compose --profile db --profile cache --profile proxy --profile monitoring up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up
docker-compose down -v --remove-orphans
```

### Docker Ports
- **8000** - FastAPI server (production)
- **8501** - Streamlit client (production)
- **8001** - FastAPI server (development)
- **8502** - Streamlit client (development)
- **5432** - PostgreSQL (if enabled)
- **6379** - Redis (if enabled)
- **80/443** - Nginx (if enabled)
- **9090** - Prometheus (if enabled)
- **3000** - Grafana (if enabled)

For detailed Docker documentation, see [DOCKER.md](DOCKER.md).

---

## 🔧 Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp server/env.example server/.env
# Edit server/.env with your API keys

# 3. Create sample data
python create_sample_data.py

# 4. Start services
python start_data_sentinel.py
```

### 🌐 Access Points

After startup, access the application at:

- **🎨 Web Interface**: http://localhost:8501
- **🔌 API Server**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **🔄 API ReDoc**: http://localhost:8000/redoc

---

## 🐳 Docker Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Quick Start with Docker

```bash
# 1. Clone repository
git clone https://github.com/your-username/agentic-data-sentinel.git
cd agentic-data-sentinel

# 2. Configure environment
cp server/env.example server/.env
# Edit server/.env with your configuration

# 3. Start services
docker-compose up -d

# 4. Check status
docker-compose ps
```

### Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `server` | 8000 | FastAPI backend server |
| `client` | 8501 | Streamlit frontend client |
| `redis` | 6379 | Caching and session storage |
| `postgres` | 5432 | Production database (optional) |

### Docker Commands

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d server

# View logs
docker-compose logs -f server
docker-compose logs -f client

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build -d

# Scale services
docker-compose up -d --scale server=3

# Execute commands in container
docker-compose exec server python -c "print('Hello from server')"
```

### Production Docker Configuration

For production deployment, use the production docker-compose file:

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# With environment file
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the server directory:

```env
# =============================================================================
# DATA SENTINEL CONFIGURATION
# =============================================================================

# Application Settings
APP_NAME=Data Sentinel
APP_VERSION=0.1.0
DEBUG=false
LOG_LEVEL=info

# Database Configuration
DATABASE_URL=sqlite:///./sentinel.db
# For PostgreSQL: postgresql://user:password@localhost:5432/sentinel

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# =============================================================================
# LLM CONFIGURATION
# =============================================================================

# LLM Provider (openai, groq, anthropic)
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Groq Configuration (Alternative)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama2-70b-4096

# Anthropic Configuration (Alternative)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# API Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=["http://localhost:8501", "http://localhost:3000"]

# =============================================================================
# MONITORING & LOGGING
# =============================================================================

# Logging
LOG_FORMAT=json
LOG_FILE=logs/sentinel.log

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090

# =============================================================================
# EXTERNAL INTEGRATIONS
# =============================================================================

# GitHub Integration (Optional)
GITHUB_TOKEN=your_github_token
GITHUB_OWNER=your_username
GITHUB_REPO=your_repo

# Slack Integration (Optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### LLM Provider Setup

#### OpenAI Setup
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
```

#### Groq Setup (Free Alternative)
```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your-groq-api-key
GROQ_MODEL=llama2-70b-4096
```

#### Anthropic Setup
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

---

## 📊 Features

### 🤖 AI-Powered Agents

#### Intelligent Anomaly Detection Agent
- **Multi-method Detection**: Isolation Forest, DBSCAN, Z-score analysis
- **Adaptive Thresholds**: AI-calculated optimal thresholds
- **Temporal Analysis**: Time-series anomaly detection
- **Severity Classification**: 5-level severity scoring
- **Confidence Scoring**: Detection confidence metrics

#### Intelligent Validation Agent
- **Dynamic Rule Generation**: AI-generated validation rules
- **Pattern Recognition**: Automatic data pattern detection
- **Business Logic Validation**: Domain-specific checks
- **Real-time Validation**: Live data quality monitoring
- **Custom Validators**: Extensible validation framework

#### Enhanced Orchestration Agent
- **Parallel Execution**: Multi-agent parallel processing
- **Intelligent Routing**: Smart agent selection
- **Workflow Optimization**: Performance optimization
- **Error Recovery**: Automatic error handling
- **Learning Integration**: Continuous improvement

### 📈 Advanced Analytics

#### Real-Time Dashboard
- **Live Metrics**: Real-time data quality metrics
- **Interactive Charts**: Plotly-powered visualizations
- **Performance Tracking**: Workflow performance monitoring
- **Trend Analysis**: Historical trend visualization
- **Custom Dashboards**: Configurable dashboard layouts

#### Anomaly Analysis
- **Severity Filtering**: Filter by anomaly severity
- **Type Classification**: Anomaly type categorization
- **Timeline Analysis**: Temporal anomaly patterns
- **Root Cause Analysis**: AI-powered root cause identification
- **Impact Assessment**: Business impact evaluation

### 🔧 Data Management

#### Dataset Management
- **Multiple Sources**: File, Database, API support
- **File Upload**: Direct file upload interface
- **Dynamic Configuration**: Source-specific configuration
- **Data Preview**: Real-time data preview
- **Schema Validation**: Automatic schema detection

#### Workflow Management
- **Scheduled Runs**: Automated workflow scheduling
- **Manual Triggers**: On-demand workflow execution
- **Status Tracking**: Real-time workflow status
- **Performance Metrics**: Execution time and success rates
- **Error Handling**: Comprehensive error reporting

---

## 🌐 API Documentation

### Core Endpoints

#### Health & Status
```http
GET /api/v1/health
GET /api/v1/agents/status
GET /api/v1/workflows
```

#### Dataset Management
```http
GET    /api/v1/datasets              # List datasets
POST   /api/v1/datasets              # Create dataset
GET    /api/v1/datasets/{id}         # Get dataset
PUT    /api/v1/datasets/{id}         # Update dataset
DELETE /api/v1/datasets/{id}         # Delete dataset
```

#### Workflow Execution
```http
POST   /api/v1/workflow              # Trigger workflow
GET    /api/v1/runs                  # List runs
GET    /api/v1/runs/{id}             # Get run details
POST   /api/v1/workflows/{id}/cancel # Cancel workflow
```

#### Anomaly Management
```http
GET    /api/v1/anomalies             # List anomalies
GET    /api/v1/anomalies/{id}        # Get anomaly details
POST   /api/v1/anomalies/{id}/resolve # Resolve anomaly
```

### Example API Usage

#### Create Dataset
```bash
curl -X POST "http://localhost:8000/api/v1/datasets" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Data Q4 2024",
    "description": "Quarterly sales data with quality issues",
    "source_type": "file",
    "source_config": {
      "file_path": "data/sales_q4_2024.csv",
      "file_type": "csv",
      "delimiter": ",",
      "encoding": "utf-8"
    }
  }'
```

#### Trigger Workflow
```bash
curl -X POST "http://localhost:8000/api/v1/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "include_llm_explanation": true
  }'
```

#### Get Anomalies
```bash
curl -X GET "http://localhost:8000/api/v1/anomalies?severity=high&limit=10"
```

---

## 🛠️ Development

### Development Setup

```bash
# 1. Clone repository
git clone https://github.com/your-username/agentic-data-sentinel.git
cd agentic-data-sentinel

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r server/requirements.txt
pip install -r client/requirements.txt

# 4. Install development dependencies
pip install -r requirements-dev.txt

# 5. Configure environment
cp server/env.example server/.env
# Edit server/.env

# 6. Run tests
pytest tests/

# 7. Start development servers
python start_data_sentinel.py
```

### Development Commands

```bash
# Run server in development mode
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run client in development mode
cd client
streamlit run app.py --server.port 8501

# Run tests
pytest tests/ -v

# Run linting
flake8 server/ client/
black server/ client/

# Run type checking
mypy server/ client/

# Generate documentation
sphinx-build docs/ docs/_build/
```

### Code Quality

This project maintains high code quality standards:

- **Type Hints**: Full type annotation coverage
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit and integration tests
- **Linting**: Flake8, Black, MyPy
- **Security**: Bandit security scanning
- **Performance**: Profiling and optimization

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=server --cov=client --cov-report=html

# Run performance tests
pytest tests/performance/ -v
```

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_agents.py
│   ├── test_services.py
│   └── test_models.py
├── integration/             # Integration tests
│   ├── test_api.py
│   ├── test_workflows.py
│   └── test_database.py
├── e2e/                     # End-to-end tests
│   ├── test_full_workflow.py
│   └── test_client_integration.py
├── performance/             # Performance tests
│   ├── test_load.py
│   └── test_stress.py
└── fixtures/                # Test fixtures
    ├── sample_data.py
    └── mock_responses.py
```

---

## 📈 Performance & Monitoring

### Performance Metrics

- **Response Time**: < 200ms for API endpoints
- **Throughput**: 1000+ requests/minute
- **Memory Usage**: < 512MB per service
- **CPU Usage**: < 50% under normal load
- **Database**: < 100ms query time

### Monitoring Setup

```bash
# Enable metrics collection
export ENABLE_METRICS=true

# Start with monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Access monitoring dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
# Jaeger: http://localhost:16686
```

### Health Checks

```bash
# Check service health
curl http://localhost:8000/api/v1/health

# Check agent status
curl http://localhost:8000/api/v1/agents/status

# Check database connectivity
curl http://localhost:8000/api/v1/health/database
```

---

## 🚀 Deployment

### Production Deployment

#### Docker Production Setup

```bash
# 1. Clone repository
git clone https://github.com/your-username/agentic-data-sentinel.git
cd agentic-data-sentinel

# 2. Configure production environment
cp .env.production .env
# Edit .env with production values

# 3. Start production services
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify deployment
curl http://your-domain.com/api/v1/health
```

#### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=data-sentinel

# Access services
kubectl port-forward svc/data-sentinel-server 8000:8000
kubectl port-forward svc/data-sentinel-client 8501:8501
```

#### Cloud Deployment

##### AWS ECS
```bash
# Build and push images
docker build -t your-account.dkr.ecr.region.amazonaws.com/data-sentinel:latest .
docker push your-account.dkr.ecr.region.amazonaws.com/data-sentinel:latest

# Deploy to ECS
aws ecs update-service --cluster data-sentinel --service data-sentinel --force-new-deployment
```

##### Google Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy data-sentinel-server --source . --platform managed --region us-central1
gcloud run deploy data-sentinel-client --source . --platform managed --region us-central1
```

##### Azure Container Instances
```bash
# Deploy to Azure
az container create --resource-group myResourceGroup --name data-sentinel --image your-registry/data-sentinel:latest
```

### Environment-Specific Configurations

#### Development
```env
DEBUG=true
LOG_LEVEL=debug
DATABASE_URL=sqlite:///./dev.db
```

#### Staging
```env
DEBUG=false
LOG_LEVEL=info
DATABASE_URL=postgresql://user:pass@staging-db:5432/sentinel
```

#### Production
```env
DEBUG=false
LOG_LEVEL=warning
DATABASE_URL=postgresql://user:pass@prod-db:5432/sentinel
ENABLE_METRICS=true
```

---

## 🔒 Security

### Security Features

- **API Authentication**: JWT-based authentication
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Content Security Policy
- **Rate Limiting**: API rate limiting
- **CORS Configuration**: Configurable CORS policies
- **Secrets Management**: Environment-based secrets

### Security Best Practices

```bash
# Run security scan
bandit -r server/ client/

# Check for vulnerabilities
safety check

# Update dependencies
pip-audit

# Generate security report
bandit -r server/ client/ -f json -o security-report.json
```

### Security Configuration

```env
# Security settings
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# CORS settings
CORS_ORIGINS=["https://yourdomain.com"]
CORS_ALLOW_CREDENTIALS=true

# Rate limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=200
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Setup

```bash
# 1. Fork the repository
# 2. Clone your fork
git clone https://github.com/your-username/agentic-data-sentinel.git
cd agentic-data-sentinel

# 3. Create feature branch
git checkout -b feature/amazing-feature

# 4. Make changes and commit
git commit -m "Add amazing feature"

# 5. Push to your fork
git push origin feature/amazing-feature

# 6. Create Pull Request
```

### Development Guidelines

- **Code Style**: Follow PEP 8, use Black for formatting
- **Type Hints**: Add type hints to all functions
- **Documentation**: Update docstrings and README
- **Testing**: Add tests for new features
- **Commits**: Use conventional commit messages

### Issue Templates

- 🐛 **Bug Report**: Use bug report template
- ✨ **Feature Request**: Use feature request template
- 📚 **Documentation**: Use documentation template
- 🔧 **Configuration**: Use configuration template

---

## 📚 Documentation

### Additional Documentation

- [📖 API Documentation](http://localhost:8000/docs)
- [🔧 Configuration Guide](docs/configuration.md)
- [🐳 Docker Guide](docs/docker.md)
- [🚀 Deployment Guide](docs/deployment.md)
- [🧪 Testing Guide](docs/testing.md)
- [🔒 Security Guide](docs/security.md)
- [🤝 Contributing Guide](CONTRIBUTING.md)
- [📋 Changelog](CHANGELOG.md)

### Dataset Documentation

See [DATASETS.md](DATASETS.md) for information about:
- Supported data formats
- Dataset configuration options
- Sample datasets
- Data quality checks

### LLM Setup Guide

See [LLM_SETUP.md](LLM_SETUP.md) for:
- LLM provider configuration
- API key setup
- Model selection guide
- Performance optimization

---

## 🆘 Support & Troubleshooting

### Common Issues

#### 1. LLM API Rate Limits
```bash
# Error: Rate limit exceeded
# Solution: Wait and retry, or upgrade API plan
export LLM_PROVIDER=groq  # Use Groq for higher limits
```

#### 2. Database Connection Issues
```bash
# Error: Database connection failed
# Solution: Check database URL and credentials
export DATABASE_URL=sqlite:///./sentinel.db  # Use SQLite for development
```

#### 3. Port Conflicts
```bash
# Error: Port already in use
# Solution: Use different ports
export SERVER_PORT=8001
export CLIENT_PORT=8502
```

#### 4. Memory Issues
```bash
# Error: Out of memory
# Solution: Increase Docker memory limits
docker-compose up -d --scale server=1
```

### Getting Help

- 📧 **Email**: support@datasentinel.ai
- 💬 **Discord**: [Join our Discord](https://discord.gg/datasentinel)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/agentic-data-sentinel/issues)
- 📖 **Wiki**: [GitHub Wiki](https://github.com/your-username/agentic-data-sentinel/wiki)
- 🎥 **Video Tutorials**: [YouTube Channel](https://youtube.com/datasentinel)

### Debug Mode

```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=debug

# Start with debug logging
python start_data_sentinel.py
```

---

## 📊 Roadmap

### Version 0.2.0 (Q2 2024)
- [ ] **Advanced ML Models**: Custom anomaly detection models
- [ ] **Real-time Streaming**: Kafka integration for real-time data
- [ ] **Advanced Analytics**: Time-series forecasting
- [ ] **Multi-tenant Support**: Organization and user management
- [ ] **API Versioning**: Backward compatibility support

### Version 0.3.0 (Q3 2024)
- [ ] **GraphQL API**: GraphQL endpoint for flexible queries
- [ ] **Advanced Visualizations**: Custom chart builder
- [ ] **Workflow Designer**: Visual workflow creation
- [ ] **Plugin System**: Third-party plugin support
- [ ] **Mobile App**: React Native mobile application

### Version 1.0.0 (Q4 2024)
- [ ] **Enterprise Features**: SSO, RBAC, audit logs
- [ ] **Cloud Native**: Kubernetes operator
- [ ] **Advanced Security**: End-to-end encryption
- [ ] **Performance Optimization**: Sub-second response times
- [ ] **Global Deployment**: Multi-region support

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Data Sentinel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **OpenAI** for GPT models and API
- **Groq** for high-performance LLM inference
- **FastAPI** for the excellent web framework
- **Streamlit** for the intuitive frontend framework
- **SQLAlchemy** for database ORM
- **Pandas** for data manipulation
- **Scikit-learn** for machine learning algorithms
- **Plotly** for interactive visualizations
- **Docker** for containerization
- **All Contributors** who help improve this project

---

<div align="center">

**Made with ❤️ by the Data Sentinel Team**

[⭐ Star this repo](https://github.com/your-username/agentic-data-sentinel) • [🐛 Report Bug](https://github.com/your-username/agentic-data-sentinel/issues) • [✨ Request Feature](https://github.com/your-username/agentic-data-sentinel/issues) • [📖 Documentation](https://github.com/your-username/agentic-data-sentinel/wiki)

</div>