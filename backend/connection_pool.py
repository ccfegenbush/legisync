# backend/connection_pool.py
import asyncio
import logging
from typing import Optional, Dict, Any
from pinecone import Pinecone
from concurrent.futures import ThreadPoolExecutor
import time
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class PineconeConnectionPool:
    """
    Simplified connection pool manager for Pinecone (without Redis dependency)
    """
    
    def __init__(
        self,
        api_key: str,
        max_connections: int = 20,
        connection_timeout: float = 30.0,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        self.api_key = api_key
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        # Pool management
        self._pool = []
        self._in_use = set()
        self._lock = asyncio.Lock()
        self._stats = {
            "connections_created": 0,
            "connections_reused": 0,
            "connections_failed": 0,
            "active_connections": 0,
            "total_requests": 0
        }
        
        # Thread pool for blocking Pinecone operations
        self.executor = ThreadPoolExecutor(max_workers=max_connections)
        
        logger.info(f"Pinecone connection pool initialized (max_connections: {max_connections})")
        
    @property 
    def _available(self):
        """Get available connections (for backward compatibility)"""
        return self._pool
        
    async def _create_connection(self) -> Optional[Pinecone]:
        """Create a new Pinecone connection"""
        try:
            connection = Pinecone(api_key=self.api_key)
            self._stats["connections_created"] += 1
            logger.debug("Created new Pinecone connection")
            return connection
        except Exception as e:
            self._stats["connections_failed"] += 1
            logger.error(f"Failed to create Pinecone connection: {e}")
            return None
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool with automatic return"""
        connection = None
        try:
            async with self._lock:
                self._stats["total_requests"] += 1
                
                # Try to reuse existing connection
                if self._pool:
                    connection = self._pool.pop()
                    self._in_use.add(id(connection))
                    self._stats["connections_reused"] += 1
                    self._stats["active_connections"] += 1
                    logger.debug("Reusing connection from pool")
                
                # Create new connection if pool is empty and under limit
                elif len(self._in_use) < self.max_connections:
                    connection = await self._create_connection()
                    if connection:
                        self._in_use.add(id(connection))
                        self._stats["active_connections"] += 1
                else:
                    # Wait for connection to become available
                    logger.warning("Connection pool exhausted, waiting...")
            
            # If no connection available, wait and retry
            retry_count = 0
            while connection is None and retry_count < self.retry_attempts:
                await asyncio.sleep(self.retry_delay)
                retry_count += 1
                
                async with self._lock:
                    if self._pool:
                        connection = self._pool.pop()
                        self._in_use.add(id(connection))
                        self._stats["connections_reused"] += 1
                        self._stats["active_connections"] += 1
                        break
            
            if connection is None:
                raise Exception("Unable to acquire connection from pool")
            
            yield connection
            
        finally:
            # Return connection to pool
            if connection:
                async with self._lock:
                    conn_id = id(connection)
                    if conn_id in self._in_use:
                        self._in_use.remove(conn_id)
                        self._stats["active_connections"] -= 1
                        
                        # Return to pool if under capacity
                        if len(self._pool) < self.max_connections // 2:
                            self._pool.append(connection)
                            logger.debug("Returned connection to pool")
                        else:
                            logger.debug("Pool full, discarding connection")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            **self._stats.copy(),
            "pool_size": len(self._pool),
            "active_connections": len(self._in_use),
            "available_connections": len(self._pool),
            "max_connections": self.max_connections,
            "pool_utilization": len(self._in_use) / self.max_connections if self.max_connections > 0 else 0
        }
    
    async def acquire_connection(self):
        """Alias for get_connection for backward compatibility"""
        return await self.get_connection()
        
    async def release_connection(self, connection):
        """Release a connection back to the pool"""
        async with self._lock:
            if connection in self._in_use:
                self._in_use.remove(connection)
                if len(self._pool) < self.max_connections:
                    self._pool.append(connection)
                    self._stats["connections_reused"] += 1
    
    async def close(self):
        """Close all connections and cleanup"""
        async with self._lock:
            self._pool.clear()
            self._in_use.clear()
        
        self.executor.shutdown(wait=True)
        logger.info("Pinecone connection pool closed")

# Global connection pool instance (will be initialized in app startup)
pinecone_pool: Optional[PineconeConnectionPool] = None
