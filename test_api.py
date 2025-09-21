"""Test script for API endpoints."""

import requests
import json

def test_health():
    """Test health endpoint."""
    print("🏥 Testing Health Endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health test failed: {e}")
        return False

def test_metrics():
    """Test metrics endpoint."""
    print("\n📊 Testing Metrics Endpoint...")
    try:
        response = requests.get("http://localhost:8000/metrics")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")
        return False

def test_agent_workflow():
    """Test agent workflow endpoint."""
    print("\n🤖 Testing Agent Workflow Endpoint...")
    try:
        payload = {
            "dataset_id": 1,
            "include_llm_explanation": True
        }
        response = requests.post(
            "http://localhost:8000/api/v1/agent/workflow",
            json=payload
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Agent workflow test failed: {e}")
        return False

def test_external_apis():
    """Test external API endpoints."""
    print("\n🔗 Testing External API Endpoints...")
    try:
        # Test integration status
        response = requests.get("http://localhost:8000/api/v1/external/integrations/status")
        print(f"Integration Status - Status: {response.status_code}")
        print(f"Integration Status - Response: {response.json()}")
        
        # Test notification (will fail without real API keys, but should not crash)
        notification_payload = {
            "channel": "#test",
            "message": "Test notification from Data Sentinel",
            "priority": "medium",
            "platform": "slack"
        }
        response = requests.post(
            "http://localhost:8000/api/v1/external/notify",
            json=notification_payload
        )
        print(f"Notification - Status: {response.status_code}")
        print(f"Notification - Response: {response.json()}")
        
        return True
    except Exception as e:
        print(f"❌ External API test failed: {e}")
        return False

def main():
    """Run all API tests."""
    print("🧪 Data Sentinel API Testing Suite")
    print("=" * 50)
    
    # Run tests
    health_success = test_health()
    metrics_success = test_metrics()
    agent_success = test_agent_workflow()
    external_success = test_external_apis()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 50)
    print(f"Health Endpoint: {'✅ PASS' if health_success else '❌ FAIL'}")
    print(f"Metrics Endpoint: {'✅ PASS' if metrics_success else '❌ FAIL'}")
    print(f"Agent Workflow: {'✅ PASS' if agent_success else '❌ FAIL'}")
    print(f"External APIs: {'✅ PASS' if external_success else '❌ FAIL'}")
    
    if all([health_success, metrics_success, agent_success, external_success]):
        print("\n🎉 All API tests passed! Your Data Sentinel is working perfectly!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
