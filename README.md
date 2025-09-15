# 🛡️ Data Sentinel - Agentic AI Data Quality Platform

Data Sentinel is an agentic AI platform that autonomously ensures data quality, anomaly detection, and insight generation across modern data warehouses. It uses LangGraph for orchestration, LLMs for explanations, and provides a comprehensive dashboard for monitoring and management.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- OpenAI API key (or other LLM provider)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd agentic-data-sentinel
cp env.example .env
# Edit .env with your configuration
```

### 2. Start Services

```bash
# Using Make (recommended)
make quickstart

# Or manually
docker-compose up -d
python scripts/generate_sample_data.py
```

### 3. Access the Platform

- **API**: http://localhost:8000
- **Dashboard**: http://localhost:8501
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

---

## Table of contents

1. [Project Overview](#project-overview)
2. [Goals & Use Cases](#goals--use-cases)
3. [High-level Architecture](#high-level-architecture)
4. [Tech Stack](#tech-stack)
5. [Core Components](#core-components)
6. [Data Model & Storage](#data-model--storage)
7. [Agent Workflow (detailed)](#agent-workflow-detailed)
8. [Implementation Plan — Step by step](#implementation-plan---step-by-step)
9. [Development & Infra Setup](#development--infra-setup)
10. [APIs & UI contract](#apis--ui-contract)
11. [LLM & MCP Integration](#llm--mcp-integration)
12. [Testing, CI/CD, and Deployment](#testing-cicd-and-deployment)
13. [Monitoring, Observability & Metrics](#monitoring-observability--metrics)
14. [Security & Governance](#security--governance)
15. [Performance & Scaling](#performance--scaling)
16. [Sample data & quickstart commands](#sample-data--quickstart-commands)
17. [Roadmap & milestones](#roadmap--milestones)
18. [Contributing & License](#contributing--license)

---

# Project Overview

Data Sentinel is designed to be a demonstrable, deployable project that highlights both **data engineering** and **data science** skills, while showcasing **agentic AI** capability: an autonomous loop that checks, reasons, and acts on data problems.

It is intentionally domain-agnostic: you can onboard any tabular dataset and the agent will treat it uniformly (tables → columns → validations → metrics → action).

---

# Goals & Use Cases

* Automatically detect data quality issues and anomalies in a data warehouse.
* Produce human-readable explanations for anomalies via LLMs (root cause hypotheses).
* Provide actionable remediation: SQL patches, re-ingestion, alerts (Slack/Jira), or automated fixes.
* Give data engineers and analysts a single UI (Streamlit) + API surface (FastAPI) to inspect health and run workflows.

**Primary audiences:** Data Engineers, Data Scientists, Analytics Engineers, SREs, Product/Data Owners.

---

# High-level Architecture

```
                +-----------------+
                |  Streamlit UI   |   <-- Manual runs, drilldowns, explanations
                +--------+--------+
                         |
                         v
                +--------+---------+
                |     FastAPI      |   <-- API endpoints for triggers, reports
                +--------+---------+
                         |
                         v
                +--------+---------+
                |   LangGraph /    |   <-- Agentic workflow engine (nodes)
                |   LangChain      |
                +--------+---------+
                         |
        +----------------+----------------+
        |                                 |
        v                                 v
+---------------+                 +------------------+
| Validation &  |                 |  LLM Service     |  <- prompt + explain
| Analytics svc |                 |  (OpenAI/other)  |
+---------------+                 +------------------+
        |                                 |
        v                                 v
+---------------+                 +------------------+
| Data Warehouse|                 | External Tools   | <- Slack, Jira, GitHub
|  (DW / DB)    |                 | via MCP / Webhook|
+---------------+                 +------------------+
```

Notes:

* For local development use DuckDB/Postgres + Docker.
* For production, target BigQuery / Snowflake / Redshift.

---

# Tech Stack

* **Orchestration / Agent:** LangGraph (or LangChain agents) for workflow nodes & planning
* **LLM:** OpenAI/Anthropic/Mistral or any LLM backend via LangChain
* **API:** FastAPI
* **Dashboard:** Streamlit
* **Database/Metadata:** Postgres / DuckDB (local) for metadata + events; Data Warehouse (DuckDB/BigQuery/Snowflake) for analytic tables
* **Validation:** Great Expectations (optional) or custom rules
* **MCP (Model Context Protocol):** Use for structured tool calls / external actions
* **CI/CD:** GitHub Actions / Docker
* **Testing:** pytest
* **Dev tools:** Docker Compose

---

# Core Components

## 1. FastAPI (API layer)

* Auth protected endpoints for: run validation, list datasets, get anomalies, request fixes.
* Webhooks for notifications.

## 2. LangGraph Agent Workflows

* Modular node design where each node does a single responsibility: `fetch_table`, `validate_table`, `detect_anomaly`, `explain_anomaly`, `plan_remediation`, `execute_action`.

## 3. Validation & Analytics Service

* A microservice (or Python module) that runs checks (null %, distribution drift, cardinality changes, uniqueness, duplicates) and returns scores.

## 4. LLM & Explanation

* For each anomaly, generate a human-friendly explanation and recommended SQL patch or steps.
* Use prompt templates and structured outputs (JSON preferred).

## 5. MCP Connectors

* Slack notifier
* Jira/GitHub issue creator
* Optional: trigger DAG runs (Airflow / Dagster) or make commits to infra repo with fixes

## 6. Streamlit Dashboard

* Summary health metrics
* Dataset listing and health drilldown
* Anomaly explorer with LLM explanation
* Manual action triggers

---

# Data Model & Storage

Design two persistence layers:

1. **Operational DB** (Postgres/DuckDB): stores metadata, run history, anomalies, suggested fixes.
2. **Data Warehouse**: the actual datasets to monitor.

### Suggested tables (operational DB)

```sql
-- datasets
CREATE TABLE datasets (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  owner TEXT,
  source TEXT,
  last_ingest TIMESTAMP,
  health_score FLOAT,
  created_at TIMESTAMP DEFAULT now()
);

-- runs
CREATE TABLE runs (
  id SERIAL PRIMARY KEY,
  dataset_id INT REFERENCES datasets(id),
  run_time TIMESTAMP DEFAULT now(),
  status TEXT,
  summary JSONB
);

-- anomalies
CREATE TABLE anomalies (
  id SERIAL PRIMARY KEY,
  dataset_id INT REFERENCES datasets(id),
  table_name TEXT,
  column_name TEXT,
  issue_type TEXT,
  severity INT,
  detected_at TIMESTAMP DEFAULT now(),
  description TEXT,
  suggested_sql TEXT,
  extra JSONB
);
```

---

# Agent Workflow — detailed (generate → predict → analyze → plan → act)

For each dataset/table run the following loop:

1. **Fetch / Snapshot**

   * Pull a sample or statistics (row count, null% per column, histograms) from DW.

2. **Validate** (Predict)

   * Run deterministic checks (schema, null rate, unique constraints).
   * Run ML-based anomaly detection if enabled (time-series model or isolation forest on metrics).

3. **Analyze**

   * Compute a composite `health_score`.
   * If anomaly threshold exceeded, collect context (recent deployments, upstream job logs, ingestion times).

4. **Explain** (LLM)

   * Call an LLM with a templated prompt and structured inputs to hypothesize root cause and suggest remediation SQL or steps.

5. **Plan**

   * Decide action based on severity & policy: `AUTO_FIX`, `NOTIFY_OWNER`, `CREATE_ISSUE`, `NO_ACTION`.

6. **Act**

   * If `AUTO_FIX`: run (or queue) SQL patch against staging and verify.
   * If `NOTIFY_OWNER`: send Slack message with summary + link to dashboard.
   * If `CREATE_ISSUE`: Create Jira/GitHub issue via MCP.

7. **Record**

   * Persist run results & anomalies to operational DB and update dataset `health_score`.

8. **Repeat / Schedule**

   * Schedule next run per dataset cadence.

### LangGraph Node examples (pseudo)

```python
# node: fetch_table
def fetch_table(table_id):
    stats = dw.get_table_stats(table_id)
    return stats

# node: validate_table
def validate_table(stats, rules):
    results = []
    for rule in rules:
        results.append(rule.check(stats))
    return results

# node: explain_anomaly
def explain_anomaly(anomaly, context):
    prompt = build_prompt(anomaly, context)
    response = llm.call(prompt)
    structured = parse_response(response)
    return structured
```

---

# Implementation plan — step by step (developer checklist)

> Each item below is a suggested PR/feature to implement. Use this as a sprint backlog.

## Phase 0 — Planning & repo scaffolding

* [ ] Create repo skeleton
* [ ] Add `README.md`, `CODE_OF_CONDUCT`, `CONTRIBUTING.md`, `LICENSE`
* [ ] Create `requirements.txt` and `pyproject.toml`/`poetry.lock` if using poetry

## Phase 1 — Local infra & samples

* [ ] Docker Compose with Postgres + DuckDB (or DuckDB only) + Redis (optional)
* [ ] Sample dataset loader script (`scripts/generate_sample_data.py`)
* [ ] Simple FastAPI skeleton with health endpoint
* [ ] Simple Streamlit app skeleton

## Phase 2 — Validation service

* [ ] Implement basic deterministic checks (null%, dtype mismatch, unique constraint)
* [ ] Add a lightweight scoring function to compute `health_score`
* [ ] Persist run results to operational DB

## Phase 3 — Agent & Orchestration

* [ ] Integrate LangGraph / LangChain agent harness
* [ ] Implement base nodes: fetch, validate, detect, explain, plan, act
* [ ] Create an orchestration runner to run agents against a list of datasets

## Phase 4 — LLM explanations & MCP

* [ ] Implement LLM prompt templates + response parsing
* [ ] Integrate MCP pattern for external tool calls (Slack/Jira/GitHub)
* [ ] Add options for `AUTO_FIX` with explicit approval flow

## Phase 5 — Dashboard & UX

* [ ] Build Streamlit pages: overview, dataset drilldown, anomaly details
* [ ] Add manual-run controls and run logs
* [ ] Add export/report generation

## Phase 6 — Tests, CI, containerization

* [ ] Unit tests for Validation service and LangGraph nodes
* [ ] Integration tests using in-memory DuckDB
* [ ] GitHub Actions: lint, tests, build docker

## Phase 7 — Production hardening

* [ ] Add caching, batching, concurrency controls
* [ ] Add RBAC/auth (FastAPI OAuth2 or token-based)
* [ ] Add monitoring (Prometheus/Grafana) and logging (structured)

---

# Development & infra setup (local quickstart)

**Prereqs**

* Python 3.10+
* Docker & Docker Compose
* An LLM API key (OpenAI or other) for the explanation service

**Local setup (example)**

```bash
# clone repo
git clone git@github.com:your-org/data-sentinel.git
cd data-sentinel

# copy env
cp .env.example .env
# edit .env to add DB urls and LLM keys

# build & run containers (postgres + app)
docker compose up --build

# run migrations (if using Alembic)
# alembic upgrade head

# run the FastAPI app
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# run Streamlit
# streamlit run app/frontend/streamlit_main.py
```

**Environment variables (examples)**

```
DATABASE_URL=postgresql://user:pass@postgres:5432/dsentinel
DW_CONN_STRING=duckdb:///data/dw.db  # local DW
LLM_API_KEY=sk-...                 # provider key
LLM_PROVIDER=openai                # or anthropic
SLACK_WEBHOOK=https://hooks.slack.com/xyz
```

---

# APIs & UI contract

**API endpoints (suggested)**

* `GET /health` — app health
* `GET /datasets` — list datasets and health
* `POST /datasets` — register new dataset
* `POST /runs/{dataset_id}` — trigger a run
* `GET /runs/{run_id}` — get run details
* `GET /anomalies` — list anomalies
* `POST /anomalies/{id}/action` — take action (create issue / auto-fix)

**Streamlit pages**

* Overview (health, score distribution)
* Dataset details (columns, metrics, run history)
* Anomaly explorer (LLM explanation + suggested SQL)
* Administration (register dataset, set rules)

---

# LLM & MCP Integration

## LLM prompt template (example)

```
You are a Data Steward assistant. Given the following anomaly metadata and recent metrics, explain the most likely root cause and propose one or two remediation steps (SQL or operational) in JSON format with keys: cause, confidence, suggested_sql, action_type.

Anomaly: {anomaly}
Context: {context}

Return JSON only.
```

**Parsing & safety**

* Validate JSON response; use a schema validator (pydantic) to enforce `suggested_sql` is a non-destructive `SELECT` or `UPDATE` statement
* Avoid blindly executing SQL from LLM output — always require `staging` run and approval unless rule-based low-risk changes are marked for auto-apply.

## MCP (Model Context Protocol) usage

* Model outputs that instruct an external action should be structured as an MCP object (tool name, action, payload).
* MCP connector layer transforms the MCP payload into API calls (Slack message, create Jira ticket, call orchestration endpoint).

Example MCP object (JSON):

```json
{
  "tool": "slack",
  "action": "post_message",
  "payload": {"channel": "#dataops", "text": "Anomaly detected in sales.transactions: 43% nulls in price"}
}
```

---

# Testing, CI/CD, and Deployment

**Testing strategy**

* Unit tests for validation rules and scoring functions.
* Contract tests for LLM response parsing.
* Integration tests that run an end-to-end agent loop against synthetic data.

**GitHub Actions**

* `lint` (ruff/flake8)
* `test` (pytest)
* `build` (docker build)
* `deploy` (optional: push to ECR/GCR)

**Deployment options**

* Containerized: Docker → ECR/GCR → run on ECS/Fargate, Cloud Run, or Kubernetes (EKS/GKE)
* Serverless FastAPI: Cloud Run / Azure Container Apps
* Streamlit: deploy on Streamlit Cloud or as a container

---

# Monitoring, Observability & Metrics

Track these core metrics:

* **Run success rate** (per dataset)
* **Average run duration** (latency)
* **Anomalies per 1k rows**
* **Auto-fix success rate**
* **Time to remediation**

Tools:

* Prometheus + Grafana for metrics
* ELK / Loki for logs
* Sentry for error reporting

---

# Security & Governance

* Store secrets in a secrets manager (AWS Secrets Manager, GCP Secret Manager) — do not commit `.env` with secrets.
* Least-privilege DB accounts for auto-fix operations.
* Audit trail for all changes initiated by agent (who/what/when).
* RBAC for manual approval screens.

---

# Performance & Scaling

* Use **batch sampling** for very large tables (statistics rather than full scans).
* Cache repeated property calculations (Redis).
* Parallelize dataset checks using worker pool (Celery/FastAPI background tasks)
* For heavy analytics, push down computations to the data warehouse (SQL), not Python.

---

# Sample data & quickstart commands

**Generate synthetic dataset (simple Python)**

```python
# scripts/generate_sample_data.py
import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()

rows = []
for _ in range(10000):
    rows.append({
        'user_id': fake.uuid4(),
        'event_time': fake.date_time_this_year(),
        'price': float(np.round(np.random.exponential(50), 2)),
        'status': np.random.choice(['ok', 'failed', None], p=[0.85, 0.1, 0.05])
    })

pd.DataFrame(rows).to_parquet('data/sample_events.parquet')
```

**Load to local DW (DuckDB CLI)**

```sql
-- duckdb
INSTALL httpfs; -- if needed
CREATE TABLE events AS SELECT * FROM read_parquet('data/sample_events.parquet');
```

---

# Roadmap & milestones (recommended)

**Sprint 0 (1 week)**: Repo & basic infra, sample data loader, FastAPI + Streamlit skeleton

**Sprint 1 (2 weeks)**: Validation rules + persistence + basic runs

**Sprint 2 (2 weeks)**: LangGraph agent nodes + orchestration

**Sprint 3 (2 weeks)**: LLM explanation + MCP notifications

**Sprint 4 (1 week)**: Dashboard polishing + tests + CI

**Sprint 5 (1-2 weeks)**: Production hardening and deploy to cloud

---

# Example prompts & testing

Create a `prompts/` directory with templates and expected LLM output examples (golden files) used in contract tests.

**Prompt example**

```
Explain this anomaly:
- Column: price
- Null rate: 43%
- Last successful ingest: 2025-08-01
- Upstream: payments API responded 503 on 2025-08-02
```

**Expected output (structured)**

```json
{
  "cause": "Upstream API outage during ingest window",
  "confidence": 0.92,
  "suggested_sql": "UPDATE staging.events SET price = 0 WHERE price IS NULL AND event_time < '2025-08-02';",
  "action_type": "notify_owner"
}
```

---

# Contributing & License

Contributions welcome. Keep PRs small and focused. Write tests. Document LLM prompts and expected outputs.

Suggested license: MIT.

---

# Next steps (what I can help with next)

* Generate the repository skeleton (Docker Compose, minimal FastAPI + Streamlit pages, sample data generator)
* Implement the validation service boilerplate and a couple of deterministic checks
* Create LangGraph node templates for the agent loop

If you want, I can scaffold the repo with files (Docker Compose, FastAPI skeleton, Streamlit skeleton, and sample scripts). Tell me which part you want first and I will generate it.

---

<small>Made for an educational capstone: Data Engineers & Data Scientists. Keep safety in mind: never auto-execute destructive SQL without an approval workflow.</small>
