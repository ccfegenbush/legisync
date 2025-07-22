# backend/cache_service.py
import json
import hashlib
import logging
from typing import Optional, Dict, Any, List
from cachetools import TTLCache
import asyncio
from datetime import timedelta

logger = logging.getLogger(__name__)

class CacheService:
    """
    Advanced caching service for RAG optimizations with memory-based caching
    (Redis integration disabled for Python 3.13+ compatibility)
    """
    
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379/0",
        memory_cache_size: int = 1000,
        memory_ttl: int = 300,  # 5 minutes
        redis_ttl: int = 3600   # 1 hour
    ):
        self.redis_url = redis_url
        self.redis_ttl = redis_ttl
        self.redis_client = None
        self.async_redis_client = None
        
        # In-memory cache for ultra-fast access
        self.memory_cache = TTLCache(maxsize=memory_cache_size, ttl=memory_ttl)
        
        # Query similarity cache - stores normalized queries
        self.similarity_cache = TTLCache(maxsize=500, ttl=1800)  # 30 minutes
        
        # Connection pool for Redis (disabled for compatibility)
        self.connection_pool = None
        
    async def initialize(self):
        """Initialize cache service (memory-only for Python 3.13+ compatibility)"""
        logger.info("Cache service initialized with memory-only mode")
        logger.info("Redis integration disabled for Python 3.13+ compatibility")
        return True
    
    def _get_cache_key(self, query: str, prefix: str = "rag") -> str:
        """Generate cache key from query"""
        query_hash = hashlib.md5(query.lower().strip().encode()).hexdigest()
        return f"{prefix}:{query_hash}"
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for similarity detection"""
        # Remove extra whitespace, convert to lowercase, remove common words
        import re
        normalized = re.sub(r'\s+', ' ', query.lower().strip())
        # Could add more sophisticated normalization like stemming
        return normalized
    
    async def get_cached_result(self, query: str) -> Optional[Dict[Any, Any]]:
        """
        Get cached result with fallback chain:
        1. Check memory cache
        2. Check for similar queries
        """
        cache_key = self._get_cache_key(query)
        
        # Level 1: Memory cache (fastest)
        if cache_key in self.memory_cache:
            logger.info(f"Cache HIT (memory): {query[:50]}...")
            return self.memory_cache[cache_key]
        
        # Level 2: Query similarity detection
        normalized_query = self._normalize_query(query)
        for cached_query, cached_key in self.similarity_cache.items():
            # Simple similarity check - could be enhanced with semantic similarity
            if self._query_similarity(normalized_query, cached_query) > 0.8:
                logger.info(f"Cache HIT (similarity): {query[:50]} -> {cached_query[:50]}")
                return await self.get_cached_result(cached_key)
        
        logger.info(f"Cache MISS: {query[:50]}...")
        return None
    
    async def set_cached_result(self, query: str, result: Dict[Any, Any]):
        """Store result in memory cache"""
        cache_key = self._get_cache_key(query)
        
        # Store in memory cache
        self.memory_cache[cache_key] = result
        
        # Store normalized query for similarity detection
        normalized_query = self._normalize_query(query)
        self.similarity_cache[normalized_query] = query
        
        logger.info(f"Cached result for: {query[:50]}...")
    
    def _query_similarity(self, query1: str, query2: str) -> float:
        """Simple Jaccard similarity for query matching"""
        set1 = set(query1.split())
        set2 = set(query2.split())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        stats = {
            "memory_cache_size": len(self.memory_cache),
            "memory_cache_maxsize": self.memory_cache.maxsize,
            "similarity_cache_size": len(self.similarity_cache),
            "redis_connected": False,
            "cache_mode": "memory_only"
        }
            
        return stats
    
    async def clear_cache(self, pattern: str = "rag:*"):
        """Clear memory cache"""
        self.memory_cache.clear()
        self.similarity_cache.clear()
        logger.info("Memory cache cleared")
    
    async def close(self):
        """Clean up (no-op for memory-only cache)"""
        logger.info("Cache service closed")

# Global cache instance
cache_service = CacheService()
