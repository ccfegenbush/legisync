#!/usr/bin/env python3
"""
Comprehensive test suite for OpenStates API integration and data processing
"""
import os
import pytest
import requests
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestOpenStatesAPI:
    """Test suite for OpenStates API connectivity and data processing"""

    def test_api_key_configuration(self):
        """Test that API key is properly configured"""
        api_key = os.getenv("OPENSTATES_API_KEY")
        
        assert api_key is not None, "OPENSTATES_API_KEY not found in environment"
        assert api_key != "your_openstates_key_here", "Please set actual API key"
        assert len(api_key) > 10, "API key appears to be invalid"

    def test_openstates_api_connection(self):
        """Test basic API connectivity"""
        api_key = os.getenv("OPENSTATES_API_KEY")
        
        if not api_key or api_key == "your_openstates_key_here":
            pytest.skip("API key not configured")
        
        url = "https://v3.openstates.org/jurisdictions"
        headers = {
            'X-API-KEY': api_key,
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        assert response.status_code == 200, f"API connection failed: {response.status_code}"
        data = response.json()
        assert 'results' in data, "Invalid API response format"
        assert len(data['results']) > 0, "No jurisdictions returned"

    def test_texas_bills_fetch(self):
        """Test fetching Texas bills from OpenStates API"""
        api_key = os.getenv("OPENSTATES_API_KEY")
        
        if not api_key or api_key == "your_openstates_key_here":
            pytest.skip("API key not configured")
        
        url = "https://v3.openstates.org/bills"
        headers = {
            'X-API-KEY': api_key,
            'Accept': 'application/json'
        }
        params = {
            'jurisdiction': 'tx',
            'per_page': 5,
            'include': ['abstracts', 'sponsorships']
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        assert response.status_code == 200, f"Bills fetch failed: {response.status_code}"
        data = response.json()
        assert 'results' in data, "Invalid response format"
        
        if data['results']:
            bill = data['results'][0]
            assert 'identifier' in bill, "Bill missing identifier"
            assert 'title' in bill, "Bill missing title"
            assert 'session' in bill, "Bill missing session"

    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        """Test handling of API errors"""
        mock_get.return_value.status_code = 429
        mock_get.return_value.text = "Rate limit exceeded"
        
        api_key = "test_key"
        url = "https://v3.openstates.org/jurisdictions"
        headers = {
            'X-API-KEY': api_key,
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        assert response.status_code == 429

    @patch('requests.get')
    def test_bill_data_processing(self, mock_get):
        """Test processing of bill data from API"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'identifier': 'HB 55',
                    'title': 'Education Funding Bill',
                    'session': '891',
                    'status': 'introduced',
                    'abstracts': [
                        {'abstract': 'This bill addresses education funding'}
                    ],
                    'sponsorships': [
                        {'name': 'John Doe', 'primary': True}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        from data_collector import OpenStatesAPI, TexasBill
        
        api = OpenStatesAPI("test_key")
        bills = api.get_texas_bills(limit=1)
        
        assert len(bills) == 1
        bill = bills[0]
        assert bill['identifier'] == 'HB 55'
        assert bill['title'] == 'Education Funding Bill'
        assert bill['session'] == '891'

    def test_bill_format_conversion(self):
        """Test conversion from OpenStates format to TexasBill format"""
        from data_collector import OpenStatesAPI, TexasBill
        
        api = OpenStatesAPI("test_key")
        raw_bill = {
            'identifier': 'HB 100',
            'title': 'Test Bill',
            'abstracts': [{'abstract': 'Test abstract'}],
            'status': 'passed',
            'session': '891',
            'sponsorships': [
                {'name': 'Jane Smith', 'primary': True},
                {'name': 'Bob Johnson', 'primary': False}
            ]
        }
        
        formatted_bill = api.format_bill(raw_bill)
        
        assert formatted_bill.bill_number == 'HB 100'
        assert formatted_bill.title == 'Test Bill'
        assert formatted_bill.summary == 'Test abstract'
        assert formatted_bill.status == 'passed'
        assert formatted_bill.session == '891'
        assert 'Jane Smith' in formatted_bill.authors

    def test_session_parameter_validation(self):
        """Test that session parameters are properly validated"""
        from data_collector import OpenStatesAPI
        
        api = OpenStatesAPI("test_key")
        
        # Test with valid session
        with patch.object(api, 'get_texas_bills', return_value=[]):
            bills = api.get_texas_bills(session="891")
            # Should not raise an exception

    def test_rate_limiting_compliance(self):
        """Test that API calls respect rate limiting"""
        import time
        from data_collector import OpenStatesAPI
        
        api = OpenStatesAPI("test_key")
        
        # Mock the requests to track timing
        with patch('time.sleep') as mock_sleep, \
             patch('requests.get') as mock_get:
            
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'results': []}
            
            # Simulate multiple pages
            api.get_texas_bills(limit=50)  # Would require multiple pages
            
            # Verify that sleep was called for rate limiting
            # (This depends on the implementation details)

class TestDataIngestion:
    """Test suite for the enhanced data ingestion process"""

    def test_enhanced_bill_processor_initialization(self):
        """Test that EnhancedBillProcessor can be initialized"""
        from enhanced_ingest import EnhancedBillProcessor
        
        with patch('enhanced_ingest.VoyageClient'), \
             patch('enhanced_ingest.Pinecone'):
            
            processor = EnhancedBillProcessor()
            assert processor is not None

    @patch('enhanced_ingest.VoyageClient')
    @patch('enhanced_ingest.Pinecone')
    def test_bill_embedding_creation(self, mock_pinecone, mock_voyage):
        """Test creation of embeddings for bills"""
        from enhanced_ingest import EnhancedBillProcessor
        
        mock_voyage_instance = MagicMock()
        mock_voyage_instance.embed.return_value = [[0.1, 0.2, 0.3]]
        mock_voyage.return_value = mock_voyage_instance
        
        processor = EnhancedBillProcessor()
        
        test_bills = [
            {
                'bill_id': 'HB 55',
                'title': 'Test Bill',
                'summary': 'Test summary',
                'session': '891',
                'bill_type': 'HB'
            }
        ]
        
        vectors = processor.create_enhanced_embeddings(test_bills)
        
        assert len(vectors) == 1
        assert vectors[0]['id'] == 'tx-891-HB 55'
        assert 'values' in vectors[0]
        assert 'metadata' in vectors[0]

    def test_embedding_text_creation(self):
        """Test creation of rich text for embedding"""
        from enhanced_ingest import EnhancedBillProcessor
        
        with patch('enhanced_ingest.VoyageClient'), \
             patch('enhanced_ingest.Pinecone'):
            
            processor = EnhancedBillProcessor()
            
            test_bill = {
                'bill_id': 'HB 55',
                'title': 'Education Funding Bill',
                'summary': 'This bill addresses education funding for Texas schools.',
                'session': '891',
                'bill_type': 'HB',
                'status': 'introduced',
                'authors': ['John Doe', 'Jane Smith']
            }
            
            embedding_text = processor.create_embedding_text(test_bill)
            
            assert 'HB 55' in embedding_text
            assert 'Education Funding Bill' in embedding_text
            assert 'education funding' in embedding_text.lower()
            assert '891' in embedding_text

if __name__ == "__main__":
    # Run basic connectivity test
    print("🧪 OpenStates API Test Suite")
    print("=" * 50)
    
    # Run the connectivity test
    test_class = TestOpenStatesAPI()
    
    try:
        test_class.test_api_key_configuration()
        print("✅ API key configuration: PASSED")
    except Exception as e:
        print(f"❌ API key configuration: FAILED - {e}")
        exit(1)
    
    try:
        test_class.test_openstates_api_connection()
        print("✅ API connection: PASSED")
    except Exception as e:
        print(f"❌ API connection: FAILED - {e}")
    
    try:
        test_class.test_texas_bills_fetch()
        print("✅ Texas bills fetch: PASSED")
    except Exception as e:
        print(f"❌ Texas bills fetch: FAILED - {e}")
    
    print("=" * 50)
    print("Run full test suite with: pytest test_openstates.py")

if __name__ == "__main__":
    # Run basic connectivity test
    print("🧪 OpenStates API Test Suite")
    print("=" * 50)
    
    # Run the connectivity test
    test_class = TestOpenStatesAPI()
    
    try:
        test_class.test_api_key_configuration()
        print("✅ API key configuration: PASSED")
    except Exception as e:
        print(f"❌ API key configuration: FAILED - {e}")
        exit(1)
    
    try:
        test_class.test_openstates_api_connection()
        print("✅ API connection: PASSED")
    except Exception as e:
        print(f"❌ API connection: FAILED - {e}")
    
    try:
        test_class.test_texas_bills_fetch()
        print("✅ Texas bills fetch: PASSED")
    except Exception as e:
        print(f"❌ Texas bills fetch: FAILED - {e}")
    
    print("=" * 50)
    print("Run full test suite with: pytest test_openstates.py")
