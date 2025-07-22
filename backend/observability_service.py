# backend/observability_service.py
"""
Enterprise-grade OpenTelemetry + Grafana integration for LegisSync
Cost-optimized observability with comprehensive metrics and tracing
"""

import logging
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager

from opentelemetry import trace, metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import os

logger = logging.getLogger(__name__)

class LegisyncObservability:
    """
    Comprehensive observability service with OpenTelemetry + Grafana
    Designed for cost-effective production monitoring
    """
    
    def __init__(
        self,
        service_name: str = "legisync-backend",
        prometheus_port: int = 8001,
        jaeger_endpoint: str = None,
        enable_prometheus: bool = True,
        enable_jaeger: bool = True
    ):
        self.service_name = service_name
        self.prometheus_port = prometheus_port
        self.jaeger_endpoint = jaeger_endpoint or os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
        
        # Initialize providers
        self._setup_tracing(enable_jaeger)
        self._setup_metrics(enable_prometheus)
        self._setup_custom_metrics()
        
        logger.info(f"✅ Observability initialized for {service_name}")
        
    def _setup_tracing(self, enable_jaeger: bool):
        """Setup distributed tracing with Jaeger"""
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENVIRONMENT", "development")
        })
        
        # Set up tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))
        self.tracer = trace.get_tracer(__name__)
        
        if enable_jaeger:
            try:
                jaeger_exporter = JaegerExporter(
                    endpoint=self.jaeger_endpoint,
                    collector_endpoint=self.jaeger_endpoint,
                )
                span_processor = BatchSpanProcessor(jaeger_exporter)
                trace.get_tracer_provider().add_span_processor(span_processor)
                logger.info("✅ Jaeger tracing enabled")
            except Exception as e:
                logger.warning(f"⚠️ Jaeger setup failed: {e}")
    
    def _setup_metrics(self, enable_prometheus: bool):
        """Setup metrics collection with Prometheus"""
        if enable_prometheus:
            try:
                # Start Prometheus metrics server
                start_http_server(self.prometheus_port)
                
                # Set up metrics provider
                reader = PrometheusMetricReader()
                metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))
                self.meter = metrics.get_meter(__name__)
                
                logger.info(f"✅ Prometheus metrics server started on port {self.prometheus_port}")
            except Exception as e:
                logger.warning(f"⚠️ Prometheus setup failed: {e}")
                self.meter = metrics.get_meter(__name__)
        else:
            self.meter = metrics.get_meter(__name__)
    
    def _setup_custom_metrics(self):
        """Setup custom business metrics for LegisSync"""
        
        # Request metrics
        self.request_counter = self.meter.create_counter(
            "legisync_requests_total",
            description="Total number of requests by endpoint"
        )
        
        self.request_duration = self.meter.create_histogram(
            "legisync_request_duration_seconds",
            description="Request duration in seconds"
        )
        
        # Cache metrics
        self.cache_operations = self.meter.create_counter(
            "legisync_cache_operations_total",
            description="Cache operations (hits/misses) by layer"
        )
        
        # RAG-specific metrics
        self.rag_queries = self.meter.create_counter(
            "legisync_rag_queries_total",
            description="RAG queries by type and result"
        )
        
        self.documents_retrieved = self.meter.create_histogram(
            "legisync_documents_retrieved",
            description="Number of documents retrieved per query"
        )
        
        self.embedding_operations = self.meter.create_counter(
            "legisync_embedding_operations_total",
            description="Embedding operations by type"
        )
        
        # System metrics
        self.active_connections = self.meter.create_up_down_counter(
            "legisync_active_connections",
            description="Number of active database connections"
        )
        
        self.cache_size = self.meter.create_up_down_counter(
            "legisync_cache_size",
            description="Current cache size by layer"
        )
        
        # Cost tracking metrics
        self.api_calls = self.meter.create_counter(
            "legisync_api_calls_total",
            description="External API calls by provider"
        )
        
        self.token_usage = self.meter.create_counter(
            "legisync_tokens_used_total",
            description="Token usage by model and operation"
        )
        
        logger.info("✅ Custom metrics initialized")
    
    @contextmanager
    def trace_operation(self, operation_name: str, **attributes):
        """Context manager for tracing operations"""
        start_time = time.time()
        
        with self.tracer.start_as_current_span(operation_name) as span:
            # Set custom attributes
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
            
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("duration.seconds", duration)
    
    def record_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        labels = {
            "endpoint": endpoint,
            "method": method,
            "status_code": str(status_code)
        }
        
        self.request_counter.add(1, labels)
        self.request_duration.record(duration, labels)
    
    def record_cache_operation(self, operation: str, layer: str, hit: bool = None):
        """Record cache operation metrics"""
        labels = {
            "operation": operation,
            "layer": layer
        }
        
        if hit is not None:
            labels["result"] = "hit" if hit else "miss"
        
        self.cache_operations.add(1, labels)
    
    def record_rag_query(self, query_type: str, documents_found: int, cached: bool, error: bool = False):
        """Record RAG query metrics"""
        labels = {
            "query_type": query_type,
            "cached": str(cached),
            "error": str(error)
        }
        
        self.rag_queries.add(1, labels)
        self.documents_retrieved.record(documents_found, {"query_type": query_type})
    
    def record_embedding_operation(self, operation: str, model: str, count: int):
        """Record embedding operation metrics"""
        labels = {
            "operation": operation,
            "model": model
        }
        
        self.embedding_operations.add(count, labels)
    
    def record_api_call(self, provider: str, operation: str, tokens_used: int = 0):
        """Record external API call metrics for cost tracking"""
        api_labels = {
            "provider": provider,
            "operation": operation
        }
        
        self.api_calls.add(1, api_labels)
        
        if tokens_used > 0:
            token_labels = {
                "provider": provider,
                "model": operation  # operation often contains model info
            }
            self.token_usage.add(tokens_used, token_labels)
    
    def update_connection_count(self, count: int, pool_name: str):
        """Update active connection metrics"""
        self.active_connections.add(count, {"pool": pool_name})
    
    def update_cache_size(self, size: int, cache_layer: str):
        """Update cache size metrics"""
        self.cache_size.add(size, {"layer": cache_layer})
    
    def instrument_fastapi(self, app):
        """Auto-instrument FastAPI application"""
        FastAPIInstrumentor.instrument_app(app, tracer_provider=trace.get_tracer_provider())
        RequestsInstrumentor().instrument()
        logger.info("✅ FastAPI auto-instrumentation enabled")
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get current observability health status"""
        return {
            "tracing_enabled": trace.get_tracer_provider() is not None,
            "metrics_enabled": self.meter is not None,
            "prometheus_port": self.prometheus_port,
            "service_name": self.service_name,
            "jaeger_endpoint": self.jaeger_endpoint
        }

# Global observability instance
observability = LegisyncObservability()
