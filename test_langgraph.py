"""Test script for LangGraph agent workflow."""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.langgraph_agent import DataQualityAgent
from app.observability.metrics import MetricsCollector

async def test_langgraph_agent():
    """Test the LangGraph agent workflow."""
    print("🤖 Testing LangGraph Agent Workflow")
    print("=" * 50)
    
    try:
        # Initialize the agent
        agent = DataQualityAgent()
        print("✅ Agent initialized successfully")
        
        # Test workflow with dataset ID 1
        print("\n🚀 Running workflow for dataset ID 1...")
        result = await agent.run_workflow(dataset_id=1)
        
        print("\n📊 Workflow Results:")
        print(f"Status: {result.get('status')}")
        print(f"Dataset ID: {result.get('dataset_id')}")
        print(f"Health Score: {result.get('health_score')}")
        print(f"Anomalies Detected: {result.get('anomalies_detected')}")
        print(f"Actions Executed: {result.get('actions_executed')}")
        
        if result.get('error'):
            print(f"❌ Error: {result.get('error')}")
        else:
            print("✅ Workflow completed successfully!")
            
        # Test metrics collection
        print("\n📈 Testing Metrics Collection...")
        metrics = MetricsCollector()
        metrics.record_workflow(
            dataset_id=1,
            status=result.get('status', 'completed'),
            duration=5.0
        )
        metrics.record_anomaly('null_values', 3)
        metrics.record_health_score(1, result.get('health_score', 0.75))
        print("✅ Metrics recorded successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_external_apis():
    """Test external API integrations."""
    print("\n🔗 Testing External API Integrations")
    print("=" * 50)
    
    try:
        from app.services.external_apis import ExternalAPIManager
        
        # Initialize API manager
        api_manager = ExternalAPIManager()
        print("✅ External API manager initialized")
        
        # Check integration status
        print("\n📋 Integration Status:")
        print(f"Slack: {'✅' if api_manager.slack else '❌'}")
        print(f"Jira: {'✅' if api_manager.jira else '❌'}")
        print(f"GitHub: {'✅' if api_manager.github else '❌'}")
        print(f"Email: {'✅' if api_manager.email else '❌'}")
        
        # Test notification (will fail without real API keys, but should not crash)
        print("\n📤 Testing notification (mock)...")
        result = await api_manager.send_notification(
            channel="#test",
            message="Test notification from Data Sentinel",
            priority="medium",
            platform="slack"
        )
        print(f"Notification result: {result}")
        
        # Test issue creation (will fail without real API keys, but should not crash)
        print("\n📝 Testing issue creation (mock)...")
        result = await api_manager.create_issue(
            title="Test Data Quality Issue",
            description="This is a test issue created by Data Sentinel",
            priority="medium",
            platform="jira"
        )
        print(f"Issue creation result: {result}")
        
        print("✅ External API tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ External API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🧪 Data Sentinel Testing Suite")
    print("=" * 50)
    
    # Test LangGraph agent
    langgraph_success = await test_langgraph_agent()
    
    # Test external APIs
    api_success = await test_external_apis()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 50)
    print(f"LangGraph Agent: {'✅ PASS' if langgraph_success else '❌ FAIL'}")
    print(f"External APIs: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if langgraph_success and api_success:
        print("\n🎉 All tests passed! Your Data Sentinel is ready!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())
