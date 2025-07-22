# backend/performance_monitor.py
import asyncio
import logging
import time
import psutil
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    timestamp: float
    endpoint: str
    query: str
    duration_ms: float
    cache_hit: bool
    documents_found: int
    error: bool
    status_code: int
    user_agent: Optional[str] = None

@dataclass
class SystemMetrics:
    """System resource metrics"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    active_connections: int
    cache_size: int
    thread_count: int

class PerformanceMonitor:
    """
    Comprehensive performance monitoring service for RAG optimizations
    """
    
    def __init__(self, max_request_history: int = 10000):
        self.max_request_history = max_request_history
        
        # Request tracking
        self.request_history = deque(maxlen=max_request_history)
        self.request_lock = threading.RLock()
        
        # System metrics
        self.system_history = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self.system_lock = threading.RLock()
        
        # Performance statistics
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_errors": 0,
            "avg_response_time_ms": 0.0,
            "requests_per_minute": 0.0,
            "active_connections": 0
        }
        
        # Endpoint-specific metrics
        self.endpoint_stats = defaultdict(lambda: {
            "requests": 0,
            "avg_duration_ms": 0.0,
            "errors": 0,
            "cache_hits": 0,
            "cache_misses": 0
        })
        
        # Monitoring control
        self._monitoring = False
        self._monitor_task = None
        
        # Performance thresholds
        self.thresholds = {
            "response_time_ms": 2000,  # 2 seconds
            "cache_hit_rate": 0.7,     # 70%
            "error_rate": 0.05,        # 5%
            "cpu_usage": 80.0,         # 80%
            "memory_usage": 85.0       # 85%
        }
    
    def record_request(
        self,
        endpoint: str,
        query: str,
        duration_ms: float,
        cache_hit: bool = False,
        documents_found: int = 0,
        error: bool = False,
        status_code: int = 200,
        user_agent: str = None
    ):
        """Record a request for performance analysis"""
        metrics = RequestMetrics(
            timestamp=time.time(),
            endpoint=endpoint,
            query=query[:100],  # Truncate long queries
            duration_ms=duration_ms,
            cache_hit=cache_hit,
            documents_found=documents_found,
            error=error,
            status_code=status_code,
            user_agent=user_agent
        )
        
        with self.request_lock:
            self.request_history.append(metrics)
            
            # Update global stats
            self.stats["total_requests"] += 1
            if cache_hit:
                self.stats["cache_hits"] += 1
            else:
                self.stats["cache_misses"] += 1
            
            if error:
                self.stats["total_errors"] += 1
            
            # Update endpoint stats
            endpoint_stat = self.endpoint_stats[endpoint]
            endpoint_stat["requests"] += 1
            if cache_hit:
                endpoint_stat["cache_hits"] += 1
            else:
                endpoint_stat["cache_misses"] += 1
            if error:
                endpoint_stat["errors"] += 1
            
            # Update averages
            self._update_averages(endpoint, duration_ms)
    
    def _update_averages(self, endpoint: str, duration_ms: float):
        """Update running averages for performance metrics"""
        # Global average
        total_requests = self.stats["total_requests"]
        if total_requests == 1:
            self.stats["avg_response_time_ms"] = duration_ms
        else:
            current_avg = self.stats["avg_response_time_ms"]
            self.stats["avg_response_time_ms"] = (
                (current_avg * (total_requests - 1) + duration_ms) / total_requests
            )
        
        # Endpoint average
        endpoint_stat = self.endpoint_stats[endpoint]
        endpoint_requests = endpoint_stat["requests"]
        if endpoint_requests == 1:
            endpoint_stat["avg_duration_ms"] = duration_ms
        else:
            current_avg = endpoint_stat["avg_duration_ms"]
            endpoint_stat["avg_duration_ms"] = (
                (current_avg * (endpoint_requests - 1) + duration_ms) / endpoint_requests
            )
    
    def _record_system_metrics(self):
        """Record current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            process = psutil.Process()
            
            metrics = SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                active_connections=len(process.connections()),
                cache_size=len(self.request_history),
                thread_count=process.num_threads()
            )
            
            with self.system_lock:
                self.system_history.append(metrics)
                
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start background system monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        
        async def monitor_loop():
            while self._monitoring:
                self._record_system_metrics()
                await asyncio.sleep(interval_seconds)
        
        self._monitor_task = asyncio.create_task(monitor_loop())
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        cutoff_time = time.time() - (hours * 3600)
        
        with self.request_lock:
            recent_requests = [
                r for r in self.request_history 
                if r.timestamp >= cutoff_time
            ]
        
        if not recent_requests:
            return {"message": "No recent requests found"}
        
        # Calculate metrics
        total_requests = len(recent_requests)
        cache_hits = sum(1 for r in recent_requests if r.cache_hit)
        errors = sum(1 for r in recent_requests if r.error)
        durations = [r.duration_ms for r in recent_requests]
        
        # Time-based analysis
        requests_per_hour = total_requests / hours
        cache_hit_rate = cache_hits / total_requests if total_requests > 0 else 0
        error_rate = errors / total_requests if total_requests > 0 else 0
        
        # Response time analysis
        avg_duration = sum(durations) / len(durations) if durations else 0
        p95_duration = sorted(durations)[int(0.95 * len(durations))] if durations else 0
        p99_duration = sorted(durations)[int(0.99 * len(durations))] if durations else 0
        
        return {
            "time_period_hours": hours,
            "total_requests": total_requests,
            "requests_per_hour": requests_per_hour,
            "cache_performance": {
                "hit_rate": cache_hit_rate,
                "hits": cache_hits,
                "misses": total_requests - cache_hits
            },
            "response_times": {
                "average_ms": avg_duration,
                "p95_ms": p95_duration,
                "p99_ms": p99_duration
            },
            "error_analysis": {
                "error_rate": error_rate,
                "total_errors": errors
            },
            "endpoint_breakdown": dict(self.endpoint_stats),
            "performance_alerts": self._get_performance_alerts()
        }
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get current real-time performance statistics"""
        # Recent requests (last 5 minutes)
        recent_cutoff = time.time() - 300
        
        with self.request_lock:
            recent_requests = [
                r for r in self.request_history 
                if r.timestamp >= recent_cutoff
            ]
        
        # Calculate real-time metrics
        current_rps = len(recent_requests) / 5 if recent_requests else 0  # requests per second
        recent_avg_duration = (
            sum(r.duration_ms for r in recent_requests) / len(recent_requests) 
            if recent_requests else 0
        )
        
        # System metrics (latest)
        with self.system_lock:
            latest_system = self.system_history[-1] if self.system_history else None
        
        return {
            "current_time": datetime.now().isoformat(),
            "requests_per_second": current_rps,
            "avg_response_time_ms": recent_avg_duration,
            "active_requests": len(recent_requests),
            "system_metrics": asdict(latest_system) if latest_system else None,
            "cache_stats": {
                "hit_rate": self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"]) if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0 else 0,
                "total_hits": self.stats["cache_hits"],
                "total_misses": self.stats["cache_misses"]
            }
        }
    
    def _get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance issues and generate alerts"""
        alerts = []
        
        # Check cache hit rate
        total_cache_requests = self.stats["cache_hits"] + self.stats["cache_misses"]
        if total_cache_requests > 0:
            hit_rate = self.stats["cache_hits"] / total_cache_requests
            if hit_rate < self.thresholds["cache_hit_rate"]:
                alerts.append({
                    "type": "cache_performance",
                    "severity": "warning",
                    "message": f"Cache hit rate ({hit_rate:.2%}) below threshold ({self.thresholds['cache_hit_rate']:.2%})"
                })
        
        # Check average response time
        if self.stats["avg_response_time_ms"] > self.thresholds["response_time_ms"]:
            alerts.append({
                "type": "response_time",
                "severity": "warning",
                "message": f"Average response time ({self.stats['avg_response_time_ms']:.0f}ms) above threshold ({self.thresholds['response_time_ms']}ms)"
            })
        
        # Check error rate
        if self.stats["total_requests"] > 0:
            error_rate = self.stats["total_errors"] / self.stats["total_requests"]
            if error_rate > self.thresholds["error_rate"]:
                alerts.append({
                    "type": "error_rate",
                    "severity": "error",
                    "message": f"Error rate ({error_rate:.2%}) above threshold ({self.thresholds['error_rate']:.2%})"
                })
        
        return alerts
    
    def export_metrics(self, filepath: str):
        """Export all metrics to JSON file for analysis"""
        with self.request_lock, self.system_lock:
            data = {
                "export_timestamp": datetime.now().isoformat(),
                "stats": self.stats,
                "endpoint_stats": dict(self.endpoint_stats),
                "request_history": [asdict(r) for r in self.request_history],
                "system_history": [asdict(s) for s in self.system_history]
            }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Metrics exported to {filepath}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
