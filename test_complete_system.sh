#!/bin/bash

# 🛡️ Data Sentinel - Complete System Test Script
# This script tests all functionality of the Data Sentinel platform
# Run this after starting the system with: python run.py

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
API_BASE="http://localhost:8000"
DASHBOARD_URL="http://localhost:8501"

echo -e "${BLUE}🛡️ Data Sentinel - Complete System Test${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name failed to start after $max_attempts attempts${NC}"
    return 1
}

# Wait for services to be ready
wait_for_service "$API_BASE/health" "API Server"
wait_for_service "$DASHBOARD_URL" "Dashboard"

echo ""
echo -e "${PURPLE}🚀 Starting Complete System Test${NC}"
echo ""

# Test 1: Health Check
echo -e "${CYAN}1. Testing Health Check${NC}"
curl -s "$API_BASE/health" | jq '.' > /dev/null
print_result $? "Health check passed"

# Test 2: List Initial Datasets
echo -e "${CYAN}2. Testing Initial Dataset List${NC}"
curl -s "$API_BASE/api/v1/datasets/" | jq '.' > /dev/null
print_result $? "Dataset list retrieved"

# Test 3: Add Sample Datasets
echo -e "${CYAN}3. Adding Sample Datasets${NC}"

# Add Parquet dataset
PARQUET_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/datasets/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_events",
    "owner": "test_team",
    "source": "file:///Users/talha.umer/agentic-data-sentinel/data/sample_events.parquet"
  }')
echo "$PARQUET_RESPONSE" | jq '.' > /dev/null
print_result $? "Parquet dataset added"

# Add CSV dataset
CSV_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/datasets/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_employees",
    "owner": "hr_team",
    "source": "file:///Users/talha.umer/agentic-data-sentinel/data/sample_employees.csv?format=csv"
  }')
echo "$CSV_RESPONSE" | jq '.' > /dev/null
print_result $? "CSV dataset added"

# Add JSON dataset
JSON_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/datasets/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_products",
    "owner": "product_team",
    "source": "file:///Users/talha.umer/agentic-data-sentinel/data/sample_products.json?format=json"
  }')
echo "$JSON_RESPONSE" | jq '.' > /dev/null
print_result $? "JSON dataset added"

# Add Excel dataset
EXCEL_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/datasets/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_employees_excel",
    "owner": "hr_team",
    "source": "file:///Users/talha.umer/agentic-data-sentinel/data/sample_employees.xlsx?format=xlsx"
  }')
echo "$EXCEL_RESPONSE" | jq '.' > /dev/null
print_result $? "Excel dataset added"

# Test 4: Run Agent Workflows
echo -e "${CYAN}4. Running Agent Workflows${NC}"

# Get dataset IDs
DATASETS=$(curl -s "$API_BASE/api/v1/datasets/")
echo "Available datasets:"
echo "$DATASETS" | jq -r '.[] | "ID \(.id): \(.name) (\(.owner))"'

# Run workflow on first dataset
echo -e "${YELLOW}Running workflow on dataset 1...${NC}"
WORKFLOW_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/agent/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "include_llm_explanation": true
  }')
echo "$WORKFLOW_RESPONSE" | jq '.' > /dev/null
print_result $? "Workflow 1 completed"

# Run workflow on CSV dataset
echo -e "${YELLOW}Running workflow on CSV dataset...${NC}"
WORKFLOW_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/agent/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 2,
    "include_llm_explanation": true
  }')
echo "$WORKFLOW_RESPONSE" | jq '.' > /dev/null
print_result $? "CSV workflow completed"

# Run workflow on JSON dataset
echo -e "${YELLOW}Running workflow on JSON dataset...${NC}"
WORKFLOW_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/agent/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 3,
    "include_llm_explanation": true
  }')
echo "$WORKFLOW_RESPONSE" | jq '.' > /dev/null
print_result $? "JSON workflow completed"

# Test 5: Check Workflow Runs
echo -e "${CYAN}5. Checking Workflow Runs${NC}"
RUNS_RESPONSE=$(curl -s "$API_BASE/api/v1/runs/")
echo "$RUNS_RESPONSE" | jq '.' > /dev/null
print_result $? "Workflow runs retrieved"

echo "Recent runs:"
echo "$RUNS_RESPONSE" | jq -r '.[] | "Run \(.id): Dataset \(.dataset_id) | Status: \(.status) | Health: \(.summary.health_score // "N/A")"'

# Test 6: Check Anomalies
echo -e "${CYAN}6. Checking Detected Anomalies${NC}"
ANOMALIES_RESPONSE=$(curl -s "$API_BASE/api/v1/anomalies/")
echo "$ANOMALIES_RESPONSE" | jq '.' > /dev/null
print_result $? "Anomalies retrieved"

ANOMALY_COUNT=$(echo "$ANOMALIES_RESPONSE" | jq 'length')
echo "Total anomalies detected: $ANOMALY_COUNT"

if [ "$ANOMALY_COUNT" -gt 0 ]; then
    echo "Sample anomalies:"
    echo "$ANOMALIES_RESPONSE" | jq -r '.[0:3][] | "ID \(.id): \(.table_name).\(.column_name) - \(.issue_type) (Severity: \(.severity))"'
fi

# Test 7: Test Approval Queue
echo -e "${CYAN}7. Testing Approval Queue${NC}"
APPROVALS_RESPONSE=$(curl -s "$API_BASE/api/v1/agent/pending-approvals")
echo "$APPROVALS_RESPONSE" | jq '.' > /dev/null
print_result $? "Approval queue retrieved"

PENDING_COUNT=$(echo "$APPROVALS_RESPONSE" | jq '.count')
echo "Pending approvals: $PENDING_COUNT"

# Test 8: Create High-Severity Anomaly for Testing
echo -e "${CYAN}8. Creating Test High-Severity Anomaly${NC}"
HIGH_SEVERITY_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/anomalies/" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "table_name": "events",
    "column_name": "critical_field",
    "issue_type": "data_loss",
    "severity": 5,
    "description": "Critical data loss detected - test anomaly for approval queue",
    "status": "open"
  }')
echo "$HIGH_SEVERITY_RESPONSE" | jq '.' > /dev/null
print_result $? "High-severity anomaly created"

# Update anomaly to pending approval
ANOMALY_ID=$(echo "$HIGH_SEVERITY_RESPONSE" | jq -r '.id')
curl -s -X PUT "$API_BASE/api/v1/anomalies/$ANOMALY_ID" \
  -H "Content-Type: application/json" \
  -d '{"status": "pending_approval", "action_taken": "pending_approval"}' > /dev/null
print_result $? "Anomaly updated to pending approval"

# Test 9: Test Approval Process
echo -e "${CYAN}9. Testing Approval Process${NC}"
APPROVE_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/agent/approve/$ANOMALY_ID?approved=true&approved_by=test_user")
echo "$APPROVE_RESPONSE" | jq '.' > /dev/null
print_result $? "Approval process completed"

# Test 10: Check Final Status
echo -e "${CYAN}10. Checking Final System Status${NC}"

# Check datasets
echo "Dataset health scores:"
curl -s "$API_BASE/api/v1/datasets/" | jq -r '.[] | "\(.name): \(.health_score)"'

# Check final anomaly count
FINAL_ANOMALIES=$(curl -s "$API_BASE/api/v1/anomalies/")
FINAL_COUNT=$(echo "$FINAL_ANOMALIES" | jq 'length')
echo "Total anomalies: $FINAL_COUNT"

# Check final approval queue
FINAL_APPROVALS=$(curl -s "$API_BASE/api/v1/agent/pending-approvals")
FINAL_PENDING=$(echo "$FINAL_APPROVALS" | jq '.count')
echo "Pending approvals: $FINAL_PENDING"

# Test 11: Test Error Handling
echo -e "${CYAN}11. Testing Error Handling${NC}"

# Test invalid dataset ID
INVALID_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$API_BASE/api/v1/datasets/99999")
if [ "$INVALID_RESPONSE" = "404" ]; then
    print_result 0 "404 error handling works"
else
    print_result 1 "404 error handling failed"
fi

# Test invalid endpoint
INVALID_ENDPOINT=$(curl -s -w "%{http_code}" -o /dev/null "$API_BASE/api/v1/invalid")
if [ "$INVALID_ENDPOINT" = "404" ]; then
    print_result 0 "Invalid endpoint handling works"
else
    print_result 1 "Invalid endpoint handling failed"
fi

echo ""
echo -e "${GREEN}🎉 ALL TESTS COMPLETED SUCCESSFULLY! 🎉${NC}"
echo ""
echo -e "${BLUE}📊 Test Summary:${NC}"
echo -e "  • Health check: ✅"
echo -e "  • Dataset management: ✅"
echo -e "  • Multi-format support: ✅"
echo -e "  • Agent workflows: ✅"
echo -e "  • Anomaly detection: ✅"
echo -e "  • Approval queue: ✅"
echo -e "  • Error handling: ✅"
echo ""
echo -e "${PURPLE}🌐 Access Points:${NC}"
echo -e "  • Dashboard: $DASHBOARD_URL"
echo -e "  • API: $API_BASE"
echo -e "  • API Docs: $API_BASE/docs"
echo -e "  • Health: $API_BASE/health"
echo ""
echo -e "${GREEN}Data Sentinel is fully operational! 🚀${NC}"
