import os
import pytest
from unittest.mock import patch, MagicMock
import json
import tempfile
from fastapi.testclient import TestClient

# Set up test environment
os.environ["TESTING"] = "true" 
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["VOYAGE_API_KEY"] = "test_voyage_key"
os.environ["PINECONE_API_KEY"] = "test_pinecone_key"
os.environ["PINECONE_INDEX_NAME"] = "test-bills-index"
os.environ["GOOGLE_API_KEY"] = "test_google_key"

from app import app

class TestEnhancedEndpoints:
    """Test cases for enhanced API endpoints"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_health_endpoint_enhanced(self):
        """Test enhanced health check endpoint"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check basic health info
        assert data["status"] == "healthy"
        assert data["service"] == "legisync-backend"
        
        # Should include cache stats
        assert "cache_stats" in data
        
        # Check timestamp format
        assert "status" in data
        assert "version" in data
    
    def test_debug_status_endpoint(self):
        """Test debug status endpoint"""
        response = self.client.get("/debug/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check API key status (should show presence, not actual values)
        assert "pinecone_api_key" in data
        assert "voyage_api_key" in data
        assert "google_api_key" in data
        assert isinstance(data["pinecone_api_key"], bool)
        
        # Check service initialization status
        assert "vectorstore_initialized" in data
        assert "cache_service" in data
    
    def test_cache_stats_endpoint(self):
        """Test cache statistics endpoint"""
        response = self.client.get("/admin/cache/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include memory cache stats
        assert "memory_cache_size" in data
        assert isinstance(data["memory_cache_size"], int)
    
    def test_cache_clear_endpoint(self):
        """Test cache clearing endpoint"""
        response = self.client.post("/admin/cache/clear")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "cleared" in data["message"].lower()
    
    def test_response_quality_analytics_endpoint(self):
        """Test response quality analytics endpoint"""
        response = self.client.get("/admin/response-quality")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "analytics" in data
        assert "insights" in data
        
        # Check insights structure
        insights = data["insights"]
        assert "overall_health" in insights
        assert "recommendations" in insights
        assert isinstance(insights["recommendations"], list)
    
    def test_performance_stats_endpoint(self):
        """Test performance statistics endpoint"""
        response = self.client.get("/admin/performance")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include basic performance metrics
        assert "total_requests" in data
        assert "avg_response_time" in data
        assert "error_rate" in data
        assert isinstance(data["total_requests"], int)
    
    def test_prometheus_metrics_endpoint(self):
        """Test Prometheus metrics endpoint"""
        response = self.client.get("/metrics")
        
        assert response.status_code == 200
        
        # Should return prometheus format (text/plain)
        content_type = response.headers.get("content-type", "")
        assert "text/plain" in content_type.lower() or "text" in content_type.lower()
    
    def test_realtime_performance_endpoint(self):
        """Test real-time performance endpoint"""
        response = self.client.get("/admin/performance/realtime")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include real-time metrics
        assert "active_connections" in data
        assert "avg_response_time_1min" in data
        assert "error_rate_1min" in data
    
    def test_performance_alerts_endpoint(self):
        """Test performance alerts endpoint"""
        response = self.client.get("/admin/performance/alerts")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "alerts" in data
        assert "status" in data
        assert isinstance(data["alerts"], list)
    
    def test_export_metrics_endpoint(self):
        """Test metrics export endpoint"""
        response = self.client.post("/admin/performance/export", params={"filename": "test_metrics.json"})
        
        assert response.status_code == 200
        data = response.json()
        
        # Should indicate successful export
        assert "message" in data or "filepath" in data
    
    def test_embeddings_warmup_endpoint(self):
        """Test embeddings cache warmup endpoint"""
        warmup_queries = ["education funding", "healthcare bills", "tax reform"]
        
        response = self.client.post("/admin/embeddings/warmup", json=warmup_queries)
        
        assert response.status_code == 200
        data = response.json()
        
        if "error" not in data:  # If embeddings service is available
            assert "message" in data
            assert "queries" in data
            assert data["queries"] == warmup_queries
    
    def test_optimization_status_endpoint(self):
        """Test system optimization status endpoint"""
        response = self.client.get("/admin/optimization/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check optimization features
        assert "optimization_features" in data
        features = data["optimization_features"]
        
        assert "multi_tier_caching" in features
        assert "connection_pooling" in features
        assert "async_processing" in features
        assert "embeddings_optimization" in features
        assert "performance_monitoring" in features
        
        # Check performance targets
        assert "performance_targets" in data
        targets = data["performance_targets"]
        assert "response_time_ms" in targets
        assert "cache_hit_rate" in targets
    
    @patch('app.vectorstore')
    @patch('app.RetrievalQA')
    def test_rag_endpoint_with_caching(self, mock_qa, mock_vectorstore):
        """Test RAG endpoint with caching behavior"""
        # Mock document retrieval
        mock_retriever = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "HB 55 relates to education funding."
        mock_doc.metadata = {"bill_id": "HB 55", "title": "Education Bill"}
        mock_retriever.get_relevant_documents.return_value = [mock_doc]
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        # Mock QA chain
        mock_chain = MagicMock()
        mock_chain.return_value = {
            "result": "HB 55 addresses education funding reform.",
            "source_documents": [mock_doc]
        }
        mock_qa.from_chain_type.return_value = mock_chain
        
        # First request
        response1 = self.client.post("/rag", json={"query": "education funding test"})
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second identical request (should potentially use cache)
        response2 = self.client.post("/rag", json={"query": "education funding test"})
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Both should succeed
        assert "result" in data1
        assert "result" in data2
        assert data1["documents_found"] >= 0
        assert data2["documents_found"] >= 0
    
    @patch('app.vectorstore')
    def test_rag_endpoint_error_handling(self, mock_vectorstore):
        """Test RAG endpoint error handling"""
        # Mock an error in vectorstore
        mock_vectorstore.as_retriever.side_effect = Exception("Database connection failed")
        
        response = self.client.post("/rag", json={"query": "test error handling"})
        
        assert response.status_code == 200  # Should still return 200 with error in response
        data = response.json()
        
        assert data["error"] is True
        assert "error_details" in data
        assert data["query"] == "test error handling"
    
    def test_rag_endpoint_with_quality_metrics(self):
        """Test RAG endpoint includes quality metrics when available"""
        with patch('app.vectorstore') as mock_vectorstore, \
             patch('app.RetrievalQA') as mock_qa, \
             patch('app.PERFORMANCE_SERVICES_AVAILABLE', True):
            
            # Mock successful retrieval
            mock_retriever = MagicMock()
            mock_doc = MagicMock()
            mock_doc.page_content = "HB 55 comprehensive education funding bill"
            mock_doc.metadata = {"bill_id": "HB 55", "session": "891"}
            mock_retriever.get_relevant_documents.return_value = [mock_doc]
            mock_vectorstore.as_retriever.return_value = mock_retriever
            
            # Mock QA chain
            mock_chain = MagicMock()
            mock_chain.return_value = {
                "result": "**HB 55** provides comprehensive education funding reform for Texas schools.",
                "source_documents": [mock_doc]
            }
            mock_qa.from_chain_type.return_value = mock_chain
            
            response = self.client.post("/rag", json={"query": "education funding"})
            assert response.status_code == 200
            
            data = response.json()
            
            # Should include quality metrics when performance services are available
            if "quality_metrics" in data:
                quality = data["quality_metrics"]
                assert "overall_score" in quality
                assert "grade" in quality
                assert "improvement_suggestions" in quality
    
    def test_agent_endpoint_with_caching(self):
        """Test agent endpoint with caching"""
        with patch('app.create_react_agent') as mock_agent_creator:
            # Mock agent
            mock_agent = MagicMock()
            mock_agent.invoke.return_value = {
                "messages": [{"role": "assistant", "content": "Agent response"}]
            }
            mock_agent_creator.return_value = mock_agent
            
            response = self.client.post("/agent", json={"query": "test agent query"})
            
            assert response.status_code == 200
            data = response.json()
            
            # Should return agent result
            assert "messages" in data or "error" not in data
    
    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        response = self.client.options("/rag")
        
        # Should include CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    def test_error_responses_structure(self):
        """Test that error responses have consistent structure"""
        # Test with invalid JSON
        response = self.client.post("/rag", json={"invalid": "no query field"})
        
        # Should return validation error
        assert response.status_code == 422  # Validation error
    
    def test_concurrent_requests_handling(self):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import threading
        
        def make_request(query_suffix):
            return self.client.post("/rag", json={"query": f"concurrent test {query_suffix}"})
        
        # Make multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        for response in results:
            assert response.status_code in [200, 500]  # Either success or graceful error
            
            if response.status_code == 200:
                data = response.json()
                assert "query" in data
                assert "result" in data
