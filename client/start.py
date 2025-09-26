"""Start the Data Sentinel client."""

import subprocess
import sys
import os

def main():
    """Start the Streamlit client."""
    try:
        # Change to client directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\nShutting down client...")
    except Exception as e:
        print(f"Error starting client: {e}")

if __name__ == "__main__":
    main()
