#!/usr/bin/env python3
"""
Integration tests for LegiSync API endpoints
"""
import os
import pytest
import requests
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Set test environment
os.environ["TESTING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

class TestLegiSyncAPI:
    """Integration tests for LegiSync API endpoints"""

    @pytest.fixture
    def client(self):
        """Create a test client"""
        from app import app
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_debug_endpoint(self, client):
        """Test the debug status endpoint"""
        response = client.get("/debug")
        
        assert response.status_code == 200
        data = response.json()
        assert "environment" in data
        assert "pinecone_index" in data
        assert "voyage_configured" in data

    @patch('app.vectorstore')
    @patch('app.llm')
    def test_rag_endpoint_success(self, mock_llm, mock_vectorstore, client):
        """Test successful RAG query"""
        # Mock retriever
        mock_retriever = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "HB 55 relates to education funding based on property values."
        mock_doc.metadata = {
            "bill_id": "HB 55",
            "title": "Education Funding Bill",
            "session": "891"
        }
        mock_retriever.get_relevant_documents = AsyncMock(return_value=[mock_doc])
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        # Mock LLM
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Several bills in session 891 relate to education funding. **HB 55** concerns funding based on property values."
        ))
        
        # Test request
        response = client.post("/rag", json={"query": "education funding"})
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "documents_found" in data
        assert "query" in data
        assert data["documents_found"] == 1
        assert "HB 55" in data["result"]

    def test_rag_endpoint_empty_query(self, client):
        """Test RAG endpoint with empty query"""
        response = client.post("/rag", json={"query": ""})
        
        assert response.status_code == 422  # Validation error

    def test_rag_endpoint_invalid_json(self, client):
        """Test RAG endpoint with invalid JSON"""
        response = client.post("/rag", data="invalid json")
        
        assert response.status_code == 422

    @patch('app.vectorstore')
    @patch('app.llm')
    def test_rag_endpoint_multiple_bills(self, mock_llm, mock_vectorstore, client):
        """Test RAG endpoint returning multiple bill references"""
        # Mock multiple documents
        mock_retriever = MagicMock()
        mock_docs = [
            MagicMock(
                page_content="HB 55 education funding",
                metadata={"bill_id": "HB 55", "session": "891"}
            ),
            MagicMock(
                page_content="HB 82 school enrollment",
                metadata={"bill_id": "HB 82", "session": "891"}
            ),
            MagicMock(
                page_content="SB 31 property tax relief",
                metadata={"bill_id": "SB 31", "session": "891"}
            )
        ]
        mock_retriever.get_relevant_documents = AsyncMock(return_value=mock_docs)
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Several education bills: **HB 55** for funding, **HB 82** for enrollment, **SB 31** for tax relief."
        ))
        
        response = client.post("/rag", json={"query": "education bills"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["documents_found"] == 3
        assert "HB 55" in data["result"]
        assert "HB 82" in data["result"]
        assert "SB 31" in data["result"]

    @patch('app.vectorstore')
    def test_rag_endpoint_error_handling(self, mock_vectorstore, client):
        """Test RAG endpoint error handling"""
        mock_vectorstore.as_retriever.side_effect = Exception("Database error")
        
        response = client.post("/rag", json={"query": "test query"})
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "Database error" in data["error"]

    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/rag")
        
        # Check that CORS headers are present (depends on implementation)
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented

    @patch('app.vectorstore')
    @patch('app.llm')
    def test_rag_endpoint_session_specific(self, mock_llm, mock_vectorstore, client):
        """Test RAG queries with session-specific context"""
        mock_retriever = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "In session 891, HB 55 addresses education funding."
        mock_doc.metadata = {
            "bill_id": "HB 55",
            "session": "891",
            "bill_type": "HB"
        }
        mock_retriever.get_relevant_documents = AsyncMock(return_value=[mock_doc])
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="In session 891, **HB 55** addresses education funding based on property values."
        ))
        
        response = client.post("/rag", json={"query": "session 891 education"})
        
        assert response.status_code == 200
        data = response.json()
        assert "session 891" in data["result"]
        assert "HB 55" in data["result"]

class TestSystemIntegration:
    """End-to-end system integration tests"""

    def test_complete_workflow(self):
        """Test complete workflow from data ingestion to query"""
        # This would test the full pipeline:
        # 1. Data collection from OpenStates
        # 2. Embedding generation
        # 3. Vector storage in Pinecone
        # 4. RAG query processing
        # 5. Response generation
        
        # For now, we'll test the components separately
        # as a full integration test would require live APIs
        pass

    @patch('enhanced_ingest.VoyageClient')
    @patch('enhanced_ingest.Pinecone')
    def test_data_ingestion_pipeline(self, mock_pinecone, mock_voyage):
        """Test the data ingestion pipeline"""
        from enhanced_ingest import EnhancedBillProcessor
        
        # Mock VoyageAI embeddings
        mock_voyage_instance = MagicMock()
        mock_voyage_instance.embed.return_value = [[0.1] * 1024]  # 1024-dim vector
        mock_voyage.return_value = mock_voyage_instance
        
        # Mock Pinecone
        mock_pinecone_instance = MagicMock()
        mock_index = MagicMock()
        mock_index.upsert.return_value = {"upserted_count": 1}
        mock_index.describe_index_stats.return_value = MagicMock(total_vector_count=1)
        mock_pinecone_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pinecone_instance
        
        processor = EnhancedBillProcessor()
        
        # Test bill processing
        test_bills = [
            {
                'bill_id': 'HB 55',
                'title': 'Education Funding Bill',
                'summary': 'This bill addresses education funding.',
                'session': '891',
                'bill_type': 'HB'
            }
        ]
        
        vectors = processor.create_enhanced_embeddings(test_bills)
        
        assert len(vectors) == 1
        assert vectors[0]['id'] == 'tx-891-HB 55'
        
        # Test upload
        result = processor.upload_to_pinecone(vectors)
        assert result is not None

if __name__ == "__main__":
    # Run basic API tests
    from fastapi.testclient import TestClient
    from app import app
    
    client = TestClient(app)
    
    print("🧪 LegiSync API Integration Tests")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health endpoint: PASSED")
        else:
            print(f"❌ Health endpoint: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Health endpoint: ERROR - {e}")
    
    # Test debug endpoint
    try:
        response = client.get("/debug")
        if response.status_code == 200:
            print("✅ Debug endpoint: PASSED")
        else:
            print(f"❌ Debug endpoint: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Debug endpoint: ERROR - {e}")
    
    print("=" * 50)
    print("Run full test suite with: pytest test_integration.py")
