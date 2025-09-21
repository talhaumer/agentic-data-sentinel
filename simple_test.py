"""Simple test for debugging."""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_basic_imports():
    """Test basic imports."""
    print("Testing basic imports...")
    
    try:
        from app.agents.langgraph_agent import DataQualityAgent
        print("✅ DataQualityAgent imported")
        
        from app.observability.metrics import MetricsCollector
        print("✅ MetricsCollector imported")
        
        from app.services.external_apis import ExternalAPIManager
        print("✅ ExternalAPIManager imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent_creation():
    """Test agent creation."""
    print("\nTesting agent creation...")
    
    try:
        from app.agents.langgraph_agent import DataQualityAgent
        agent = DataQualityAgent()
        print("✅ DataQualityAgent created successfully")
        
        # Test the graph property
        print(f"Graph type: {type(agent.graph)}")
        print("✅ Graph created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_workflow():
    """Test workflow execution."""
    print("\nTesting workflow execution...")
    
    try:
        from app.agents.langgraph_agent import DataQualityAgent
        agent = DataQualityAgent()
        
        print("Running workflow...")
        result = await agent.run_workflow(dataset_id=1)
        
        print(f"✅ Workflow completed: {result}")
        return True
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run tests."""
    print("🧪 Simple Test Suite")
    print("=" * 30)
    
    # Test imports
    import_success = await test_basic_imports()
    
    if import_success:
        # Test agent creation
        creation_success = await test_agent_creation()
        
        if creation_success:
            # Test workflow
            workflow_success = await test_workflow()
        else:
            workflow_success = False
    else:
        creation_success = False
        workflow_success = False
    
    print(f"\n📋 Results:")
    print(f"Imports: {'✅' if import_success else '❌'}")
    print(f"Creation: {'✅' if creation_success else '❌'}")
    print(f"Workflow: {'✅' if workflow_success else '❌'}")

if __name__ == "__main__":
    asyncio.run(main())
