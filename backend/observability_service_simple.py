"""
Simplified Observability Service for LegisSync
Provides metrics collection using prometheus_client directly to avoid compatibility issues
"""

import time
import logging
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

class SimplifiedObservabilityService:
    """Simplified observability service using prometheus_client directly"""
    
    def __init__(self):
        """Initialize the observability service with basic metrics"""
        self.initialized = False
        self._setup_metrics()
        
    def _setup_metrics(self):
        """Set up Prometheus metrics"""
        try:
            # Request metrics
            self.rag_query_counter = Counter(
                'rag_query_total',
                'Total number of RAG queries',
                ['cache_hit', 'status', 'documents_found']
            )
            
            self.rag_query_duration = Histogram(
                'rag_query_duration_ms',
                'RAG query duration in milliseconds',
                ['cache_hit']
            )
            
            self.rag_documents_found = Gauge(
                'rag_documents_found',
                'Number of documents found per query',
                ['query_type']
            )
            
            self.cache_hits_counter = Counter(
                'cache_hits_total',
                'Total cache hits',
                ['endpoint']
            )
            
            self.rag_errors_counter = Counter(
                'rag_errors_total',
                'Total RAG errors',
                ['endpoint', 'error_type']
            )
            
            self.health_check_counter = Counter(
                'health_check_total',
                'Total health checks',
                ['status']
            )
            
            # System metrics
            self.active_requests = Gauge(
                'active_requests',
                'Number of active requests'
            )
            
            self.initialized = True
            logger.info("✅ Simplified observability service initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize observability: {e}")
            self.initialized = False
    
    def instrument_fastapi(self, app):
        """Add basic instrumentation to FastAPI app"""
        if not self.initialized:
            logger.warning("⚠️ Observability service not initialized, skipping instrumentation")
            return
            
        # Note: Middleware should be added before the app starts, not here
        logger.info("✅ FastAPI observability service registered")
    
    def get_middleware(self):
        """Get the middleware function for manual addition to FastAPI app"""
        if not self.initialized:
            return None
            
        async def add_prometheus_middleware(request, call_next):
            start_time = time.time()
            self.active_requests.inc()
            
            try:
                response = await call_next(request)
                return response
            finally:
                self.active_requests.dec()
        
        return add_prometheus_middleware
    
    def record_custom_metric(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a custom metric"""
        if not self.initialized:
            return
            
        labels = labels or {}
        
        try:
            if metric_name == "rag_query_total":
                self.rag_query_counter.labels(**labels).inc(value)
            elif metric_name == "rag_query_duration_ms":
                self.rag_query_duration.labels(**labels).observe(value)
            elif metric_name == "rag_documents_found":
                self.rag_documents_found.labels(**labels).set(value)
            elif metric_name == "cache_hits_total":
                self.cache_hits_counter.labels(**labels).inc(value)
            elif metric_name == "rag_errors_total":
                self.rag_errors_counter.labels(**labels).inc(value)
            elif metric_name == "health_check_total":
                self.health_check_counter.labels(**labels).inc(value)
                
        except Exception as e:
            logger.error(f"❌ Failed to record metric {metric_name}: {e}")
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        if not self.initialized:
            return "# Observability service not initialized\n"
        
        try:
            return generate_latest().decode('utf-8')
        except Exception as e:
            logger.error(f"❌ Failed to generate metrics: {e}")
            return f"# Error generating metrics: {e}\n"
    
    def get_content_type(self) -> str:
        """Get the Prometheus content type"""
        return CONTENT_TYPE_LATEST
    
    def get_stats(self) -> Dict[str, Any]:
        """Get observability service stats"""
        return {
            "initialized": self.initialized,
            "metrics_available": self.initialized,
            "service": "simplified_prometheus"
        }

# Create global instance
observability = SimplifiedObservabilityService()
