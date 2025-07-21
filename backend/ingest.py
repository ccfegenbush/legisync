import pandas as pd
from voyageai import Client as VoyageClient
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

# Load sample data (download CSV from data.openstates.org/downloads and place in backend/)
df = pd.read_csv("texas_bills_2025.csv")  # Replace with your CSV path
texts = df["text"].tolist()
metadata = df[["bill_id", "state", "date"]].to_dict("records")

vo = VoyageClient(api_key=os.getenv("VOYAGE_API_KEY"))
embeddings = vo.embed(texts, model="voyage-3.5", input_type="document").embeddings

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("bills-index")
vectors = [{"id": str(i), "values": emb, "metadata": meta} for i, (emb, meta) in enumerate(zip(embeddings, metadata))]
index.upsert(vectors=vectors)

print("Data ingested successfully!")