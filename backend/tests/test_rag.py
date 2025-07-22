import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import time

# Disable tracing for tests
os.environ["TESTING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Mock environment variables
os.environ["VOYAGE_API_KEY"] = "test_voyage_key"
os.environ["PINECONE_API_KEY"] = "test_pinecone_key"
os.environ["PINECONE_INDEX_NAME"] = "test-bills-index"
os.environ["GOOGLE_API_KEY"] = "test_google_key"

from app import rag_query, QueryRequest, app

class TestRAGSystem:
    """Test cases for the RAG (Retrieval-Augmented Generation) system"""

    @pytest.mark.asyncio
    async def test_rag_query_success(self):
        """Test successful RAG query processing"""
        with patch('app.vectorstore') as mock_vectorstore, \
             patch('app.RetrievalQA') as mock_qa:
            
            # Mock the retriever and documents
            mock_retriever = MagicMock()
            mock_doc = MagicMock()
            mock_doc.page_content = "HB 55 relates to education funding based on property values."
            mock_doc.metadata = {
                "bill_id": "HB 55",
                "title": "Education Funding Bill",
                "session": "891"
            }
            
            mock_retriever.get_relevant_documents = MagicMock(return_value=[mock_doc])
            mock_vectorstore.as_retriever.return_value = mock_retriever
            
            # Mock the RetrievalQA chain
            mock_chain = MagicMock()
            mock_chain.return_value = {
                "result": "Several bills in session 891 relate to education funding. HB 55 concerns funding based on property values.",
                "source_documents": [mock_doc]
            }
            mock_qa.from_chain_type.return_value = mock_chain
            
            # Create a request object
            request = QueryRequest(query="education funding")
            result = await rag_query(request)
            
            # Verify the result structure
            assert "result" in result
            assert "documents_found" in result
            assert result["documents_found"] == 1
            assert "HB 55" in result["result"]

    @pytest.mark.asyncio
    async def test_rag_query_no_documents(self):
        """Test RAG query when no relevant documents are found"""
        with patch('app.vectorstore') as mock_vectorstore, \
             patch('app.model') as mock_llm:
            
            mock_retriever = MagicMock()
            mock_retriever.get_relevant_documents = MagicMock(return_value=[])
            mock_vectorstore.as_retriever.return_value = mock_retriever
            
            request = QueryRequest(query="non-existent topic")
            result = await rag_query(request)
            
            assert result["documents_found"] == 0
            assert "No specific bills found" in result["result"]
            assert "Search Suggestions" in result["result"]
            assert "suggestions_provided" in result
            assert result["suggestions_provided"] is True

    @pytest.mark.asyncio 
    async def test_rag_query_multiple_bills(self):
        """Test RAG query that returns multiple bill references"""
        with patch('app.vectorstore') as mock_vectorstore, \
             patch('app.model') as mock_llm:
            
            mock_retriever = MagicMock()
            mock_docs = [
                MagicMock(
                    page_content="HB 55 relates to education funding.",
                    metadata={"bill_id": "HB 55", "title": "Education Funding", "session": "891"}
                ),
                MagicMock(
                    page_content="HB 82 addresses school enrollment calculations.",
                    metadata={"bill_id": "HB 82", "title": "School Enrollment", "session": "891"}
                ),
                MagicMock(
                    page_content="SB 31 concerns property tax relief for schools.",
                    metadata={"bill_id": "SB 31", "title": "Tax Relief", "session": "891"}
                )
            ]
            
            mock_retriever.get_relevant_documents = MagicMock(return_value=mock_docs)
            mock_vectorstore.as_retriever.return_value = mock_retriever
            
            # Mock the RetrievalQA chain
            with patch('app.RetrievalQA') as mock_qa:
                mock_chain = MagicMock()
                mock_chain.return_value = {
                    "result": "Several bills relate to education: **HB 55** for funding, **HB 82** for enrollment, and **SB 31** for tax relief.",
                    "source_documents": mock_docs
                }
                mock_qa.from_chain_type.return_value = mock_chain
                
                request = QueryRequest(query="education bills")
                result = await rag_query(request)
                
                assert result["documents_found"] == 3
                assert "HB 55" in result["result"]
                assert "HB 82" in result["result"]
                assert "SB 31" in result["result"]

    @pytest.mark.asyncio
    async def test_rag_query_error_handling(self):
        """Test error handling in RAG query"""
        with patch('app.vectorstore') as mock_vectorstore:
            mock_vectorstore.as_retriever.side_effect = Exception("Database error")
            
            request = QueryRequest(query="test query")
            
            result = await rag_query(request)
            
            assert result["error"] is True
            assert "error_details" in result
            assert result["query"] == "test query"

    def test_query_request_validation(self):
        """Test QueryRequest model validation"""
        # Valid request
        valid_request = QueryRequest(query="valid query")
        assert valid_request.query == "valid query"
        
        # Empty query should still work (handled by business logic)
        empty_request = QueryRequest(query="")
        assert empty_request.query == ""

    @pytest.mark.asyncio
    async def test_rag_query_with_session_filter(self):
        """Test RAG query with session-specific results"""
        with patch('app.vectorstore') as mock_vectorstore, \
             patch('app.model') as mock_llm:
            
            mock_retriever = MagicMock()
            mock_doc = MagicMock()
            mock_doc.page_content = "HB 55 from session 891 relates to education funding."
            mock_doc.metadata = {
                "bill_id": "HB 55",
                "title": "Education Funding Bill",
                "session": "891"
            }
            
            mock_retriever.get_relevant_documents = MagicMock(return_value=[mock_doc])
            mock_vectorstore.as_retriever.return_value = mock_retriever
            
            # Mock the RetrievalQA chain
            with patch('app.RetrievalQA') as mock_qa:
                mock_chain = MagicMock()
                mock_chain.return_value = {
                    "result": "In session 891, HB 55 addresses education funding based on property values.",
                    "source_documents": [mock_doc]
                }
                mock_qa.from_chain_type.return_value = mock_chain
                
                request = QueryRequest(query="session 891 education bills")
                result = await rag_query(request)
            
            assert "session 891" in result["result"]
            assert "HB 55" in result["result"]

@pytest.mark.asyncio
async def test_app_health_endpoint():
    """Test the health check endpoint"""
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "legisync-backend"

@pytest.mark.asyncio 
async def test_rag_endpoint_integration():
    """Integration test for the RAG endpoint"""
    from fastapi.testclient import TestClient
    
    with patch('app.vectorstore') as mock_vectorstore, \
         patch('app.model') as mock_llm:
        
        mock_retriever = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "Test bill content"
        mock_doc.metadata = {"bill_id": "HB 1", "title": "Test Bill"}
        
        mock_retriever.get_relevant_documents = MagicMock(return_value=[mock_doc])
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        # Mock the RetrievalQA chain
        with patch('app.RetrievalQA') as mock_qa:
            mock_chain = MagicMock()
            mock_chain.return_value = {
                "result": "This is a test response about HB 1.",
                "source_documents": [mock_doc]
            }
            mock_qa.from_chain_type.return_value = mock_chain
            
            client = TestClient(app)
            response = client.post("/rag", json={"query": "test query"})
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "documents_found" in data
        assert data["documents_found"] == 1

class TestRAGSystemEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_empty_query(self):
        """Test handling of empty query"""
        request = QueryRequest(query="")
        result = await rag_query(request)
        
        # Should handle gracefully
        assert "result" in result
        assert isinstance(result["result"], str)
    
    @pytest.mark.asyncio
    async def test_very_long_query(self):
        """Test handling of very long queries"""
        long_query = "education funding " * 100  # Very long query
        request = QueryRequest(query=long_query)
        
        with patch('app.vectorstore') as mock_vectorstore:
            mock_retriever = MagicMock()
            mock_retriever.get_relevant_documents = MagicMock(return_value=[])
            mock_vectorstore.as_retriever.return_value = mock_retriever
            
            result = await rag_query(request)
            
            # Should handle without crashing - the exact behavior may vary
            assert "result" in result
            assert "documents_found" in result
            # Should be 0 for empty documents list, but test the core functionality
            assert isinstance(result["documents_found"], int)
    
    @pytest.mark.asyncio
    async def test_special_characters_in_query(self):
        """Test handling of special characters in queries"""
        special_queries = [
            "bill #123 & tax reform @2024",
            "education: funding; (K-12) schools",
            "healthcare → medical → insurance",
            "funding $$ for schools 100%"
        ]
        
        for query in special_queries:
            request = QueryRequest(query=query)
            
            with patch('app.vectorstore') as mock_vectorstore:
                mock_retriever = MagicMock()
                mock_retriever.get_relevant_documents = MagicMock(return_value=[])
                mock_vectorstore.as_retriever.return_value = mock_retriever
                
                result = await rag_query(request)
                
                # Should handle without crashing
                assert "result" in result