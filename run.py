#!/usr/bin/env python3
"""Complete Data Sentinel runner with setup and testing."""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def print_banner():
    """Print the Data Sentinel banner."""
    print("🛡️" + "=" * 58 + "🛡️")
    print("🛡️" + " " * 20 + "DATA SENTINEL" + " " * 20 + "🛡️")
    print("🛡️" + " " * 15 + "AI-Powered Data Quality" + " " * 15 + "🛡️")
    print("🛡️" + "=" * 58 + "🛡️")
    print()

def check_python_version():
    """Check Python version compatibility."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'pandas', 'numpy', 
        'sqlalchemy', 'pydantic', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("   Installing dependencies...")
        
        # Install server dependencies
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "server/requirements.txt"], 
                         check=True, capture_output=True)
            print("✅ Server dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install server dependencies: {e}")
            return False
        
        # Install client dependencies
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "client/requirements.txt"], 
                         check=True, capture_output=True)
            print("✅ Client dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install client dependencies: {e}")
            return False
    else:
        print("✅ All dependencies are installed")
    
    return True

def setup_environment():
    """Setup environment files."""
    print("⚙️ Setting up environment...")
    
    env_file = Path("server/.env")
    env_example = Path("server/env.example")
    
    if not env_file.exists() and env_example.exists():
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ Environment file created from template")
            print("⚠️  Please edit server/.env and add your API keys if needed")
        except Exception as e:
            print(f"⚠️  Could not create .env file: {e}")
    else:
        print("✅ Environment file already exists")

def create_sample_data():
    """Create sample data if it doesn't exist."""
    data_dir = Path("data")
    if not data_dir.exists():
        print("📊 Creating sample data...")
        try:
            subprocess.run([sys.executable, "create_sample_data.py"], 
                         check=True, capture_output=True)
            print("✅ Sample data created")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Could not create sample data: {e}")
    else:
        print("✅ Sample data already exists")

def run_tests():
    """Run basic tests."""
    print("🧪 Running basic tests...")
    try:
        # Test server imports by running from server directory
        server_dir = os.path.abspath("server")
        result = subprocess.run([
            sys.executable, "-c", 
            "from main import app; print('Server imports work')"
        ], cwd=server_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Server imports work")
        else:
            print("⚠️  Server import test failed, but continuing...")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
        
        # Test client imports by running from client directory
        client_dir = os.path.abspath("client")
        result = subprocess.run([
            sys.executable, "-c", 
            "import app; print('Client imports work')"
        ], cwd=client_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Client imports work")
        else:
            print("⚠️  Client import test failed, but continuing...")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
        
        print("✅ Basic tests completed")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not run tests: {e}")
        return True  # Continue anyway

def start_server():
    """Start the FastAPI server."""
    print("🚀 Starting Data Sentinel Server...")
    try:
        # Get absolute path to server directory
        server_dir = os.path.abspath("server")
        
        # Start server from server directory
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], cwd=server_dir)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Check if server is running
        try:
            import requests
            response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully")
                return process
            else:
                print("❌ Server health check failed")
                return None
        except Exception as e:
            print(f"⚠️  Server may not be ready yet: {e}")
            return process
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def start_client():
    """Start the Streamlit client."""
    print("🖥️ Starting Data Sentinel Client...")
    try:
        # Get absolute path to client directory
        client_dir = os.path.abspath("client")
        
        # Start client from client directory
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", 
            "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"
        ], cwd=client_dir)
        
        print("✅ Client started successfully")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start client: {e}")
        return None

def main():
    """Main function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check and install dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Create sample data
    create_sample_data()
    
    # Run tests
    run_tests()
    
    print("\n🚀 Starting Data Sentinel services...")
    print("📡 Server: http://localhost:8000")
    print("🖥️ Client: http://localhost:8501")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services")
    print("=" * 60)
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("❌ Failed to start server")
        sys.exit(1)
    
    # Start client
    client_process = start_client()
    if not client_process:
        print("❌ Failed to start client")
        server_process.terminate()
        sys.exit(1)
    
    # Open browser
    try:
        time.sleep(2)
        webbrowser.open("http://localhost:8501")
    except Exception:
        pass  # Browser opening is optional
    
    try:
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if server_process.poll() is not None:
                print("❌ Server process died")
                break
            if client_process.poll() is not None:
                print("❌ Client process died")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Data Sentinel...")
        
        # Terminate processes
        if server_process:
            server_process.terminate()
        if client_process:
            client_process.terminate()
        
        # Wait for processes to terminate
        if server_process:
            server_process.wait()
        if client_process:
            client_process.wait()
        
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
