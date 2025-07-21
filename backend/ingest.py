# backend/ingest.py
import pandas as pd
from voyageai import Client as VoyageClient
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

print("Loading data from texas_bills_2025.csv...")
df = pd.read_csv("texas_bills_2025.csv")
print(f"Loaded {len(df)} bills from CSV")

# Handle missing values in text fields
df["title"] = df["title"].fillna("")
df["description"] = df["description"].fillna("")
df["committee"] = df["committee"].fillna("")

# Combine title and description for richer text embeddings
texts = (df["title"] + " - " + df["description"]).tolist()

# Include more comprehensive metadata
metadata_columns = [
    "bill_id", "session_id", "bill_number", "status", "status_desc", 
    "status_date", "title", "description", "committee_id", "committee", 
    "last_action_date", "last_action", "url", "state_link"
]
metadata = df[metadata_columns].to_dict("records")

print("Generating embeddings...")
vo = VoyageClient(api_key=os.getenv("VOYAGE_API_KEY"))
embeddings = vo.embed(texts, model="voyage-3.5", input_type="document").embeddings
print(f"Generated {len(embeddings)} embeddings")

print("Upserting vectors to Pinecone...")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("bills-index")

# Use bill_id as vector ID for more meaningful identification
vectors = [
    {
        "id": str(meta["bill_id"]), 
        "values": emb, 
        "metadata": meta
    } 
    for emb, meta in zip(embeddings, metadata)
]
index.upsert(vectors=vectors)

print("Data ingested successfully!")
print(f"Upserted {len(vectors)} vectors to Pinecone index 'bills-index'")