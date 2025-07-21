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

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js default dev server
        "http://localhost:3001",  # Alternative Next.js port
        "http://127.0.0.1:3000",  # Alternative localhost format
        "http://127.0.0.1:3001",
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

vo = VoyageClient(api_key=os.getenv("VOYAGE_API_KEY"))
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))
index_name = "bills-index"

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
vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings, text_key="text")

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
        chain = RetrievalQA.from_chain_type(model, retriever=vectorstore.as_retriever())
        return chain({"query": request.query})

@app.post("/agent")
@traceable
async def run_agent(request: QueryRequest):
    with optional_span("agent-query"):
        agent = create_react_agent(model, tools)
        return agent.invoke({"messages": [{"role": "user", "content": request.query}]})