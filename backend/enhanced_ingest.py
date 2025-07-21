"""
Enhanced Bill Ingestion Script
Processes bills from multiple sources and ingests into Pinecone
"""
import os
import pandas as pd
from typing import List, Dict
import logging
from voyageai import Client as VoyageClient
from pinecone import Pinecone
from datetime import datetime
import json
from dotenv import load_dotenv
from data_collector import OpenStatesAPI, TexasBill

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedBillProcessor:
    """
    Enhanced processor for bills with multiple data sources
    """
    
    def __init__(self):
        self.voyage_client = VoyageClient(api_key=os.getenv("VOYAGE_API_KEY"))
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "bills-index-dev")
        self.index = self.pc.Index(self.index_name)
    
    def process_openstates_data(self, limit: int = 1000) -> List[Dict]:
        """
        Collect and process data from OpenStates API
        """
        api_key = os.getenv("OPENSTATES_API_KEY")
        if not api_key:
            logger.error("OpenStates API key not found. Get one at https://openstates.org/accounts/profile/")
            return []
        
        collector = OpenStatesAPI(api_key)
        raw_bills = collector.get_texas_bills(limit=limit)
        
        processed_bills = []
        for raw_bill in raw_bills:
            try:
                bill = collector.format_bill(raw_bill)
                processed_bills.append({
                    "id": f"tx-{bill.session}-{bill.bill_number}",
                    "bill_number": bill.bill_number,
                    "title": bill.title,
                    "summary": bill.summary,
                    "text": f"{bill.title}\n\n{bill.summary}",  # Combine for embedding
                    "status": bill.status,
                    "introduced_date": bill.introduced_date,
                    "authors": bill.authors,
                    "subjects": bill.subjects,
                    "session": bill.session,
                    "bill_type": bill.bill_type,
                    "source": "openstates",
                    "last_updated": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error processing bill {raw_bill.get('identifier', 'unknown')}: {e}")
                continue
        
        return processed_bills
    
    def create_enhanced_embeddings(self, bills: List[Dict]) -> List[Dict]:
        """
        Create embeddings with enhanced metadata
        """
        vectors = []
        
        for i, bill in enumerate(bills):
            try:
                # Create rich text for embedding
                embedding_text = self.create_embedding_text(bill)
                
                # Generate embedding
                embedding = self.voyage_client.embed(
                    [embedding_text], 
                    model="voyage-3.5", 
                    input_type="document"
                ).embeddings[0]
                
                # Enhanced metadata
                metadata = {
                    "text": embedding_text,
                    "bill_number": bill["bill_number"],
                    "title": bill["title"],
                    "summary": bill["summary"][:500] + "..." if len(bill["summary"]) > 500 else bill["summary"],
                    "status": bill["status"],
                    "authors": ", ".join(bill["authors"][:3]),  # Limit for metadata size
                    "subjects": ", ".join(bill["subjects"][:5]),
                    "session": bill["session"],
                    "bill_type": bill["bill_type"],
                    "source": bill["source"],
                    "introduced_date": bill["introduced_date"],
                    "last_updated": bill["last_updated"]
                }
                
                vectors.append({
                    "id": bill["id"],
                    "values": embedding,
                    "metadata": metadata
                })
                
                if (i + 1) % 50 == 0:
                    logger.info(f"Processed {i + 1}/{len(bills)} bills")
                    
            except Exception as e:
                logger.error(f"Error creating embedding for {bill['id']}: {e}")
                continue
        
        return vectors
    
    def create_embedding_text(self, bill: Dict) -> str:
        """
        Create rich text combining multiple fields for better search
        """
        parts = []
        
        # Bill identification
        parts.append(f"Bill: {bill['bill_number']}")
        parts.append(f"Type: {bill['bill_type']}")
        parts.append(f"Session: {bill['session']}")
        
        # Content
        if bill['title']:
            parts.append(f"Title: {bill['title']}")
        
        if bill['summary']:
            parts.append(f"Summary: {bill['summary']}")
        
        # Context
        if bill['subjects']:
            parts.append(f"Subjects: {', '.join(bill['subjects'])}")
        
        if bill['authors']:
            parts.append(f"Authors: {', '.join(bill['authors'])}")
        
        if bill['status']:
            parts.append(f"Status: {bill['status']}")
        
        return "\n\n".join(parts)
    
    def upsert_to_pinecone(self, vectors: List[Dict], batch_size: int = 100):
        """
        Upload vectors to Pinecone in batches
        """
        logger.info(f"Upserting {len(vectors)} vectors to Pinecone index '{self.index_name}'")
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            try:
                self.index.upsert(vectors=batch)
                logger.info(f"Upserted batch {i//batch_size + 1}/{(len(vectors) + batch_size - 1)//batch_size}")
            except Exception as e:
                logger.error(f"Error upserting batch {i//batch_size + 1}: {e}")
        
        # Get index stats
        stats = self.index.describe_index_stats()
        logger.info(f"Index now contains {stats['total_vector_count']} vectors")
    
    def run_full_ingestion(self, limit: int = 1000):
        """
        Run the complete ingestion process
        """
        logger.info("Starting enhanced bill ingestion process...")
        
        # Step 1: Collect data
        logger.info("Collecting bills from OpenStates...")
        bills = self.process_openstates_data(limit=limit)
        
        if not bills:
            logger.error("No bills collected. Check API keys and network connection.")
            return
        
        logger.info(f"Collected {len(bills)} bills")
        
        # Step 2: Create embeddings
        logger.info("Creating embeddings...")
        vectors = self.create_enhanced_embeddings(bills)
        
        if not vectors:
            logger.error("No vectors created. Check embedding process.")
            return
        
        logger.info(f"Created {len(vectors)} embeddings")
        
        # Step 3: Upload to Pinecone
        logger.info("Uploading to Pinecone...")
        self.upsert_to_pinecone(vectors)
        
        logger.info("✅ Enhanced ingestion complete!")
        
        # Step 4: Save metadata for analysis
        self.save_ingestion_report(bills, len(vectors))
    
    def save_ingestion_report(self, bills: List[Dict], vector_count: int):
        """
        Save a report of what was ingested
        """
        report = {
            "ingestion_date": datetime.now().isoformat(),
            "total_bills_processed": len(bills),
            "total_vectors_created": vector_count,
            "bill_types": {},
            "subjects": {},
            "status_counts": {},
            "session_info": {}
        }
        
        # Analyze the data
        for bill in bills:
            # Bill types
            bill_type = bill.get("bill_type", "unknown")
            report["bill_types"][bill_type] = report["bill_types"].get(bill_type, 0) + 1
            
            # Subjects
            for subject in bill.get("subjects", []):
                report["subjects"][subject] = report["subjects"].get(subject, 0) + 1
            
            # Status
            status = bill.get("status", "unknown")
            report["status_counts"][status] = report["status_counts"].get(status, 0) + 1
            
            # Session
            session = bill.get("session", "unknown")
            report["session_info"][session] = report["session_info"].get(session, 0) + 1
        
        # Save report
        with open("ingestion_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info("📊 Ingestion report saved to ingestion_report.json")

def main():
    """
    Run enhanced ingestion
    """
    processor = EnhancedBillProcessor()
    
    # Start with 2000 bills to significantly expand the dataset
    processor.run_full_ingestion(limit=2000)

if __name__ == "__main__":
    main()
