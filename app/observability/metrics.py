"""Prometheus metrics collection."""

from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry
import time

# Create a custom registry
registry = CollectorRegistry()

# Define metrics
workflow_counter = Counter(
    'data_sentinel_workflows_total',
    'Total number of workflows executed',
    ['status', 'dataset_id'],
    registry=registry
)

workflow_duration = Histogram(
    'data_sentinel_workflow_duration_seconds',
    'Duration of workflow execution',
    ['dataset_id'],
    registry=registry
)

anomalies_detected = Counter(
    'data_sentinel_anomalies_detected_total',
    'Total number of anomalies detected',
    ['anomaly_type', 'severity'],
    registry=registry
)

health_score_gauge = Gauge(
    'data_sentinel_health_score',
    'Current health score of datasets',
    ['dataset_id'],
    registry=registry
)

api_requests = Counter(
    'data_sentinel_api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

api_duration = Histogram(
    'data_sentinel_api_duration_seconds',
    'Duration of API requests',
    ['method', 'endpoint'],
    registry=registry
)

# System info
system_info = Info(
    'data_sentinel_system',
    'System information',
    registry=registry
)

system_info.info({
    'version': '1.0.0',
    'environment': 'development'
})

class MetricsCollector:
    """Metrics collection helper class."""
    
    @staticmethod
    def record_workflow(dataset_id: int, status: str, duration: float):
        """Record workflow metrics."""
        workflow_counter.labels(status=status, dataset_id=str(dataset_id)).inc()
        workflow_duration.labels(dataset_id=str(dataset_id)).observe(duration)
    
    @staticmethod
    def record_anomaly(anomaly_type: str, severity: int):
        """Record anomaly detection metrics."""
        anomalies_detected.labels(
            anomaly_type=anomaly_type, 
            severity=str(severity)
        ).inc()
    
    @staticmethod
    def record_health_score(dataset_id: int, score: float):
        """Record health score metrics."""
        health_score_gauge.labels(dataset_id=str(dataset_id)).set(score)
    
    @staticmethod
    def record_api_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record API request metrics."""
        api_requests.labels(
            method=method, 
            endpoint=endpoint, 
            status_code=str(status_code)
        ).inc()
        api_duration.labels(method=method, endpoint=endpoint).observe(duration)
