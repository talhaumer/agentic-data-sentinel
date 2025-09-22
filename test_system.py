#!/usr/bin/env python3
"""
🛡️ Data Sentinel - Complete System Test Script (Python)
This script tests all functionality of the Data Sentinel platform
Run this after starting the system with: python run.py
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Configuration
API_BASE = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:8501"

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_colored(text: str, color: str = Colors.NC) -> None:
    """Print colored text"""
    print(f"{color}{text}{Colors.NC}")

def print_result(success: bool, message: str) -> None:
    """Print test result"""
    if success:
        print_colored(f"✅ {message}", Colors.GREEN)
    else:
        print_colored(f"❌ {message}", Colors.RED)
        sys.exit(1)

def wait_for_service(url: str, service_name: str, max_attempts: int = 30) -> bool:
    """Wait for service to be ready"""
    print_colored(f"⏳ Waiting for {service_name} to be ready...", Colors.YELLOW)
    
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_colored(f"✅ {service_name} is ready!", Colors.GREEN)
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(".", end="", flush=True)
        time.sleep(2)
    
    print()
    print_colored(f"❌ {service_name} failed to start after {max_attempts} attempts", Colors.RED)
    return False

def test_api_endpoint(url: str, method: str = "GET", data: Optional[Dict] = None, description: str = "") -> Optional[Dict]:
    """Test API endpoint"""
    try:
        if method.upper() == "POST":
            response = requests.post(url, json=data, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        
        response.raise_for_status()
        print_result(True, description)
        return response.json() if response.content else None
    except requests.exceptions.RequestException as e:
        print_result(False, f"{description} - Error: {str(e)}")
        return None

def main():
    """Main test function"""
    print_colored("🛡️ Data Sentinel - Complete System Test", Colors.BLUE)
    print_colored("==========================================", Colors.BLUE)
    print()
    
    # Wait for services to be ready
    if not wait_for_service(f"{API_BASE}/health", "API Server"):
        sys.exit(1)
    if not wait_for_service(f"{DASHBOARD_URL}", "Dashboard"):
        sys.exit(1)
    
    print()
    print_colored("🚀 Starting Complete System Test", Colors.PURPLE)
    print()
    
    # Test 1: Health Check
    print_colored("1. Testing Health Check", Colors.CYAN)
    test_api_endpoint(f"{API_BASE}/health", description="Health check passed")
    
    # Test 2: List Initial Datasets
    print_colored("2. Testing Initial Dataset List", Colors.CYAN)
    datasets = test_api_endpoint(f"{API_BASE}/api/v1/datasets/", description="Dataset list retrieved")
    
    # Test 3: Add Sample Datasets
    print_colored("3. Adding Sample Datasets", Colors.CYAN)
    
    # Add Parquet dataset
    parquet_data = {
        "name": "test_events",
        "owner": "test_team",
        "source": "file:///Users/talha.umer/agentic-data-sentinel/data/sample_events.parquet"
    }
    parquet_response = test_api_endpoint(f"{API_BASE}/api/v1/datasets/", "POST", parquet_data, "Parquet dataset added")
    
    # Add CSV dataset
    csv_data = {
        "name": "test_employees",
        "owner": "hr_team",
        "source": "file:///Users/talha.umer/agentic-data-sentinel/data/sample_employees.csv?format=csv"
    }
    csv_response = test_api_endpoint(f"{API_BASE}/api/v1/datasets/", "POST", csv_data, "CSV dataset added")
    
    # Add JSON dataset
    json_data = {
        "name": "test_products",
        "owner": "product_team",
        "source": "file:///Users/talha.umer/agentic-data-sentinel/data/sample_products.json?format=json"
    }
    json_response = test_api_endpoint(f"{API_BASE}/api/v1/datasets/", "POST", json_data, "JSON dataset added")
    
    # Add Excel dataset
    excel_data = {
        "name": "test_employees_excel",
        "owner": "hr_team",
        "source": "file:///Users/talha.umer/agentic-data-sentinel/data/sample_employees.xlsx?format=xlsx"
    }
    excel_response = test_api_endpoint(f"{API_BASE}/api/v1/datasets/", "POST", excel_data, "Excel dataset added")
    
    # Test 4: Run Agent Workflows
    print_colored("4. Running Agent Workflows", Colors.CYAN)
    
    # Get updated dataset list
    datasets = test_api_endpoint(f"{API_BASE}/api/v1/datasets/", description="Updated dataset list retrieved")
    print("Available datasets:")
    for dataset in datasets:
        print(f"ID {dataset['id']}: {dataset['name']} ({dataset['owner']})")
    
    # Run workflow on first dataset
    print_colored("Running workflow on dataset 1...", Colors.YELLOW)
    workflow_data = {
        "dataset_id": 1,
        "include_llm_explanation": True
    }
    test_api_endpoint(f"{API_BASE}/api/v1/agent/workflow", "POST", workflow_data, "Workflow 1 completed")
    
    # Run workflow on CSV dataset
    print_colored("Running workflow on CSV dataset...", Colors.YELLOW)
    workflow_data["dataset_id"] = 2
    test_api_endpoint(f"{API_BASE}/api/v1/agent/workflow", "POST", workflow_data, "CSV workflow completed")
    
    # Run workflow on JSON dataset
    print_colored("Running workflow on JSON dataset...", Colors.YELLOW)
    workflow_data["dataset_id"] = 3
    test_api_endpoint(f"{API_BASE}/api/v1/agent/workflow", "POST", workflow_data, "JSON workflow completed")
    
    # Test 5: Check Workflow Runs
    print_colored("5. Checking Workflow Runs", Colors.CYAN)
    runs = test_api_endpoint(f"{API_BASE}/api/v1/runs/", description="Workflow runs retrieved")
    
    print("Recent runs:")
    for run in runs:
        health_score = run.get('summary', {}).get('health_score', 'N/A')
        print(f"Run {run['id']}: Dataset {run['dataset_id']} | Status: {run['status']} | Health: {health_score}")
    
    # Test 6: Check Anomalies
    print_colored("6. Checking Detected Anomalies", Colors.CYAN)
    anomalies = test_api_endpoint(f"{API_BASE}/api/v1/anomalies/", description="Anomalies retrieved")
    
    anomaly_count = len(anomalies) if anomalies else 0
    print(f"Total anomalies detected: {anomaly_count}")
    
    if anomaly_count > 0:
        print("Sample anomalies:")
        for anomaly in anomalies[:3]:
            print(f"ID {anomaly['id']}: {anomaly['table_name']}.{anomaly['column_name']} - {anomaly['issue_type']} (Severity: {anomaly['severity']})")
    
    # Test 7: Test Approval Queue
    print_colored("7. Testing Approval Queue", Colors.CYAN)
    approvals = test_api_endpoint(f"{API_BASE}/api/v1/agent/pending-approvals", description="Approval queue retrieved")
    
    pending_count = approvals.get('count', 0) if approvals else 0
    print(f"Pending approvals: {pending_count}")
    
    # Test 8: Create High-Severity Anomaly for Testing
    print_colored("8. Creating Test High-Severity Anomaly", Colors.CYAN)
    high_severity_data = {
        "dataset_id": 1,
        "table_name": "events",
        "column_name": "critical_field",
        "issue_type": "data_loss",
        "severity": 5,
        "description": "Critical data loss detected - test anomaly for approval queue",
        "status": "open"
    }
    high_severity_response = test_api_endpoint(f"{API_BASE}/api/v1/anomalies/", "POST", high_severity_data, "High-severity anomaly created")
    
    # Update anomaly to pending approval
    if high_severity_response:
        anomaly_id = high_severity_response['id']
        update_data = {
            "status": "pending_approval",
            "action_taken": "pending_approval"
        }
        test_api_endpoint(f"{API_BASE}/api/v1/anomalies/{anomaly_id}", "PUT", update_data, "Anomaly updated to pending approval")
        
        # Test 9: Test Approval Process
        print_colored("9. Testing Approval Process", Colors.CYAN)
        test_api_endpoint(f"{API_BASE}/api/v1/agent/approve/{anomaly_id}?approved=true&approved_by=test_user", "POST", description="Approval process completed")
    
    # Test 10: Check Final Status
    print_colored("10. Checking Final System Status", Colors.CYAN)
    
    # Check datasets
    print("Dataset health scores:")
    final_datasets = test_api_endpoint(f"{API_BASE}/api/v1/datasets/", description="Final dataset list retrieved")
    if final_datasets:
        for dataset in final_datasets:
            print(f"{dataset['name']}: {dataset['health_score']}")
    
    # Check final anomaly count
    final_anomalies = test_api_endpoint(f"{API_BASE}/api/v1/anomalies/", description="Final anomalies retrieved")
    final_anomaly_count = len(final_anomalies) if final_anomalies else 0
    print(f"Total anomalies: {final_anomaly_count}")
    
    # Check final approval queue
    final_approvals = test_api_endpoint(f"{API_BASE}/api/v1/agent/pending-approvals", description="Final approval queue retrieved")
    final_pending_count = final_approvals.get('count', 0) if final_approvals else 0
    print(f"Pending approvals: {final_pending_count}")
    
    print()
    print_colored("🎉 ALL TESTS COMPLETED SUCCESSFULLY! 🎉", Colors.GREEN)
    print()
    print_colored("📊 Test Summary:", Colors.BLUE)
    print("  • Health check: ✅")
    print("  • Dataset management: ✅")
    print("  • Multi-format support: ✅")
    print("  • Agent workflows: ✅")
    print("  • Anomaly detection: ✅")
    print("  • Approval queue: ✅")
    print()
    print_colored("🌐 Access Points:", Colors.PURPLE)
    print(f"  • Dashboard: {DASHBOARD_URL}")
    print(f"  • API: {API_BASE}")
    print(f"  • API Docs: {API_BASE}/docs")
    print(f"  • Health: {API_BASE}/health")
    print()
    print_colored("Data Sentinel is fully operational! 🚀", Colors.GREEN)

if __name__ == "__main__":
    main()
