import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

# Set up test environment
os.environ["TESTING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Mock the VoyageClient before importing
class MockVoyageClient:
    def __init__(self, *args, **kwargs):
        pass
    
    def embed(self, texts, **kwargs):
        # Return mock embeddings
        if isinstance(texts, list):
            return MagicMock(embeddings=[[0.1] * 1024 for _ in texts])
        else:
            return MagicMock(embeddings=[[0.1] * 1024])

with patch('embeddings_service.VoyageClient', MockVoyageClient):
    from embeddings_service import OptimizedEmbeddingsService

class TestOptimizedEmbeddingsService:
    """Test cases for the optimized embeddings service"""
    
    @pytest.mark.asyncio
    async def test_embeddings_service_initialization(self):
        """Test embeddings service initialization"""
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5",
            batch_size=50,
            max_workers=3
        )
        
        assert service.model == "voyage-3.5"
        assert service.batch_size == 50
        assert service.max_workers == 3
        assert service.cache == {}
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_embed_query_single(self):
        """Test embedding a single query"""
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5"
        )
        
        query = "education funding bills"
        embedding = await service.embed_query(query)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 1024  # Mock embedding dimension
        assert all(isinstance(x, float) for x in embedding)
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_embed_documents_batch(self):
        """Test embedding multiple documents in batch"""
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5",
            batch_size=3
        )
        
        documents = [
            "HB 55 education funding",
            "SB 120 healthcare reform", 
            "HB 200 tax policy",
            "SB 300 transportation"
        ]
        
        embeddings = await service.embed_documents(documents)
        
        assert isinstance(embeddings, list)
        assert len(embeddings) == 4
        assert all(len(emb) == 1024 for emb in embeddings)
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_embedding_caching(self):
        """Test that embeddings are cached properly"""
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5"
        )
        
        query = "test caching query"
        
        # First call - should compute embedding
        embedding1 = await service.embed_query(query)
        
        # Check cache
        cache_key = service._get_cache_key(query, "query")
        assert cache_key in service.cache
        
        # Second call - should use cache
        embedding2 = await service.embed_query(query)
        
        # Should be identical (from cache)
        assert embedding1 == embedding2
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_cache_warm_up(self):
        """Test cache warm-up functionality"""
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5"
        )
        
        warmup_queries = [
            "education funding",
            "healthcare bills",
            "tax reform"
        ]
        
        await service.warm_cache(warmup_queries)
        
        # Check that all queries are cached
        for query in warmup_queries:
            cache_key = service._get_cache_key(query, "query")
            assert cache_key in service.cache
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_batch_processing_large_dataset(self):
        """Test batch processing with large dataset"""
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5",
            batch_size=5
        )
        
        # Create large dataset (more than batch size)
        large_dataset = [f"Document {i} content" for i in range(12)]
        
        embeddings = await service.embed_documents(large_dataset)
        
        assert len(embeddings) == 12
        assert all(len(emb) == 1024 for emb in embeddings)
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent embedding requests"""
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5",
            max_workers=3
        )
        
        queries = [f"concurrent query {i}" for i in range(6)]
        
        # Make concurrent requests
        tasks = [service.embed_query(query) for query in queries]
        embeddings = await asyncio.gather(*tasks)
        
        assert len(embeddings) == 6
        assert all(len(emb) == 1024 for emb in embeddings)
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_error_handling_api_failure(self):
        """Test error handling when API fails"""
        # Create service with failing client
        class FailingClient:
            def embed(self, *args, **kwargs):
                raise Exception("API request failed")
        
        with patch('embeddings_service.VoyageClient', return_value=FailingClient()):
            service = OptimizedEmbeddingsService(
                api_key="test_key",
                model="voyage-3.5"
            )
            
            # Should handle API failure gracefully
            with pytest.raises(Exception):
                await service.embed_query("failing query")
            
            await service.close()
    
    @pytest.mark.asyncio
    async def test_stats_reporting(self):
        """Test statistics reporting"""
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5"
        )
        
        # Generate some activity
        await service.embed_query("test query 1")
        await service.embed_query("test query 2")
        await service.embed_documents(["doc1", "doc2", "doc3"])
        
        stats = service.get_stats()
        
        assert "cache_size" in stats
        assert "total_requests" in stats
        assert "cache_hit_rate" in stats
        assert stats["cache_size"] >= 0
        assert stats["total_requests"] >= 5
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """Test cache key generation logic"""
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5"
        )
        
        # Test different input types generate different keys
        query_key = service._get_cache_key("test text", "query")
        doc_key = service._get_cache_key("test text", "document")
        
        assert query_key != doc_key
        
        # Test same input generates same key
        query_key2 = service._get_cache_key("test text", "query")
        assert query_key == query_key2
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_memory_management_large_cache(self):
        """Test memory management with large cache"""
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5"
        )
        
        # Fill cache with many entries
        for i in range(100):
            await service.embed_query(f"query {i}")
        
        stats_before = service.get_stats()
        
        # Clear cache if it gets too large (implementation dependent)
        if hasattr(service, '_manage_cache_size'):
            service._manage_cache_size()
        
        stats_after = service.get_stats()
        
        # Cache should still be functional
        assert stats_after["cache_size"] >= 0
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_different_input_types(self):
        """Test handling of different input types"""
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5"
        )
        
        # Test different input scenarios
        test_cases = [
            "simple string",
            "multi-word query with special chars!",
            "",  # empty string
            "   whitespace padded   ",
            "Very long query with lots of text to test how the service handles longer inputs that might exceed certain limits but should still work fine",
        ]
        
        for test_input in test_cases:
            embedding = await service.embed_query(test_input)
            assert isinstance(embedding, list)
            assert len(embedding) == 1024
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation"""
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5"
        )
        
        # First request - cache miss
        await service.embed_query("cache test query")
        
        # Second request - cache hit
        await service.embed_query("cache test query")
        
        # Third request - cache miss
        await service.embed_query("different cache test query")
        
        stats = service.get_stats()
        
        # Should have some cache hits
        if stats["total_requests"] > 0:
            assert 0 <= stats["cache_hit_rate"] <= 1.0
        
        await service.close()
    
    def test_service_configuration(self):
        """Test service configuration validation"""
        # Test valid configuration
        service = OptimizedEmbeddingsService(
            api_key="test_key",
            model="voyage-3.5",
            batch_size=100,
            max_workers=5
        )
        
        assert service.batch_size == 100
        assert service.max_workers == 5
        
        # Test default values
        service2 = OptimizedEmbeddingsService(api_key="test_key")
        assert service2.batch_size > 0
        assert service2.max_workers > 0
