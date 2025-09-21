"""OpenTelemetry tracing configuration."""

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

def setup_tracing():
    """Setup OpenTelemetry tracing."""
    # Create resource
    resource = Resource.create({
        "service.name": "data-sentinel",
        "service.version": "1.0.0",
        "deployment.environment": os.getenv("ENVIRONMENT", "development")
    })
    
    # Create tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    # Add Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("JAEGER_AGENT_HOST", "localhost"),
        agent_port=int(os.getenv("JAEGER_AGENT_PORT", "14268")),
    )
    
    # Add span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Instrument libraries
    FastAPIInstrumentor.instrument()
    SQLAlchemyInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    
    return trace.get_tracer(__name__)

def get_tracer(name: str):
    """Get a tracer instance."""
    return trace.get_tracer(name)
