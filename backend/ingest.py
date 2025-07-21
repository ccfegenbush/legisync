# backend/ingest.py
import pandas as pd
from voyageai import Client as VoyageClient
from pinecone import Pinecone
from dotenv import load_dotenv
import os
import time

load_dotenv()

print("Loading data from texas_bills_2025.csv...")
df = pd.read_csv("texas_bills_2025.csv")
print(f"Loaded {len(df)} bills from CSV")

# Handle missing values in text fields
df["title"] = df["title"].fillna("")
df["description"] = df["description"].fillna("")
df["committee"] = df["committee"].fillna("")
df["status_desc"] = df["status_desc"].fillna("")
df["last_action"] = df["last_action"].fillna("")
df["url"] = df["url"].fillna("")

# Combine title and description for richer text embeddings
texts = (df["title"] + " - " + df["description"]).tolist()

# Include essential metadata (optimized to reduce payload size)
metadata_columns = [
    "bill_id", "bill_number", "status_desc", "title", 
    "committee", "last_action", "url"
]
metadata = df[metadata_columns].to_dict("records")

# Clean metadata to remove any NaN values that could cause JSON errors
import math
for record in metadata:
    for key, value in record.items():
        if isinstance(value, float) and math.isnan(value):
            record[key] = ""
        elif value is None:
            record[key] = ""

print("Generating embeddings...")
vo = VoyageClient(api_key=os.getenv("VOYAGE_API_KEY"))

# Process embeddings in batches due to API limits
batch_size = 1000  # Voyage AI limit is 1000
all_embeddings = []

print(f"Processing {len(texts)} texts in batches of {batch_size}...")
for i in range(0, len(texts), batch_size):
    batch_texts = texts[i:i + batch_size]
    batch_num = i//batch_size + 1
    total_batches = (len(texts) + batch_size - 1)//batch_size
    
    print(f"Processing batch {batch_num}/{total_batches} ({len(batch_texts)} items)...")
    
    try:
        batch_embeddings = vo.embed(batch_texts, model="voyage-3.5", input_type="document").embeddings
        all_embeddings.extend(batch_embeddings)
        
        # Small delay to be API-friendly
        if batch_num < total_batches:
            time.sleep(1)
            
    except Exception as e:
        print(f"Error processing batch {batch_num}: {e}")
        raise

embeddings = all_embeddings
print(f"Generated {len(embeddings)} embeddings total")

print("Upserting vectors to Pinecone...")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("bills-index")

# Prepare all vectors
all_vectors = [
    {
        "id": str(meta["bill_id"]), 
        "values": emb, 
        "metadata": meta
    } 
    for emb, meta in zip(embeddings, metadata)
]

# Upsert in batches to avoid Pinecone limits
upsert_batch_size = 100  # Reduced due to metadata size - each vector has extensive metadata
total_upserted = 0

print(f"Upserting {len(all_vectors)} vectors in batches of {upsert_batch_size}...")
for i in range(0, len(all_vectors), upsert_batch_size):
    batch_vectors = all_vectors[i:i + upsert_batch_size]
    batch_num = i//upsert_batch_size + 1
    total_batches = (len(all_vectors) + upsert_batch_size - 1)//upsert_batch_size
    
    print(f"Upserting batch {batch_num}/{total_batches} ({len(batch_vectors)} vectors)...")
    
    try:
        index.upsert(vectors=batch_vectors)
        total_upserted += len(batch_vectors)
        
        # Small delay to be API-friendly
        if batch_num < total_batches:
            time.sleep(0.5)
            
    except Exception as e:
        print(f"Error upserting batch {batch_num}: {e}")
        raise

print("Data ingested successfully!")
print(f"Upserted {total_upserted} vectors to Pinecone index 'bills-index'")