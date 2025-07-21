import pytest
from unittest.mock import patch
from app import rag_query

@pytest.mark.asyncio
async def test_rag_query():
    with patch('langchain.chains.RetrievalQA.from_chain_type') as mock_chain:
        mock_chain.return_value = {"result": "Mock summary"}
        result = await rag_query("Test query")
        assert "Mock summary" in result["result"]