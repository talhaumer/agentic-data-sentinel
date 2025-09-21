"""Simple metrics collection without external dependencies."""

import time
from typing import Dict, Any
from collections import defaultdict, deque
from datetime import datetime

# In-memory metrics storage
_metrics = {
    'workflows': defaultdict(int),
    'anomalies': defaultdict(int),
    'health_scores': {},
    'api_requests': defaultdict(int),
    'api_durations': deque(maxlen=1000)
}

# System info
system_info = {
    'version': '1.0.0',
    'environment': 'development',
    'start_time': datetime.utcnow().isoformat()
}

class MetricsCollector:
    """Simple metrics collection helper class."""
    
    @staticmethod
    def record_workflow(dataset_id: int, status: str, duration: float):
        """Record workflow metrics."""
        key = f"{status}_{dataset_id}"
        _metrics['workflows'][key] += 1
        
        # Store duration for analysis
        _metrics['api_durations'].append({
            'type': 'workflow',
            'dataset_id': dataset_id,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @staticmethod
    def record_anomaly(anomaly_type: str, severity: int):
        """Record anomaly detection metrics."""
        key = f"{anomaly_type}_{severity}"
        _metrics['anomalies'][key] += 1
    
    @staticmethod
    def record_health_score(dataset_id: int, score: float):
        """Record health score metrics."""
        _metrics['health_scores'][str(dataset_id)] = {
            'score': score,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def record_api_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record API request metrics."""
        key = f"{method}_{endpoint}_{status_code}"
        _metrics['api_requests'][key] += 1
        
        # Store duration for analysis
        _metrics['api_durations'].append({
            'type': 'api',
            'method': method,
            'endpoint': endpoint,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @staticmethod
    def get_metrics() -> Dict[str, Any]:
        """Get current metrics."""
        return {
            'workflows': dict(_metrics['workflows']),
            'anomalies': dict(_metrics['anomalies']),
            'health_scores': _metrics['health_scores'],
            'api_requests': dict(_metrics['api_requests']),
            'system_info': system_info,
            'total_metrics': {
                'total_workflows': sum(_metrics['workflows'].values()),
                'total_anomalies': sum(_metrics['anomalies'].values()),
                'total_api_requests': sum(_metrics['api_requests'].values())
            }
        }
