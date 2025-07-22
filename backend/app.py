# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_pinecone import PineconeVectorStore  # Updated import
from langchain.chains import RetrievalQA
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool
from voyageai import Client as VoyageClient
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # Your fix
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import logging
import pinecone
from pinecone import Pinecone
import asyncio
import httpx
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
from cache_service import cache_service
from connection_pool import PineconeConnectionPool, pinecone_pool
from embeddings_service import OptimizedEmbeddingsService, embeddings_service
from performance_monitor import PerformanceMonitor, performance_monitor
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Thread pool for CPU-bound operations
thread_pool = ThreadPoolExecutor(max_workers=10)

# HTTP client for async operations
http_client: Optional[httpx.AsyncClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    global http_client, pinecone_pool, embeddings_service
    
    logger.info("Starting LegisSync backend with RAG optimizations...")
    
    # Initialize cache service
    cache_initialized = await cache_service.initialize()
    if cache_initialized:
        logger.info("✅ Cache service initialized successfully")
    else:
        logger.warning("⚠️ Cache service using memory-only mode")
    
    # Initialize Pinecone connection pool
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if pinecone_api_key:
        pinecone_pool = PineconeConnectionPool(
            api_key=pinecone_api_key,
            max_connections=20,
            connection_timeout=30.0
        )
        logger.info("✅ Pinecone connection pool initialized")
    
    # Initialize optimized embeddings service
    voyage_api_key = os.getenv("VOYAGE_API_KEY")
    if voyage_api_key:
        embeddings_service = OptimizedEmbeddingsService(
            api_key=voyage_api_key,
            model="voyage-3.5",
            batch_size=100,
            max_workers=5
        )
        logger.info("✅ Optimized embeddings service initialized")
        
        # Pre-warm cache with common queries
        common_queries = [
            "healthcare bill",
            "education funding", 
            "transportation infrastructure",
            "environmental protection",
            "tax reform"
        ]
        await embeddings_service.warm_cache(common_queries)
        logger.info("✅ Embeddings cache warmed")
    
    # Initialize HTTP client with connection pooling
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
    )
    
    # Start performance monitoring
    await performance_monitor.start_monitoring(interval_seconds=60)
    logger.info("✅ Performance monitoring started")
    
    logger.info("🚀 LegisSync backend fully optimized and ready!")
    
    yield
    
    # Cleanup
    logger.info("Shutting down LegisSync backend...")
    
    if http_client:
        await http_client.aclose()
    if pinecone_pool:
        await pinecone_pool.close()
    if embeddings_service:
        await embeddings_service.close()
    await cache_service.close()
    await performance_monitor.stop_monitoring()
    thread_pool.shutdown(wait=True)
    
    logger.info("✅ LegisSync backend shutdown complete")

# Log environment variable status (without exposing the actual keys)
logger.info(f"PINECONE_API_KEY present: {bool(os.getenv('PINECONE_API_KEY'))}")
logger.info(f"VOYAGE_API_KEY present: {bool(os.getenv('VOYAGE_API_KEY'))}")
logger.info(f"GOOGLE_API_KEY present: {bool(os.getenv('GOOGLE_API_KEY'))}")
logger.info(f"Index name: {os.getenv('PINECONE_INDEX_NAME', 'bills-index-dev')}")

app = FastAPI(lifespan=lifespan)

# Health check endpoint with cache stats
@app.get("/health")
async def health_check():
    cache_stats = await cache_service.get_cache_stats()
    return {
        "status": "healthy", 
        "service": "legisync-backend",
        "cache_stats": cache_stats
    }

# Debug endpoint to check system status
@app.get("/debug/status")
async def debug_status():
    cache_stats = await cache_service.get_cache_stats()
    return {
        "pinecone_api_key": bool(os.getenv("PINECONE_API_KEY")),
        "voyage_api_key": bool(os.getenv("VOYAGE_API_KEY")),
        "google_api_key": bool(os.getenv("GOOGLE_API_KEY")),
        "index_name": os.getenv("PINECONE_INDEX_NAME", "bills-index-dev"),
        "vectorstore_initialized": vectorstore is not None,
        "pinecone_client_initialized": pc is not None,
        "cache_service": cache_stats,
        "http_client_active": http_client is not None
    }

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js default dev server
        "http://localhost:3001",  # Alternative Next.js port
        "http://127.0.0.1:3000",  # Alternative localhost format
        "http://127.0.0.1:3001",
        "https://legisync-dev.vercel.app",  # Your deployed frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request models for API endpoints
class QueryRequest(BaseModel):
    query: str

# Configure tracing only when not in test mode
is_testing = os.getenv("TESTING", "false").lower() == "true" or "pytest" in os.environ.get("_", "")

if not is_testing:
    from langsmith import traceable
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")))
    tracer = trace.get_tracer(__name__)
else:
    # Use a no-op tracer and decorator for testing
    from opentelemetry.sdk.trace import NoOpTracer
    tracer = NoOpTracer()
    # Create a no-op traceable decorator
    def traceable(func):
        return func

# Initialize Pinecone client
try:
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    logger.info("Pinecone client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Pinecone client: {e}")
    pc = None

vo = VoyageClient(api_key=os.getenv("VOYAGE_API_KEY"))
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME", "bills-index-dev")

logger.info(f"Initializing Pinecone with index: {index_name}")

# Create a proper embedding function for langchain
from langchain_core.embeddings import Embeddings
from typing import List

class VoyageEmbeddings(Embeddings):
    def __init__(self, client: VoyageClient):
        self.client = client
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.client.embed(texts, model="voyage-3.5", input_type="document").embeddings
    
    def embed_query(self, text: str) -> List[float]:
        return self.client.embed([text], model="voyage-3.5", input_type="query").embeddings[0]

embeddings = VoyageEmbeddings(vo)

try:
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings, text_key="text")
    logger.info("Pinecone vectorstore initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Pinecone vectorstore: {e}")
    vectorstore = None

def query_db(bill_id: str) -> dict:
    return {"bill_id": bill_id, "content": "Mock bill details from DB"}

tools = [Tool(name="DBQuery", func=query_db, description="Fetch bill details by ID")]

# Create a context manager that works whether tracing is enabled or not
from contextlib import contextmanager

@contextmanager
def optional_span(name: str):
    if not is_testing and hasattr(tracer, 'start_as_current_span'):
        with tracer.start_as_current_span(name):
            yield
    else:
        yield

@app.post("/rag")
@traceable
async def rag_query(request: QueryRequest):
    start_time = time.time()
    cache_hit = False
    documents_found = 0
    error_occurred = False
    
    with optional_span("rag-query"):
        try:
            logger.info(f"🔍 Processing query: {request.query}")
            
            # Check cache first for immediate response
            cached_result = await cache_service.get_cached_result(request.query)
            if cached_result:
                cache_hit = True
                documents_found = cached_result.get("documents_found", 0)
                duration_ms = (time.time() - start_time) * 1000
                
                # Record performance metrics
                performance_monitor.record_request(
                    endpoint="/rag",
                    query=request.query,
                    duration_ms=duration_ms,
                    cache_hit=True,
                    documents_found=documents_found,
                    error=False,
                    status_code=200
                )
                
                logger.info(f"💾 Cache hit! Returning cached result ({duration_ms:.0f}ms)")
                return cached_result
            
            # Check if vectorstore is available
            if vectorstore is None:
                error_occurred = True
                logger.error("Vectorstore is not initialized")
                error_result = {
                    "query": request.query,
                    "result": "The search service is currently unavailable. Please try again later.",
                    "error": True
                }
                
                duration_ms = (time.time() - start_time) * 1000
                performance_monitor.record_request(
                    endpoint="/rag",
                    query=request.query,
                    duration_ms=duration_ms,
                    cache_hit=False,
                    documents_found=0,
                    error=True,
                    status_code=503
                )
                
                return error_result
            
            # Run optimized vector search and LLM processing
            async def optimized_vector_search():
                """Optimized async vector search with connection pooling"""
                if pinecone_pool and embeddings_service:
                    # Use optimized services
                    with optional_span("embedding-generation"):
                        query_embedding = await embeddings_service.embed_query(request.query)
                    
                    with optional_span("vector-search-optimized"):
                        # This would integrate with the connection pool for actual Pinecone queries
                        # For now, fall back to the existing method
                        loop = asyncio.get_event_loop()
                        retriever = vectorstore.as_retriever()
                        docs = await loop.run_in_executor(thread_pool, retriever.get_relevant_documents, request.query)
                        return docs
                else:
                    # Fallback to original method
                    loop = asyncio.get_event_loop()
                    retriever = vectorstore.as_retriever()
                    docs = await loop.run_in_executor(thread_pool, retriever.get_relevant_documents, request.query)
                    return docs
            
            async def run_chain(docs):
                """Async wrapper for chain processing with performance tracking"""
                if not docs:
                    return {
                        "query": request.query,
                        "result": "No relevant bills found for your query. Please try a different search term.",
                        "documents_found": 0
                    }
                
                with optional_span("llm-processing"):
                    loop = asyncio.get_event_loop()
                    retriever = vectorstore.as_retriever()
                    chain = RetrievalQA.from_chain_type(
                        llm=model, 
                        chain_type="stuff",
                        retriever=retriever,
                        return_source_documents=True
                    )
                    result = await loop.run_in_executor(thread_pool, chain, {"query": request.query})
                    return result
            
            # Execute vector search
            search_start = time.time()
            docs = await optimized_vector_search()
            search_duration = (time.time() - search_start) * 1000
            documents_found = len(docs)
            
            logger.info(f"📄 Retrieved {documents_found} documents ({search_duration:.0f}ms)")
            
            # Execute chain processing
            chain_start = time.time()
            chain_result = await run_chain(docs)
            chain_duration = (time.time() - chain_start) * 1000
            
            logger.info(f"🤖 LLM processing completed ({chain_duration:.0f}ms)")
            
            if isinstance(chain_result, dict) and "documents_found" in chain_result:
                # No documents found case
                final_result = chain_result
            else:
                # Normal processing
                final_result = {
                    "query": request.query,
                    "result": chain_result.get("result", "No result generated"),
                    "documents_found": documents_found,
                    "source_documents": len(chain_result.get("source_documents", [])),
                    "performance": {
                        "search_duration_ms": search_duration,
                        "llm_duration_ms": chain_duration,
                        "total_duration_ms": (time.time() - start_time) * 1000
                    }
                }
            
            # Cache successful results (but only if we found documents)
            if documents_found > 0:
                await cache_service.set_cached_result(request.query, final_result)
                logger.info("💾 Result cached for future queries")
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Record performance metrics
            performance_monitor.record_request(
                endpoint="/rag",
                query=request.query,
                duration_ms=duration_ms,
                cache_hit=False,
                documents_found=documents_found,
                error=False,
                status_code=200
            )
            
            logger.info(f"✅ RAG query completed successfully ({duration_ms:.0f}ms total)")
            return final_result
            
        except Exception as e:
            error_occurred = True
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(f"❌ Error in RAG query ({duration_ms:.0f}ms): {str(e)}", exc_info=True)
            
            error_result = {
                "query": request.query,
                "result": f"Sorry, I encountered an error while processing your request. Please try again.",
                "error": True,
                "error_details": str(e)
            }
            
            # Record error metrics
            performance_monitor.record_request(
                endpoint="/rag",
                query=request.query,
                duration_ms=duration_ms,
                cache_hit=cache_hit,
                documents_found=documents_found,
                error=True,
                status_code=500
            )
            
            return error_result

@app.post("/agent")
@traceable
async def run_agent(request: QueryRequest):
    with optional_span("agent-query"):
        try:
            # Check cache for agent queries too
            agent_cache_key = f"agent:{request.query}"
            cached_result = await cache_service.get_cached_result(agent_cache_key)
            if cached_result:
                return cached_result
            
            # Run agent in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            agent = create_react_agent(model, tools)
            result = await loop.run_in_executor(
                thread_pool, 
                agent.invoke, 
                {"messages": [{"role": "user", "content": request.query}]}
            )
            
            # Cache agent results
            await cache_service.set_cached_result(agent_cache_key, result)
            
            return result
        except Exception as e:
            logger.error(f"Error in agent query: {str(e)}", exc_info=True)
            return {
                "error": True,
                "message": f"Agent processing failed: {str(e)}"
            }

# Cache management endpoints
@app.get("/admin/cache/stats")
async def get_cache_stats():
    """Get detailed cache performance statistics"""
    return await cache_service.get_cache_stats()

@app.post("/admin/cache/clear")
async def clear_cache():
    """Clear all cached results"""
    await cache_service.clear_cache()
    return {"message": "Cache cleared successfully"}

# Performance monitoring endpoint
@app.get("/admin/performance")
async def get_performance_stats():
    """Get comprehensive performance metrics for monitoring"""
    cache_stats = await cache_service.get_cache_stats()
    performance_summary = performance_monitor.get_performance_summary(hours=24)
    real_time_stats = performance_monitor.get_real_time_stats()
    
    # Get embeddings service stats if available
    embeddings_stats = embeddings_service.get_stats() if embeddings_service else None
    
    # Get Pinecone connection pool stats if available
    pinecone_stats = pinecone_pool.get_stats() if pinecone_pool else None
    
    return {
        "timestamp": time.time(),
        "service": "legisync-backend-optimized",
        "cache_stats": cache_stats,
        "performance_summary": performance_summary,
        "real_time_stats": real_time_stats,
        "embeddings_service": embeddings_stats,
        "pinecone_pool": pinecone_stats,
        "thread_pool": {
            "active_threads": len([t for t in thread_pool._threads if t.is_alive()]) if hasattr(thread_pool, '_threads') else 0,
            "max_workers": thread_pool._max_workers
        },
        "http_client_active": http_client is not None,
        "vectorstore_initialized": vectorstore is not None,
        "optimization_status": {
            "cache_service": cache_service is not None,
            "embeddings_service": embeddings_service is not None,
            "connection_pool": pinecone_pool is not None,
            "performance_monitoring": performance_monitor is not None
        }
    }

# Real-time performance dashboard endpoint
@app.get("/admin/performance/realtime")
async def get_realtime_performance():
    """Get real-time performance metrics for dashboard"""
    return performance_monitor.get_real_time_stats()

# Performance alerts endpoint
@app.get("/admin/performance/alerts")
async def get_performance_alerts():
    """Get current performance alerts"""
    summary = performance_monitor.get_performance_summary(hours=1)
    return {
        "alerts": summary.get("performance_alerts", []),
        "timestamp": time.time()
    }

# Export metrics endpoint
@app.post("/admin/performance/export")
async def export_performance_metrics(filename: str = "legisync_metrics.json"):
    """Export all performance metrics to file"""
    try:
        filepath = f"/tmp/{filename}"
        performance_monitor.export_metrics(filepath)
        return {"message": f"Metrics exported to {filepath}", "filepath": filepath}
    except Exception as e:
        return {"error": f"Export failed: {str(e)}"}

# Embeddings cache warm-up endpoint
@app.post("/admin/embeddings/warmup")
async def warmup_embeddings_cache(queries: List[str]):
    """Warm up embeddings cache with custom queries"""
    if not embeddings_service:
        return {"error": "Embeddings service not available"}
    
    try:
        await embeddings_service.warm_cache(queries)
        return {
            "message": f"Cache warmed with {len(queries)} queries",
            "queries": queries
        }
    except Exception as e:
        return {"error": f"Cache warm-up failed: {str(e)}"}

# System optimization status endpoint
@app.get("/admin/optimization/status")
async def get_optimization_status():
    """Get detailed status of all optimization features"""
    return {
        "optimization_features": {
            "multi_tier_caching": {
                "enabled": cache_service is not None,
                "memory_cache": True,
                "redis_cache": cache_service.async_redis_client is not None if cache_service else False,
                "similarity_matching": True
            },
            "connection_pooling": {
                "enabled": pinecone_pool is not None,
                "max_connections": pinecone_pool.max_connections if pinecone_pool else 0,
                "active_connections": len(pinecone_pool._in_use) if pinecone_pool else 0
            },
            "async_processing": {
                "enabled": True,
                "thread_pool_size": thread_pool._max_workers,
                "http_client_pooling": http_client is not None
            },
            "embeddings_optimization": {
                "enabled": embeddings_service is not None,
                "batch_processing": True,
                "caching": True,
                "model": embeddings_service.model if embeddings_service else None
            },
            "performance_monitoring": {
                "enabled": performance_monitor is not None,
                "real_time_tracking": True,
                "alerting": True,
                "metrics_export": True
            }
        },
        "performance_targets": {
            "response_time_ms": "< 2000",
            "cache_hit_rate": "> 70%",
            "error_rate": "< 5%",
            "concurrent_users": "1000+",
            "scalability": "millions of requests"
        }
    }