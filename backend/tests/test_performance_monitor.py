import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import time
import asyncio

# Set up test environment
os.environ["TESTING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from performance_monitor import PerformanceMonitor

class TestPerformanceMonitor:
    """Test cases for the performance monitoring service"""
    
    def test_performance_monitor_initialization(self):
        """Test performance monitor initialization"""
        monitor = PerformanceMonitor()
        
        assert monitor.metrics is not None
        assert monitor.requests == []
        assert monitor.monitoring_active is False
    
    def test_record_request(self):
        """Test recording request metrics"""
        monitor = PerformanceMonitor()
        
        # Record a successful request
        monitor.record_request(
            endpoint="/rag",
            query="test query",
            duration_ms=500.0,
            cache_hit=False,
            documents_found=3,
            error=False,
            status_code=200
        )
        
        # Check that metrics were recorded
        assert len(monitor.requests) == 1
        request = monitor.requests[0]
        
        assert request["endpoint"] == "/rag"
        assert request["query"] == "test query"
        assert request["duration_ms"] == 500.0
        assert request["cache_hit"] is False
        assert request["documents_found"] == 3
        assert request["error"] is False
        assert request["status_code"] == 200
        assert "timestamp" in request
    
    def test_record_error_request(self):
        """Test recording error request metrics"""
        monitor = PerformanceMonitor()
        
        # Record an error request
        monitor.record_request(
            endpoint="/rag",
            query="failing query",
            duration_ms=1000.0,
            cache_hit=False,
            documents_found=0,
            error=True,
            status_code=500
        )
        
        # Check that error was recorded
        assert len(monitor.requests) == 1
        request = monitor.requests[0]
        
        assert request["error"] is True
        assert request["status_code"] == 500
        assert request["duration_ms"] == 1000.0
    
    def test_get_stats(self):
        """Test getting performance statistics"""
        monitor = PerformanceMonitor()
        
        # Add some test data
        for i in range(5):
            monitor.record_request(
                endpoint="/rag",
                query=f"query {i}",
                duration_ms=100.0 + (i * 50),
                cache_hit=(i % 2 == 0),
                documents_found=i + 1,
                error=(i == 4),  # Last one is an error
                status_code=500 if i == 4 else 200
            )
        
        stats = monitor.get_stats()
        
        assert stats["total_requests"] == 5
        assert stats["error_rate"] == 0.2  # 1 error out of 5
        assert stats["avg_response_time"] == (100 + 150 + 200 + 250 + 300) / 5
        assert stats["cache_hit_rate"] == 0.6  # 3 cache hits out of 5
        assert "recent_errors" in stats
        assert len(stats["recent_errors"]) == 1  # Should have 1 error
    
    def test_get_real_time_stats(self):
        """Test real-time statistics"""
        monitor = PerformanceMonitor()
        
        # Add recent requests (within last minute)
        current_time = time.time()
        for i in range(3):
            monitor.record_request(
                endpoint="/rag",
                query=f"recent query {i}",
                duration_ms=200.0,
                cache_hit=False,
                documents_found=1,
                error=False,
                status_code=200
            )
        
        real_time_stats = monitor.get_real_time_stats()
        
        assert "requests_per_minute" in real_time_stats
        assert "avg_response_time_1min" in real_time_stats
        assert "error_rate_1min" in real_time_stats
        assert "active_connections" in real_time_stats
    
    def test_performance_summary(self):
        """Test performance summary generation"""
        monitor = PerformanceMonitor()
        
        # Add varied test data
        for i in range(10):
            duration = 1000 if i > 7 else 200  # Some slow requests
            error = i == 9  # One error
            
            monitor.record_request(
                endpoint="/rag",
                query=f"query {i}",
                duration_ms=duration,
                cache_hit=False,
                documents_found=1,
                error=error,
                status_code=500 if error else 200
            )
        
        summary = monitor.get_performance_summary(hours=24)
        
        assert "total_requests" in summary
        assert "avg_response_time" in summary
        assert "error_rate" in summary
        assert "performance_alerts" in summary
        
        # Should detect slow response times
        alerts = summary["performance_alerts"]
        slow_alert = next((alert for alert in alerts if "response time" in alert["message"]), None)
        assert slow_alert is not None
        assert slow_alert["level"] == "warning"
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self):
        """Test starting and stopping background monitoring"""
        monitor = PerformanceMonitor()
        
        # Start monitoring with very short interval for testing
        await monitor.start_monitoring(interval_seconds=0.1)
        assert monitor.monitoring_active is True
        
        # Let it run briefly
        await asyncio.sleep(0.2)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        assert monitor.monitoring_active is False
    
    def test_detect_performance_issues(self):
        """Test performance issue detection"""
        monitor = PerformanceMonitor()
        
        # Add requests with various performance characteristics
        test_cases = [
            {"duration": 5000, "error": False},  # Very slow
            {"duration": 3000, "error": False},  # Slow
            {"duration": 100, "error": True},    # Fast but error
            {"duration": 100, "error": True},    # Another error
            {"duration": 200, "error": False},   # Normal
        ]
        
        for i, case in enumerate(test_cases):
            monitor.record_request(
                endpoint="/rag",
                query=f"test {i}",
                duration_ms=case["duration"],
                cache_hit=False,
                documents_found=1,
                error=case["error"],
                status_code=500 if case["error"] else 200
            )
        
        summary = monitor.get_performance_summary(hours=1)
        alerts = summary["performance_alerts"]
        
        # Should detect multiple issues
        assert len(alerts) > 0
        
        # Check for specific alert types
        alert_messages = [alert["message"] for alert in alerts]
        assert any("response time" in msg for msg in alert_messages)
        assert any("error rate" in msg for msg in alert_messages)
    
    def test_export_metrics(self):
        """Test metrics export functionality"""
        import tempfile
        import json
        import os
        
        monitor = PerformanceMonitor()
        
        # Add some test data
        monitor.record_request(
            endpoint="/rag",
            query="export test",
            duration_ms=300.0,
            cache_hit=True,
            documents_found=2,
            error=False,
            status_code=200
        )
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            monitor.export_metrics(temp_path)
            
            # Verify file was created and contains valid JSON
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                exported_data = json.load(f)
            
            assert "performance_summary" in exported_data
            assert "detailed_metrics" in exported_data
            assert exported_data["total_requests"] == 1
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
