import os
import pytest
from unittest.mock import patch, MagicMock

# Disable tracing for tests
os.environ["TESTING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from app import rag_query

@pytest.mark.asyncio
async def test_rag_query():
    with patch('langchain.chains.RetrievalQA.from_chain_type') as mock_chain_constructor:
        # Create a mock chain instance that can be called
        mock_chain_instance = MagicMock()
        mock_chain_instance.return_value = {"result": "Mock summary"}
        mock_chain_constructor.return_value = mock_chain_instance
        
        result = await rag_query("Test query")
        
        # Verify the chain was called with the correct query
        mock_chain_instance.assert_called_once_with({"query": "Test query"})
        assert result["result"] == "Mock summary"