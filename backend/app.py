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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Log environment variable status (without exposing the actual keys)
logger.info(f"PINECONE_API_KEY present: {bool(os.getenv('PINECONE_API_KEY'))}")
logger.info(f"VOYAGE_API_KEY present: {bool(os.getenv('VOYAGE_API_KEY'))}")
logger.info(f"GOOGLE_API_KEY present: {bool(os.getenv('GOOGLE_API_KEY'))}")
logger.info(f"Index name: {os.getenv('PINECONE_INDEX_NAME', 'bills-index-dev')}")

app = FastAPI()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "legisync-backend"}

# Debug endpoint to check system status
@app.get("/debug/status")
async def debug_status():
    return {
        "pinecone_api_key": bool(os.getenv("PINECONE_API_KEY")),
        "voyage_api_key": bool(os.getenv("VOYAGE_API_KEY")),
        "google_api_key": bool(os.getenv("GOOGLE_API_KEY")),
        "index_name": os.getenv("PINECONE_INDEX_NAME", "bills-index-dev"),
        "vectorstore_initialized": vectorstore is not None,
        "pinecone_client_initialized": pc is not None
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
    with optional_span("rag-query"):
        try:
            logger.info(f"Received query: {request.query}")
            
            # Check if vectorstore is available
            if vectorstore is None:
                logger.error("Vectorstore is not initialized")
                return {
                    "query": request.query,
                    "result": "The search service is currently unavailable. Please try again later.",
                    "error": True
                }
            
            # Test Pinecone connection
            retriever = vectorstore.as_retriever()
            logger.info("Pinecone retriever created successfully")
            
            # Test retrieval
            docs = retriever.get_relevant_documents(request.query)
            logger.info(f"Retrieved {len(docs)} documents from Pinecone")
            
            if not docs:
                logger.warning("No documents found for query")
                return {
                    "query": request.query,
                    "result": "No relevant bills found for your query. Please try a different search term.",
                    "documents_found": 0
                }
            
            # Log first few docs for debugging
            for i, doc in enumerate(docs[:2]):
                logger.info(f"Doc {i}: {doc.page_content[:100]}...")
            
            # Create and run the chain
            chain = RetrievalQA.from_chain_type(
                llm=model, 
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )
            result = chain({"query": request.query})
            
            logger.info("RAG query completed successfully")
            return {
                "query": request.query,
                "result": result.get("result", "No result generated"),
                "documents_found": len(docs),
                "source_documents": len(result.get("source_documents", []))
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}", exc_info=True)
            return {
                "query": request.query,
                "result": f"Sorry, I encountered an error while processing your request. Please try again.",
                "error": True,
                "error_details": str(e)
            }

@app.post("/agent")
@traceable
async def run_agent(request: QueryRequest):
    with optional_span("agent-query"):
        agent = create_react_agent(model, tools)
        return agent.invoke({"messages": [{"role": "user", "content": request.query}]})