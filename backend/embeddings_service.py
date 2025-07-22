# backend/embeddings_service.py
import asyncio
import logging
from typing import List, Dict, Any, Optional
from voyageai import Client as VoyageClient
import httpx
from concurrent.futures import ThreadPoolExecutor
import time
from cache_service import cache_service
import hashlib

logger = logging.getLogger(__name__)

class OptimizedEmbeddingsService:
    """
    Optimized embeddings service with caching, batching, and async processing
    (Using memory-only cache for Python 3.13+ compatibility)
    """
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "voyage-3.5",
        batch_size: int = 100,
        max_workers: int = 5
    ):
        self.client = VoyageClient(api_key=api_key)
        self.model = model
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Simple in-memory cache for backward compatibility with tests
        self.cache = {}
        
        # Statistics tracking
        self.stats = {
            "embeddings_created": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "batch_requests": 0,
            "total_tokens": 0
        }
        
        logger.info(f"Embeddings service initialized (model: {model}, batch_size: {batch_size})")
    
    def _get_cache_key(self, text: str, input_type: str = "query") -> str:
        """Generate cache key for embedding (backward compatibility)"""
        return self._get_embedding_cache_key(text, input_type)
    
    def _get_embedding_cache_key(self, text: str, input_type: str = "query") -> str:
        """Generate cache key for embedding"""
        content = f"{text}:{input_type}:{self.model}"
        return f"embedding:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def embed_query(self, text: str) -> List[float]:
        """Embed a single query with caching"""
        cache_key = self._get_embedding_cache_key(text, "query")
        
        # Check simple cache first (for tests)
        if cache_key in self.cache:
            self.stats["cache_hits"] += 1
            logger.debug(f"Embedding cache hit for query: {text[:50]}...")
            return self.cache[cache_key]
        
        # Check advanced cache
        cached_embedding = await cache_service.get_cached_result(cache_key)
        if cached_embedding and "embedding" in cached_embedding:
            self.stats["cache_hits"] += 1
            # Store in simple cache too
            self.cache[cache_key] = cached_embedding["embedding"]
            logger.debug(f"Embedding cache hit for query: {text[:50]}...")
            return cached_embedding["embedding"]
        
        # Generate embedding
        self.stats["cache_misses"] += 1
        try:
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                self.executor,
                lambda: self.client.embed([text], model=self.model, input_type="query").embeddings[0]
            )
            
            # Cache the result in both caches
            self.cache[cache_key] = embedding
            await cache_service.set_cached_result(cache_key, {"embedding": embedding})
            
            self.stats["embeddings_created"] += 1
            self.stats["total_tokens"] += len(text.split())
            
            logger.debug(f"Generated embedding for query: {text[:50]}...")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents with batching and caching"""
        if not texts:
            return []
        
        embeddings = []
        uncached_texts = []
        cache_keys = []
        
        # Check cache for all texts
        for text in texts:
            cache_key = self._get_embedding_cache_key(text, "document")
            cache_keys.append(cache_key)
            
            cached_embedding = await cache_service.get_cached_result(cache_key)
            if cached_embedding and "embedding" in cached_embedding:
                embeddings.append(cached_embedding["embedding"])
                self.stats["cache_hits"] += 1
            else:
                embeddings.append(None)
                uncached_texts.append((len(embeddings) - 1, text, cache_key))
                self.stats["cache_misses"] += 1
        
        # Process uncached texts in batches
        if uncached_texts:
            await self._process_uncached_embeddings(uncached_texts, embeddings)
        
        return embeddings
    
    async def _process_uncached_embeddings(
        self, 
        uncached_texts: List[tuple], 
        embeddings: List[Optional[List[float]]]
    ):
        """Process uncached embeddings in optimal batches"""
        # Split into batches
        batches = []
        for i in range(0, len(uncached_texts), self.batch_size):
            batch = uncached_texts[i:i + self.batch_size]
            batches.append(batch)
        
        # Process batches concurrently
        tasks = []
        for batch in batches:
            task = self._process_embedding_batch(batch, embeddings)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def _process_embedding_batch(
        self, 
        batch: List[tuple], 
        embeddings: List[Optional[List[float]]]
    ):
        """Process a single batch of embeddings"""
        try:
            texts_to_embed = [item[1] for item in batch]
            
            # Generate embeddings for batch
            loop = asyncio.get_event_loop()
            batch_embeddings = await loop.run_in_executor(
                self.executor,
                lambda: self.client.embed(
                    texts_to_embed, 
                    model=self.model, 
                    input_type="document"
                ).embeddings
            )
            
            # Store results and cache
            for i, (embedding_idx, text, cache_key) in enumerate(batch):
                embedding = batch_embeddings[i]
                embeddings[embedding_idx] = embedding
                
                # Cache the result
                await cache_service.set_cached_result(
                    cache_key, 
                    {"embedding": embedding}
                )
            
            self.stats["batch_requests"] += 1
            self.stats["embeddings_created"] += len(batch)
            self.stats["total_tokens"] += sum(len(text.split()) for _, text, _ in batch)
            
            logger.info(f"Generated {len(batch)} embeddings in batch")
            
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            # Set failed embeddings to None (will need to handle in caller)
            for embedding_idx, _, _ in batch:
                embeddings[embedding_idx] = None
            raise
    
    async def warm_cache(self, common_queries: List[str]):
        """Pre-warm cache with common queries"""
        logger.info(f"Warming embedding cache with {len(common_queries)} common queries")
        
        tasks = []
        for query in common_queries:
            task = self.embed_query(query)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(f"Embedding cache warmed successfully ({successful}/{len(common_queries)})")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        total_requests = self.stats["cache_hits"] + self.stats["cache_misses"]
        return {
            **self.stats.copy(),
            "model": self.model,
            "batch_size": self.batch_size,
            "max_workers": self.executor._max_workers,
            "cache_hit_rate": self.stats["cache_hits"] / total_requests if total_requests > 0 else 0
        }
    
    async def close(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
        logger.info("Embeddings service closed")

# Global embeddings service instance
embeddings_service: Optional[OptimizedEmbeddingsService] = None
