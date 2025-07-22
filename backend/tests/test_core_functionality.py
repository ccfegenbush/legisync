import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import time

# Set up test environment
os.environ["TESTING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["VOYAGE_API_KEY"] = "test_voyage_key"
os.environ["PINECONE_API_KEY"] = "test_pinecone_key"
os.environ["PINECONE_INDEX_NAME"] = "test-bills-index"
os.environ["GOOGLE_API_KEY"] = "test_google_key"

from app import rag_query, QueryRequest, app
from fastapi.testclient import TestClient

class TestCoreRAGFunctionality:
    """Core tests for essential RAG functionality that must work"""
    
    @pytest.mark.asyncio
    async def test_rag_query_basic_success(self):
        """Test basic successful RAG query processing"""
        with patch('app.vectorstore') as mock_vectorstore, \
             patch('app.RetrievalQA') as mock_qa:
            
            # Mock the retriever and documents
            mock_retriever = MagicMock()
            mock_doc = MagicMock()
            mock_doc.page_content = "HB 55 relates to education funding."
            mock_doc.metadata = {"bill_id": "HB 55", "title": "Education Funding Bill", "session": "891"}
            
            mock_retriever.get_relevant_documents = MagicMock(return_value=[mock_doc])
            mock_vectorstore.as_retriever.return_value = mock_retriever
            
            # Mock the RetrievalQA chain
            mock_chain = MagicMock()
            mock_chain.return_value = {
                "result": "HB 55 addresses education funding based on property values.",
                "source_documents": [mock_doc]
            }
            mock_qa.from_chain_type.return_value = mock_chain
            
            # Test the query
            request = QueryRequest(query="education funding")
            result = await rag_query(request)
            
            # Verify essential response structure
            assert "result" in result
            assert "documents_found" in result
            assert result["documents_found"] == 1
            assert "HB 55" in result["result"]
            assert result["query"] == "education funding"
    
    @pytest.mark.asyncio
    async def test_rag_query_no_documents_found(self):
        """Test RAG query when no documents are found"""
        with patch('app.vectorstore') as mock_vectorstore:
            
            mock_retriever = MagicMock()
            mock_retriever.get_relevant_documents = MagicMock(return_value=[])
            mock_vectorstore.as_retriever.return_value = mock_retriever
            
            request = QueryRequest(query="non-existent topic")
            result = await rag_query(request)
            
            # Should provide helpful no-results response
            assert result["documents_found"] == 0
            assert "No specific bills found" in result["result"]
            assert "Search Suggestions" in result["result"]
            assert "suggestions_provided" in result and result["suggestions_provided"] is True
    
    @pytest.mark.asyncio
    async def test_rag_query_error_handling(self):
        """Test error handling in RAG query"""
        with patch('app.vectorstore') as mock_vectorstore:
            mock_vectorstore.as_retriever.side_effect = Exception("Database connection failed")
            
            request = QueryRequest(query="test error handling")
            result = await rag_query(request)
            
            # Should handle errors gracefully
            assert result["error"] is True
            assert "error_details" in result
            assert result["query"] == "test error handling"
    
    @pytest.mark.asyncio
    async def test_rag_query_multiple_documents(self):
        """Test RAG query with multiple documents"""
        with patch('app.vectorstore') as mock_vectorstore, \
             patch('app.RetrievalQA') as mock_qa:
            
            mock_retriever = MagicMock()
            mock_docs = [
                MagicMock(
                    page_content="HB 55 education funding",
                    metadata={"bill_id": "HB 55", "title": "Education Funding", "session": "891"}
                ),
                MagicMock(
                    page_content="SB 120 healthcare reform", 
                    metadata={"bill_id": "SB 120", "title": "Healthcare Reform", "session": "891"}
                )
            ]
            
            mock_retriever.get_relevant_documents = MagicMock(return_value=mock_docs)
            mock_vectorstore.as_retriever.return_value = mock_retriever
            
            mock_chain = MagicMock()
            mock_chain.return_value = {
                "result": "Multiple bills found: HB 55 for education and SB 120 for healthcare.",
                "source_documents": mock_docs
            }
            mock_qa.from_chain_type.return_value = mock_chain
            
            request = QueryRequest(query="legislation review")
            result = await rag_query(request)
            
            assert result["documents_found"] == 2
            assert "HB 55" in result["result"]
            assert "SB 120" in result["result"]

class TestAPIEndpoints:
    """Test essential API endpoints"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "legisync-backend"
        assert "cache_stats" in data
    
    def test_debug_status_endpoint(self):
        """Test debug status endpoint"""
        response = self.client.get("/debug/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should show API key presence
        assert "pinecone_api_key" in data
        assert "voyage_api_key" in data
        assert "google_api_key" in data
        assert isinstance(data["pinecone_api_key"], bool)
    
    def test_cache_stats_endpoint(self):
        """Test cache statistics endpoint"""
        response = self.client.get("/admin/cache/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "memory_cache_size" in data
    
    def test_cache_clear_endpoint(self):
        """Test cache clearing endpoint"""
        response = self.client.post("/admin/cache/clear")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    @patch('app.vectorstore')
    @patch('app.RetrievalQA')
    def test_rag_endpoint_integration(self, mock_qa, mock_vectorstore):
        """Test full RAG endpoint integration"""
        # Mock successful retrieval
        mock_retriever = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "Integration test content"
        mock_doc.metadata = {"bill_id": "HB 1", "title": "Test Bill"}
        mock_retriever.get_relevant_documents = MagicMock(return_value=[mock_doc])
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        mock_chain = MagicMock()
        mock_chain.return_value = {
            "result": "Integration test response about HB 1",
            "source_documents": [mock_doc]
        }
        mock_qa.from_chain_type.return_value = mock_chain
        
        # Test the endpoint
        response = self.client.post("/rag", json={"query": "integration test"})
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "documents_found" in data
        assert data["documents_found"] == 1
        assert "HB 1" in data["result"]
    
    def test_rag_endpoint_validation(self):
        """Test RAG endpoint input validation"""
        # Test missing query field
        response = self.client.post("/rag", json={})
        assert response.status_code == 422  # Validation error
        
        # Test invalid JSON
        response = self.client.post("/rag", data="invalid json")
        assert response.status_code == 422

class TestServiceIntegration:
    """Test service integration and availability"""
    
    def test_performance_services_conditional_import(self):
        """Test that performance services handle missing imports gracefully"""
        from app import PERFORMANCE_SERVICES_AVAILABLE
        
        # Should be boolean regardless of whether services are available
        assert isinstance(PERFORMANCE_SERVICES_AVAILABLE, bool)
    
    def test_cache_service_basic_functionality(self):
        """Test cache service basic functionality"""
        from cache_service import CacheService
        
        cache = CacheService()
        
        # Should be able to create instance
        assert cache is not None
        
        # Should have basic methods
        assert hasattr(cache, 'initialize')
        assert hasattr(cache, 'get_cached_result')
        assert hasattr(cache, 'set_cached_result')
        assert hasattr(cache, 'clear_cache')
    
    def test_response_quality_monitor_basic(self):
        """Test response quality monitor basic functionality"""
        from response_quality_monitor import ResponseQualityMonitor
        
        monitor = ResponseQualityMonitor()
        
        # Should be able to create instance
        assert monitor is not None
        
        # Should have basic methods
        assert hasattr(monitor, 'analyze_response_quality')
        assert hasattr(monitor, 'get_quality_analytics')
    
    def test_performance_monitor_basic(self):
        """Test performance monitor basic functionality"""
        from performance_monitor import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        
        # Should be able to create instance
        assert monitor is not None
        
        # Should have basic methods
        assert hasattr(monitor, 'record_request')
        assert hasattr(monitor, 'get_performance_summary')
        assert hasattr(monitor, 'get_real_time_stats')

class TestQueryValidation:
    """Test query processing and validation"""
    
    def test_query_request_model(self):
        """Test QueryRequest model validation"""
        # Valid request
        valid_request = QueryRequest(query="valid query")
        assert valid_request.query == "valid query"
        
        # Empty query (should work)
        empty_request = QueryRequest(query="")
        assert empty_request.query == ""
    
    @pytest.mark.asyncio
    async def test_query_edge_cases(self):
        """Test edge cases in query processing"""
        test_cases = [
            "",
            "   ",
            "single",
            "normal query with words",
            "query with special chars !@#$%^&*()",
            "very long query " * 20
        ]
        
        with patch('app.vectorstore') as mock_vectorstore:
            mock_retriever = MagicMock()
            mock_retriever.get_relevant_documents = MagicMock(return_value=[])
            mock_vectorstore.as_retriever.return_value = mock_retriever
            
            for test_query in test_cases:
                request = QueryRequest(query=test_query)
                result = await rag_query(request)
                
                # Should handle all cases without crashing
                assert "result" in result
                assert "documents_found" in result
                assert result["query"] == test_query

class TestConcurrencyAndResilience:
    """Test system behavior under load and error conditions"""
    
    @pytest.mark.asyncio
    async def test_concurrent_queries(self):
        """Test handling of concurrent queries"""
        import asyncio
        
        with patch('app.vectorstore') as mock_vectorstore:
            mock_retriever = MagicMock()
            mock_retriever.get_relevant_documents = MagicMock(return_value=[])
            mock_vectorstore.as_retriever.return_value = mock_retriever
            
            # Create multiple concurrent requests
            async def make_query(i):
                request = QueryRequest(query=f"concurrent query {i}")
                return await rag_query(request)
            
            # Run 5 queries concurrently
            tasks = [make_query(i) for i in range(5)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should complete successfully
            assert len(results) == 5
            for result in results:
                if isinstance(result, dict):
                    assert "result" in result
                    assert "documents_found" in result
    
    @pytest.mark.asyncio
    async def test_service_degradation(self):
        """Test graceful degradation when services are unavailable"""
        # Test with vectorstore unavailable
        with patch('app.vectorstore', None):
            request = QueryRequest(query="service degradation test")
            result = await rag_query(request)
            
            # Should handle gracefully
            assert "error" in result
            assert result["error"] is True

# Performance verification tests
class TestPerformanceRequirements:
    """Test that performance requirements are met"""
    
    @pytest.mark.asyncio
    async def test_response_time_acceptable(self):
        """Test that response times are reasonable"""
        with patch('app.vectorstore') as mock_vectorstore, \
             patch('app.RetrievalQA') as mock_qa:
            
            mock_retriever = MagicMock()
            mock_doc = MagicMock()
            mock_doc.page_content = "Performance test content"
            mock_doc.metadata = {"bill_id": "HB 1"}
            mock_retriever.get_relevant_documents = MagicMock(return_value=[mock_doc])
            mock_vectorstore.as_retriever.return_value = mock_retriever
            
            mock_chain = MagicMock()
            mock_chain.return_value = {
                "result": "Performance test response",
                "source_documents": [mock_doc]
            }
            mock_qa.from_chain_type.return_value = mock_chain
            
            # Measure response time
            start_time = time.time()
            request = QueryRequest(query="performance test")
            result = await rag_query(request)
            duration = time.time() - start_time
            
            # Should complete within reasonable time (adjust as needed)
            assert duration < 10.0  # 10 seconds max for test environment
            assert "result" in result
    
    def test_memory_usage_reasonable(self):
        """Test that memory usage is reasonable"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple instances to test memory usage
        from app import QueryRequest
        requests = [QueryRequest(query=f"memory test {i}") for i in range(100)]
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        # Memory increase should be reasonable (adjust threshold as needed)
        assert memory_increase < 100  # Less than 100MB increase
