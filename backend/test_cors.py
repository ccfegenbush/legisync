#!/usr/bin/env python3
import requests

def test_cors():
    url = "http://localhost:8000/rag"
    payload = {"query": "General Appropriations Bill"}
    
    # Test with CORS headers like a browser would send
    headers = {
        'Origin': 'http://localhost:3000',
        'Content-Type': 'application/json',
    }
    
    print("Testing CORS configuration...")
    print(f"URL: {url}")
    print(f"Origin: {headers['Origin']}")
    
    try:
        # Test preflight request (OPTIONS)
        print("\n1. Testing preflight request (OPTIONS)...")
        options_response = requests.options(url, headers=headers)
        print(f"Status Code: {options_response.status_code}")
        print(f"Access-Control-Allow-Origin: {options_response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
        print(f"Access-Control-Allow-Methods: {options_response.headers.get('Access-Control-Allow-Methods', 'NOT SET')}")
        
        # Test actual request (POST)
        print("\n2. Testing actual request (POST)...")
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
        
        if response.status_code == 200:
            print("✅ CORS is working correctly!")
            result = response.json()
            print(f"Response preview: {result['result'][:100]}...")
        else:
            print("❌ Request failed")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_cors()
