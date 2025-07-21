#!/usr/bin/env python3
"""
Test script to verify OpenStates API connectivity
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openstates_api():
    """Test the OpenStates API with your key"""
    api_key = os.getenv("OPENSTATES_API_KEY")
    
    if not api_key:
        print("❌ OPENSTATES_API_KEY not found in .env file")
        print("Please add your API key to the .env file:")
        print("OPENSTATES_API_KEY=your_actual_key_here")
        return False
    
    if api_key == "your_openstates_key_here":
        print("❌ Please replace 'your_openstates_key_here' with your actual API key")
        return False
    
    print("🔑 API Key found, testing connection...")
    
    # Test API call
    url = "https://v3.openstates.org/jurisdictions"
    headers = {
        'X-API-KEY': api_key,
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ OpenStates API connection successful!")
            data = response.json()
            print(f"Found {len(data.get('results', []))} jurisdictions")
            return True
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_texas_bills():
    """Test fetching Texas bills"""
    api_key = os.getenv("OPENSTATES_API_KEY")
    
    url = "https://v3.openstates.org/bills"
    headers = {
        'X-API-KEY': api_key,
        'Accept': 'application/json'
    }
    params = {
        'jurisdiction': 'tx',
        'per_page': 5,  # Just get a few for testing
        'include': ['abstracts', 'sponsorships']  # ✅ Fixed valid parameters
    }
    
    print("\n🏛️  Testing Texas bills fetch...")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            bills = data.get('results', [])
            print(f"✅ Successfully fetched {len(bills)} Texas bills")
            
            if bills:
                # Show first bill as example
                bill = bills[0]
                print(f"\nExample bill:")
                print(f"  📋 ID: {bill.get('identifier', 'N/A')}")
                print(f"  📝 Title: {bill.get('title', 'N/A')[:100]}...")
                print(f"  🏛️  Session: {bill.get('session', 'N/A')}")
                print(f"  📊 Status: {bill.get('status', 'N/A')}")
                
                subjects = bill.get('subjects', [])
                if subjects:
                    print(f"  🏷️  Subjects: {', '.join(subjects[:3])}")
            
            return True
        else:
            print(f"❌ Error fetching bills: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 OpenStates API Test")
    print("=" * 40)
    
    if test_openstates_api():
        test_texas_bills()
    
    print("\n" + "=" * 40)
    print("If tests pass, you can run: python enhanced_ingest.py")
