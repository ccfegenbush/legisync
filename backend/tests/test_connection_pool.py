import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import time

# Set up test environment
os.environ["TESTING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Mock Pinecone before importing
class MockPinecone:
    def __init__(self, *args, **kwargs):
        pass
        
    def Index(self, name):
        return MagicMock()

with patch('connection_pool.Pinecone', MockPinecone):
    from connection_pool import PineconeConnectionPool

class TestPineconeConnectionPool:
    """Test cases for Pinecone connection pooling"""
    
    @pytest.mark.asyncio
    async def test_connection_pool_initialization(self):
        """Test connection pool initialization"""
        pool = PineconeConnectionPool(
            api_key="test_key",
            max_connections=5,
            connection_timeout=10.0
        )
        
        assert pool.max_connections == 5
        assert pool.connection_timeout == 10.0
        assert len(pool._available) == 0
        assert len(pool._in_use) == 0
        
        await pool.close()
    
    @pytest.mark.asyncio
    async def test_acquire_connection(self):
        """Test acquiring a connection from pool"""
        pool = PineconeConnectionPool(
            api_key="test_key",
            max_connections=3
        )
        
        # Acquire first connection
        conn1 = await pool.acquire_connection("test-index")
        assert conn1 is not None
        assert len(pool._in_use) == 1
        
        # Acquire second connection
        conn2 = await pool.acquire_connection("test-index")
        assert conn2 is not None
        assert len(pool._in_use) == 2
        assert conn1 != conn2  # Should be different connections
        
        await pool.close()
    
    @pytest.mark.asyncio
    async def test_release_connection(self):
        """Test releasing a connection back to pool"""
        pool = PineconeConnectionPool(
            api_key="test_key",
            max_connections=3
        )
        
        # Acquire and release connection
        conn = await pool.acquire_connection("test-index")
        await pool.release_connection(conn)
        
        assert len(pool._in_use) == 0
        assert len(pool._available) == 1
        
        await pool.close()
    
    @pytest.mark.asyncio
    async def test_connection_reuse(self):
        """Test that released connections are reused"""
        pool = PineconeConnectionPool(
            api_key="test_key",
            max_connections=2
        )
        
        # Acquire connection
        conn1 = await pool.acquire_connection("test-index")
        conn1_id = id(conn1)
        
        # Release it
        await pool.release_connection(conn1)
        
        # Acquire again - should get the same connection object
        conn2 = await pool.acquire_connection("test-index")
        conn2_id = id(conn2)
        
        assert conn1_id == conn2_id
        
        await pool.close()
    
    @pytest.mark.asyncio
    async def test_max_connections_limit(self):
        """Test that pool respects max connections limit"""
        pool = PineconeConnectionPool(
            api_key="test_key",
            max_connections=2
        )
        
        # Acquire all available connections
        conn1 = await pool.acquire_connection("test-index")
        conn2 = await pool.acquire_connection("test-index")
        
        assert len(pool._in_use) == 2
        
        # Try to acquire one more (should timeout or wait)
        start_time = time.time()
        
        try:
            # Use a short timeout to avoid waiting too long in tests
            conn3 = await asyncio.wait_for(
                pool.acquire_connection("test-index"),
                timeout=0.1
            )
            # If we get here, the pool allowed more than max connections
            await pool.release_connection(conn3)
            assert False, "Pool should not exceed max connections"
        except asyncio.TimeoutError:
            # Expected behavior - pool is full
            pass
        
        elapsed = time.time() - start_time
        assert elapsed >= 0.1  # Should have waited for timeout
        
        await pool.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_connection_requests(self):
        """Test handling of concurrent connection requests"""
        pool = PineconeConnectionPool(
            api_key="test_key",
            max_connections=5
        )
        
        # Make multiple concurrent requests
        async def get_and_release_connection():
            conn = await pool.acquire_connection("test-index")
            await asyncio.sleep(0.01)  # Hold connection briefly
            await pool.release_connection(conn)
            return conn
        
        tasks = [get_and_release_connection() for _ in range(10)]
        connections = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(connections) == 10
        assert all(conn is not None for conn in connections)
        
        # Pool should be cleaned up
        assert len(pool._in_use) == 0
        
        await pool.close()
    
    @pytest.mark.asyncio 
    async def test_connection_timeout_handling(self):
        """Test connection timeout handling"""
        pool = PineconeConnectionPool(
            api_key="test_key",
            max_connections=1,
            connection_timeout=0.1  # Very short timeout
        )
        
        # Acquire the only connection
        conn1 = await pool.acquire_connection("test-index")
        
        # Try to acquire another (should timeout)
        start_time = time.time()
        
        try:
            conn2 = await pool.acquire_connection("test-index")
            # If we get here without timeout, test failed
            await pool.release_connection(conn2)
            assert False, "Should have timed out"
        except asyncio.TimeoutError:
            # Expected
            elapsed = time.time() - start_time
            assert elapsed >= 0.1  # Should respect timeout
        
        await pool.close()
    
    @pytest.mark.asyncio
    async def test_different_indexes(self):
        """Test handling of connections to different indexes"""
        pool = PineconeConnectionPool(
            api_key="test_key",
            max_connections=5
        )
        
        # Acquire connections to different indexes
        conn1 = await pool.acquire_connection("index1")
        conn2 = await pool.acquire_connection("index2")
        conn3 = await pool.acquire_connection("index1")  # Same as first
        
        assert conn1 is not None
        assert conn2 is not None
        assert conn3 is not None
        
        # Should handle different indexes properly
        assert len(pool._in_use) == 3
        
        await pool.close()
    
    @pytest.mark.asyncio
    async def test_pool_stats(self):
        """Test pool statistics reporting"""
        pool = PineconeConnectionPool(
            api_key="test_key",
            max_connections=3
        )
        
        # Initial stats
        stats = pool.get_stats()
        assert stats["max_connections"] == 3
        assert stats["active_connections"] == 0
        assert stats["available_connections"] == 0
        
        # Acquire some connections
        conn1 = await pool.acquire_connection("test-index")
        conn2 = await pool.acquire_connection("test-index")
        
        # Check updated stats
        stats = pool.get_stats()
        assert stats["active_connections"] == 2
        
        # Release one connection
        await pool.release_connection(conn1)
        
        stats = pool.get_stats()
        assert stats["active_connections"] == 1
        assert stats["available_connections"] == 1
        
        await pool.close()
    
    @pytest.mark.asyncio
    async def test_pool_cleanup_on_close(self):
        """Test that pool properly cleans up on close"""
        pool = PineconeConnectionPool(
            api_key="test_key",
            max_connections=3
        )
        
        # Acquire some connections
        conn1 = await pool.acquire_connection("test-index")
        conn2 = await pool.acquire_connection("test-index")
        
        assert len(pool._in_use) == 2
        
        # Close pool
        await pool.close()
        
        # Should clean up
        assert len(pool._in_use) == 0
        assert len(pool._available) == 0
    
    @pytest.mark.asyncio
    async def test_connection_health_check(self):
        """Test connection health checking (if implemented)"""
        pool = PineconeConnectionPool(
            api_key="test_key",
            max_connections=2
        )
        
        # Acquire connection
        conn = await pool.acquire_connection("test-index")
        
        # If health check is implemented, it should pass
        if hasattr(pool, '_check_connection_health'):
            health = await pool._check_connection_health(conn)
            assert health is True or health is None  # None means not implemented
        
        await pool.release_connection(conn)
        await pool.close()
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_index(self):
        """Test error handling for invalid index names"""
        pool = PineconeConnectionPool(
            api_key="test_key",
            max_connections=2
        )
        
        # Try with various potentially problematic index names
        test_indexes = ["", None, "invalid-index-name-that-does-not-exist"]
        
        for index_name in test_indexes:
            try:
                conn = await pool.acquire_connection(index_name)
                if conn:
                    await pool.release_connection(conn)
            except Exception as e:
                # Some errors are expected for invalid inputs
                assert isinstance(e, (ValueError, TypeError, AttributeError))
        
        await pool.close()
    
    @pytest.mark.asyncio
    async def test_connection_pool_under_load(self):
        """Test connection pool behavior under high load"""
        pool = PineconeConnectionPool(
            api_key="test_key", 
            max_connections=3
        )
        
        # Simulate high load with many rapid requests
        async def rapid_requests():
            results = []
            for i in range(20):
                try:
                    conn = await asyncio.wait_for(
                        pool.acquire_connection("test-index"), 
                        timeout=0.5
                    )
                    results.append(conn)
                    # Brief hold then release
                    await asyncio.sleep(0.001)
                    await pool.release_connection(conn)
                except asyncio.TimeoutError:
                    results.append(None)  # Mark timeouts
            return results
        
        # Run multiple concurrent high-load scenarios
        task_results = await asyncio.gather(
            rapid_requests(),
            rapid_requests(),
            return_exceptions=True
        )
        
        # Check that pool handled load reasonably
        for results in task_results:
            if isinstance(results, list):
                successful_requests = sum(1 for r in results if r is not None)
                # Should have some successful requests
                assert successful_requests > 0
        
        # Pool should be cleaned up
        stats = pool.get_stats()
        assert stats["active_connections"] == 0
        
        await pool.close()
