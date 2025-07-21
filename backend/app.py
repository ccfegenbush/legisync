# backend/app.py
from fastapi import FastAPI
from langchain_community.vectorstores import Pinecone as PineconeStore
from langchain.chains import RetrievalQA
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool
from voyageai import Client as VoyageClient
from pinecone import Pinecone
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPTraceExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from langsmith import traceable
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI  # New import

load_dotenv()

app = FastAPI()

# OpenTelemetry setup
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(OTLPTraceExporter(endpoint="http://localhost:4318/v1/traces")))
tracer = trace.get_tracer(__name__)

# Stack initialization
vo = VoyageClient(api_key=os.getenv("VOYAGE_API_KEY"))
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))  # Updated
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("bills-index")
vectorstore = PineconeStore(index, vo.embed, text_key="text")

def query_db(bill_id: str) -> dict:
    return {"bill_id": bill_id, "content": "Mock bill details from DB"}

tools = [Tool(name="DBQuery", func=query_db, description="Fetch bill details by ID")]

@app.post("/rag")
@traceable
async def rag_query(query: str):
    with tracer.start_as_current_span("rag-query"):
        chain = RetrievalQA.from_chain_type(model, retriever=vectorstore.as_retriever())
        return chain({"query": query})

@app.post("/agent")
@traceable
async def run_agent(query: str):
    with tracer.start_as_current_span("agent-query"):
        agent = create_react_agent(model, tools)
        return agent.invoke({"messages": [{"role": "user", "content": query}]})