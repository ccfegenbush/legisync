import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

# Set up test environment
os.environ["TESTING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from cache_service import CacheService

class TestCacheService:
    """Test cases for the caching service"""
    
    @pytest.mark.asyncio
    async def test_cache_initialization(self):
        """Test cache service initialization"""
        cache = CacheService()
        
        # Test memory-only initialization (default for tests)
        initialized = await cache.initialize()
        assert initialized is True
        
        # Test stats
        stats = await cache.get_cache_stats()
        assert "memory_cache_size" in stats
        assert stats["memory_cache_size"] == 0
        
        await cache.close()
    
    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        """Test basic cache set and get operations"""
        cache = CacheService()
        await cache.initialize()
        
        # Test setting and getting a cached result
        query = "test query"
        result = {"result": "test result", "documents_found": 1}
        
        await cache.set_cached_result(query, result)
        cached_result = await cache.get_cached_result(query)
        
        assert cached_result is not None
        assert cached_result["result"] == "test result"
        assert cached_result["documents_found"] == 1
        
        await cache.close()
    
    @pytest.mark.asyncio
    async def test_cache_miss(self):
        """Test cache miss scenario"""
        cache = CacheService()
        await cache.initialize()
        
        # Try to get a non-existent cached result
        cached_result = await cache.get_cached_result("non-existent query")
        assert cached_result is None
        
        await cache.close()
    
    @pytest.mark.asyncio
    async def test_similarity_matching(self):
        """Test cache similarity matching for related queries"""
        cache = CacheService()
        await cache.initialize()
        
        # Store a result
        original_query = "education funding bills"
        result = {"result": "Education funding information", "documents_found": 2}
        await cache.set_cached_result(original_query, result)
        
        # Test similar queries
        similar_queries = [
            "education funding",
            "bills about education funding",
            "education bill funding"
        ]
        
        for similar_query in similar_queries:
            cached_result = await cache.get_cached_result(similar_query)
            # Should find similar result (depending on similarity threshold)
            if cached_result:
                assert "education" in cached_result["result"].lower()
        
        await cache.close()
    
    @pytest.mark.asyncio
    async def test_cache_clear(self):
        """Test cache clearing functionality"""
        cache = CacheService()
        await cache.initialize()
        
        # Add some cached results
        await cache.set_cached_result("query1", {"result": "result1"})
        await cache.set_cached_result("query2", {"result": "result2"})
        
        # Verify they're cached
        assert await cache.get_cached_result("query1") is not None
        assert await cache.get_cached_result("query2") is not None
        
        # Clear cache
        await cache.clear_cache()
        
        # Verify they're gone
        assert await cache.get_cached_result("query1") is None
        assert await cache.get_cached_result("query2") is None
        
        await cache.close()
    
    @pytest.mark.asyncio 
    async def test_cache_stats(self):
        """Test cache statistics reporting"""
        cache = CacheService()
        await cache.initialize()
        
        # Add some data
        await cache.set_cached_result("test1", {"result": "result1"})
        await cache.set_cached_result("test2", {"result": "result2"})
        
        # Check stats
        stats = await cache.get_cache_stats()
        
        assert "memory_cache_size" in stats
        assert "redis_available" in stats
        assert stats["memory_cache_size"] >= 2
        
        await cache.close()
    
    @pytest.mark.asyncio
    async def test_cache_with_redis_unavailable(self):
        """Test cache behavior when Redis is not available"""
        cache = CacheService()
        
        # Initialize without Redis
        with patch.object(cache, '_init_redis', return_value=None):
            initialized = await cache.initialize()
            assert initialized is True  # Should still work with memory only
            
            # Should still work for basic operations
            await cache.set_cached_result("test", {"result": "test"})
            result = await cache.get_cached_result("test")
            assert result is not None
        
        await cache.close()
