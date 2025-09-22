#!/bin/bash

# 🛡️ Data Sentinel - Quick Test Script
# Simple test to verify core functionality

set -e

API_BASE="http://localhost:8000"

echo "🛡️ Data Sentinel - Quick Test"
echo "=============================="

# Test 1: Health Check
echo "1. Testing health check..."
curl -s "$API_BASE/health" | jq '.'
echo "✅ Health check passed"
echo ""

# Test 2: Add a dataset
echo "2. Adding test dataset..."
curl -s -X POST "$API_BASE/api/v1/datasets/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "quick_test",
    "owner": "test_team",
    "source": "file:///Users/talha.umer/agentic-data-sentinel/data/sample_events.parquet"
  }' | jq '.'
echo "✅ Dataset added"
echo ""

# Test 3: Run workflow
echo "3. Running agent workflow..."
curl -s -X POST "$API_BASE/api/v1/agent/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "include_llm_explanation": true
  }' | jq '.'
echo "✅ Workflow completed"
echo ""

# Test 4: Check results
echo "4. Checking results..."
echo "Datasets:"
curl -s "$API_BASE/api/v1/datasets/" | jq -r '.[] | "\(.name): \(.health_score)"'

echo ""
echo "Anomalies:"
ANOMALY_COUNT=$(curl -s "$API_BASE/api/v1/anomalies/" | jq 'length')
echo "Total anomalies: $ANOMALY_COUNT"

echo ""
echo "🎉 Quick test completed successfully!"
echo "Dashboard: http://localhost:8501"
echo "API Docs: http://localhost:8000/docs"
