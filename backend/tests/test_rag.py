import os
import pytest
from unittest.mock import patch, MagicMock

# Disable tracing for tests
os.environ["TESTING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from app import rag_query, QueryRequest

@pytest.mark.asyncio
async def test_rag_query():
    with patch('app.vectorstore') as mock_vectorstore:
        # Mock the retriever and documents
        mock_retriever = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "Mock bill content"
        mock_retriever.get_relevant_documents.return_value = [mock_doc]
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        with patch('langchain.chains.RetrievalQA.from_chain_type') as mock_chain_constructor:
            # Create a mock chain instance that can be called
            mock_chain_instance = MagicMock()
            mock_chain_instance.return_value = {"result": "Mock summary", "source_documents": [mock_doc]}
            mock_chain_constructor.return_value = mock_chain_instance
            
            # Create a request object
            request = QueryRequest(query="Test query")
            result = await rag_query(request)
            
            # Verify the chain was called with the correct query
            mock_chain_instance.assert_called_once_with({"query": "Test query"})
            assert result["result"] == "Mock summary"
            assert result["documents_found"] == 1