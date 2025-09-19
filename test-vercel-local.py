#!/usr/bin/env python3
"""
Test script to verify Vercel setup locally
Run this before deploying to ensure everything works
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # Test main app import
        from app.main_vercel_simple import app
        print("✅ Main app imported successfully")
        
        # Test API import
        from api.index import handler
        print("✅ API handler imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_app_creation():
    """Test if the FastAPI app can be created."""
    print("🔍 Testing app creation...")
    
    try:
        from app.main_vercel_simple import app
        
        # Test basic app properties
        assert app.title == "Data Sentinel v1"
        assert app.version == "1.0.0"
        print("✅ App created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_endpoints():
    """Test if endpoints are accessible."""
    print("🔍 Testing endpoints...")
    
    try:
        from app.main_vercel_simple import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        print("✅ Root endpoint working")
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        print("✅ Health endpoint working")
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return False

def test_vercel_config():
    """Test if Vercel configuration is valid."""
    print("🔍 Testing Vercel configuration...")
    
    try:
        import json
        
        # Check vercel.json exists
        vercel_config_path = Path("vercel.json")
        assert vercel_config_path.exists(), "vercel.json not found"
        
        # Load and validate vercel.json
        with open(vercel_config_path) as f:
            config = json.load(f)
        
        assert "builds" in config, "Missing builds in vercel.json"
        assert "routes" in config, "Missing routes in vercel.json"
        assert config["builds"][0]["src"] == "api/index.py", "Wrong build source"
        
        print("✅ Vercel configuration valid")
        return True
        
    except Exception as e:
        print(f"❌ Vercel config test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Vercel setup for Data Sentinel v1")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_app_creation,
        test_endpoints,
        test_vercel_config,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for Vercel deployment.")
        print("\nNext steps:")
        print("1. Push to GitHub: git push origin main")
        print("2. Go to https://vercel.com")
        print("3. Import your repository")
        print("4. Set environment variables")
        print("5. Deploy!")
    else:
        print("❌ Some tests failed. Please fix issues before deploying.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
