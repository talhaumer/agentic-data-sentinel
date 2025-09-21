"""LangChain observability configuration for LangGraph agents."""

import os
from typing import Optional
from langsmith import Client
from langchain_core.tracers import LangChainTracer
from langchain_core.callbacks import BaseCallbackHandler

# Global LangSmith client
_langsmith_client: Optional[Client] = None

def setup_tracing():
    """Setup LangChain tracing with LangSmith."""
    global _langsmith_client
    
    try:
        # Initialize LangSmith client
        api_key = os.getenv("LANGCHAIN_API_KEY", "")
        if api_key:
            _langsmith_client = Client(api_key=api_key)
            print("✅ LangSmith tracing initialized successfully")
            return _langsmith_client
        else:
            print("⚠️ LANGCHAIN_API_KEY not found, continuing without tracing...")
            return None
        
    except Exception as e:
        print(f"⚠️ LangSmith initialization failed: {e}")
        print("Continuing without tracing...")
        return None

def get_tracer(name: str):
    """Get a tracer instance."""
    global _langsmith_client
    if _langsmith_client:
        return LangChainTracer(project_name="data-sentinel")
    else:
        # Return a no-op tracer if LangSmith is not available
        return NoOpTracer()

class NoOpTracer:
    """No-op tracer for when LangSmith is not available."""
    
    def start_as_current_span(self, name: str, **kwargs):
        """No-op span context manager."""
        return NoOpSpan()

class NoOpSpan:
    """No-op span for when tracing is disabled."""
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def set_attribute(self, key: str, value):
        pass
    
    def record_exception(self, exception):
        pass
