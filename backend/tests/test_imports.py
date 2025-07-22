"""
Test to verify all imports work correctly in the testing environment
"""
import os
import pytest

# Set testing environment variables
os.environ["TESTING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["VOYAGE_API_KEY"] = "test_voyage_key"
os.environ["PINECONE_API_KEY"] = "test_pinecone_key"
os.environ["PINECONE_INDEX_NAME"] = "test-bills-index"
os.environ["GOOGLE_API_KEY"] = "test_google_key"

def test_app_import():
    """Test that app can be imported without errors"""
    try:
        from app import app
        assert app is not None, "App should be imported successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import app: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error importing app: {e}")

def test_rag_query_import():
    """Test that rag_query function can be imported"""
    try:
        from app import rag_query
        assert rag_query is not None, "rag_query should be imported successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import rag_query: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error importing rag_query: {e}")

def test_query_request_import():
    """Test that QueryRequest model can be imported"""
    try:
        from app import QueryRequest
        assert QueryRequest is not None, "QueryRequest should be imported successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import QueryRequest: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error importing QueryRequest: {e}")

def test_performance_services_conditional():
    """Test that performance services are handled correctly"""
    try:
        from app import PERFORMANCE_SERVICES_AVAILABLE
        # This should be either True or False, but not cause an error
        assert isinstance(PERFORMANCE_SERVICES_AVAILABLE, bool)
    except ImportError as e:
        pytest.fail(f"Failed to import PERFORMANCE_SERVICES_AVAILABLE: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error checking performance services: {e}")
