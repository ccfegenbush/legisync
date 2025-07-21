# backend/ingest.py
import pandas as pd
from voyageai import Client as VoyageClient
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

df = pd.read_csv("texas_bills_2025.csv")
texts = df["description"].tolist()
metadata = df[["bill_id", "session_id", "bill_number", "status", "status_desc", "status_date", "title"]].to_dict("records")

vo = VoyageClient(api_key=os.getenv("VOYAGE_API_KEY"))
embeddings = vo.embed(texts, model="voyage-3.5", input_type="document").embeddings

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("bills-index")
vectors = [{"id": str(i), "values": emb, "metadata": meta} for i, (emb, meta) in enumerate(zip(embeddings, metadata))]
index.upsert(vectors=vectors)

print("Data ingested successfully!")